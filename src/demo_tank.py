#!/usr/bin/env python
"""Draining tank demo / test problem for pid controller

Contol the outflow of a tank to maintain a constant height of fluid in
the tank.

process variable - height of fluid
control variable - area of outflow valve

The transient conservation of mass equation can be solved for the
height of fluid in a tank or reservoir:

A_r * dh/dt = Q_in - Q_out

where:

- A_r = area of the tank [m^2]
- h = height of fluid in the tank above the drain [m]
- t = time [s]
- Q = volumetric flow rate [m^3/s]

Assuming:

- Q_in forcing as a function of time
  Q = v * A
- v_out = outflow velocity, is a function of height: v = sqrt(2*g*h)
- g = gravitational acceleration [m/s^2]

dh/dt = (Q_in - A_out * v_out) = A_r

dh/dt = Q_in / A_r - sqrt(2*g*h) * A_out / A_r

c1 = sqrt(2*g) / A_r

dh/dt = Q_in(t) / A_r - c_1 * A_out(t) * sqrt(h)

Euler forward approximation for derivative:

(h_tp1 - h_t) / dt = Q_in(t) / A_r - c1 * A_out(t) * sqrt(h_t)

h_tp1 = h_t + Q_in(t) * dt / a_r - c1 * dt * A_out(t) * sqrt(h_t)


At steady state with a constant Q_in and A_out is:

0 = Q_in / A_r - sqrt(2*g*h) * A_out / A_r

Q_in = sqrt(2*g*h) * A_out

Since the process variable is height:

A_out = Q_in / sqrt(2*g*h)

For a given setpoint h, the outlet area:



Copyright (c) 2016 Benjamin J. Andre

This Source Code Form is subject to the terms of the Mozilla Public
License, v.  2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

#
# built-in modules
#
import math
import sys
import traceback

#
# installed dependencies
#

#
# other modules in this package
#
import demo_base


if sys.hexversion < 0x03050000:
    print(70 * "*")
    print("ERROR: {0} requires python >= 3.5.x. ".format(sys.argv[0]))
    print("It appears that you are running python {0}".format(
        ".".join(str(x) for x in sys.version_info[0:3])))
    print(70 * "*")
    sys.exit(1)


# -------------------------------------------------------------------------------
#
# FIXME: work functions
#
# -------------------------------------------------------------------------------
class DrainingTankDemo(demo_base.PIDDemoBase):
    """
    c1 = sqrt(2*g) / A_r

    h_tp1 = h_t + Q_in(t) * dt / A_r - c1 * dt * A_out(t) * sqrt(h_t)
    """

    def __init__(self, config):
        """
        """
        super().__init__()

        units = {'process': 'm',
                 'control': 'm^2',
                 'forcing': 'm^3/s',
                 'time': 's', }
        self._initialize_units(units)

        # problem specific data that may be used in later
        # calculations, e.g. dCV/dPV
        self._A_r = 5.0  # [m]
        self._g = 9.81  # [m^2/s]
        self._c1 = math.sqrt(2.0 * self._g) / self._A_r

        # initialize simulation related variables
        self._initial_condition = config.getfloat("process",
                                                  "initial_condition")
        self._set_point = config.getfloat("process", "set_point")
        print("Process set point: head = {0:1.6e} [{1}]".format(
            self._set_point, self._units['process']))

        self._initialize_simulation_time(
            config.getfloat("time", "delta"), config.getfloat("time", "max"))

        # initialize forcing
        forcing_type = config["forcing"]["type"]
        if forcing_type == "constant":
            self._initialize_constant_forcing(config.getfloat("forcing",
                                                              "mean"))
        elif forcing_type == "normal":
            self._initialize_normal_forcing(
                config.getfloat("forcing", "mean"),
                config.getfloat("forcing", "standard_deviation"))
        else:
            message = "Unknown forcing type '{0}'.".format(forcing_type)
            raise RuntimeError(message)

        # initialize controller
        self._initialize_controller_time(config.getfloat("control", "delta"))

        if config["control"]["control_bias"] == "calculate":
            bias = self._calculate_control_bias(self._forcing_mean,
                                                self._set_point)
        else:
            bias = config["control"]["control_bias"]
        self._control_bias = float(bias)

        Kp = config["control"]["Kp"]
        if Kp == "calculate":
            Kp = self._calculate_dCVdPV(self._forcing_mean, self._set_point)
            # NOTE(bja, 2016-11) by definition, gain's must be positive!
            Kp = abs(Kp)
        else:
            Kp = float(Kp)

        self._initialize_pid(int(config["control"]["history_length"]),
                             self._set_point, Kp,
                             config.getfloat("control", "Ki"),
                             config.getfloat("control", "Kd"),
                             self._control_bias)

    def process(self, forcing, delta_time, previous_state, control_bias):
        """
        """
        h_t = previous_state
        q_in = forcing
        a_out = control_bias
        dt = delta_time

        h_tp1 = h_t
        h_tp1 += q_in * dt / self._A_r  # height added by inflow
        h_tp1 -= self._c1 * dt * a_out * math.sqrt(h_t)  # decreased by outflow

        # non-negativity, can't have a gravity drained tank with
        # height below the drain!
        if h_tp1 < 0.0:
            h_tp1 = 0.0
        return h_tp1

    def _calculate_control_bias(self, steady_state_forcing, set_point):
        """
        A_out = Q_in / sqrt(2*g*h)
        """
        q_in = steady_state_forcing
        h_sp = set_point
        a_ss = q_in / math.sqrt(2.0 * self._g * h_sp)
        print("Steady state control bias: tank outlet area = {0:1.6e} [{1}]".format(
            a_ss, self._units['control']))
        return a_ss

    def _calculate_set_point(self, steady_state_forcing, control_bias):
        """
        h = (Q_in / A_out)**2.0 / (2*g)
        """
        q_in = steady_state_forcing
        area = control_bias
        h_sp = (q_in / area)**2 / (2.0 * self._g)
        print("Steady state set point: height = {0:1.6e} [m]".format(h_sp))
        return h_sp

    def _calculate_dCVdPV(self, steady_state_forcing, set_point):
        """Calculate the steady state dA/dh as an approximation for Kp.
        At steady state:
        (q_in/A_out)**2 = 2*g*h
        dA/dh = (-q_in/2) * sqrt(1/2*g*h**3)
        """
        q_in = steady_state_forcing
        h_sp = set_point
        dAdh = (-q_in / 2.0) * math.sqrt(1.0 / (2 * self._g * h_sp**3))
        print("Steady state dCV/dPV at set setpoint: "
              "dAdh = {0:1.6e} [{1}/{2}]".format(
                  dAdh, self._units['control'], self._units['process']))
        return dAdh

    def _calculate_time_scales(self, q_in, h_sp, a_out, h):
        """Estimate the time scales of the problem:
        Time to fill = A_r * (h_sp-h) / q_in
        Time to drain = (A_r / a_out) * (2*g*h/h_sp^2)^-0.5
        Net time scale = (Q_in - Q_out) / (A_r * h)
        """
        T_fill = self._A_r * (h_sp - h) / q_in
        T_drain = ((self._A_r / a_out) *
                   math.sqrt((h_sp**2) / (2.0 * self._g * h)))
        T_net = ((q_in - a_out * math.sqrt(2.0 * self._g * h)) /
                 (self._A_r * (h_sp - h)))
        print("T_f = {T_f}   T_d = {T_d}   T_n = {T_n}".format(
            T_f=T_fill, T_d=T_drain, T_n=T_net))


# -------------------------------------------------------------------------------
#
# main
#
# -------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        print("Module has no main functionality. Please run pid-driver.py")
        sys.exit(0)
    except Exception as error:
        print(str(error))
        traceback.print_exc()
        sys.exit(1)
