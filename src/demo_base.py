#!/usr/bin/env python
"""Base class for PID demo problems

Copyright (c) 2016 Benjamin J. Andre

This Source Code Form is subject to the terms of the Mozilla Public
License, v.  2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

#
# built-in modules
#
import abc
import configparser
import os
import sys
import traceback

#
# installed dependencies
#
import numpy as np
import matplotlib.pyplot as plt

#
# other modules in this package
#
from pid import PID

if sys.hexversion < 0x03050000:
    print(70 * "*")
    print("ERROR: {0} requires python >= 3.5.x. ".format(sys.argv[0]))
    print("It appears that you are running python {0}".format(
        ".".join(str(x) for x in sys.version_info[0:3])))
    print(70 * "*")
    sys.exit(1)


def read_config_file(filename):
    """Read the configuration file and process

    """
    print("Reading configuration file : {0}".format(filename))

    cfg_file = os.path.abspath(filename)
    if not os.path.isfile(cfg_file):
        raise RuntimeError("Could not find config file: {0}".format(cfg_file))

    config = config_parser()
    config.read(cfg_file)

    return config


# -------------------------------------------------------------------------------
#
# FIXME: work functions
#
# -------------------------------------------------------------------------------
class PIDDemoBase(object):
    """
    """

    def __init__(self):
        """
        """

        self._units = None

        # simulation time
        self._delta_time = None  # [s]
        self._max_time = None  # [s]
        self._time = None  # [s]

        # controller time
        self._control_delta = None  # [s]
        self._control_interval = None  # [steps]

        # forcing
        self._forcing_mean = None
        self._forcing_standard_deviation = None
        self._forcing = None

        # state
        self._control = None
        self._state_control = None
        self._state_no_control = None

        # controller
        self._set_point = None
        self._control_bias = None
        self._pid = None

    def __str__(self):
        """
        """
        message = ''
        message += "control_delta = {0} s".format(self._control_delta)
        return message

    def _initialize_units(self, units):
        """Assign user supplied units to various variables.
        """
        default = '?'
        if not units:
            units = []

        needed_units = ['time', 'process', 'control', 'forcing']
        for var in needed_units:
            if var not in units:
                units[var] = default
        self._units = units

    def _initialize_simulation_time(self, delta_time, max_time):
        """Initialize the time stepping for the process simeanlation
        """
        self._delta_time = delta_time
        self._max_time = max_time
        self._time = np.arange(0.0, self._max_time, self._delta_time)

    def _initialize_controller_time(self, control_delta):
        """Initialize the timing of the controller, e.g. how often process
        samples are taken and send to the controller for computation
        of the control variable.

        """
        self._control_delta = control_delta
        self._control_interval = int(self._control_delta / self._delta_time)
        print("Control delta = {0} [s]".format(self._control_delta))
        print("Control interval = {0} [time steps]".format(
            self._control_interval))

    def _initialize_constant_forcing(self, forcing_mean):
        """Use a constant forcing.
        """
        self._forcing_mean = forcing_mean
        self._forcing = self._forcing_mean * np.ones(len(self._time))

    def _initialize_normal_forcing(self,
                                   forcing_mean, forcing_standard_deviation):
        """Use a random forcing from a normal distribution with the specified
        meand and standard deviation.

        """
        self._forcing_mean = forcing_mean
        self._forcing_standard_deviation = forcing_standard_deviation
        np.random.seed(770405)
        self._forcing = np.random.normal(
            self._forcing_mean, self._forcing_standard_deviation,
            len(self._time))

    def _initialize_pid(self, history_length, set_point,
                        Kp, Ki, Kd, control_bias):
        """
        """
        print("Initializing PID controller:")
        print("  history length = {0}".format(history_length))
        print("  set_point = {0}".format(set_point))
        print("  Kp = {0}".format(Kp))
        print("  Ki = {0}".format(Ki))
        print("  Kd = {0}".format(Kd))
        self._pid = PID(history_length, set_point, Kp, Ki, Kd)
        self._control_bias = control_bias

    def simulate_no_control(self):
        """
        """
        self._state_no_control = np.zeros(len(self._time))
        self._state_no_control[0] = self._initial_condition
        for t in range(1, len(self._time)):
            previous_state = self._state_no_control[t-1]
            self._state_no_control[t] = self.process(
                self._forcing[t], self._delta_time, previous_state,
                self._control_bias)

    def simulate_with_control(self):
        """
        """
        self._state_control = np.zeros(len(self._time))
        self._control = np.zeros(len(self._time))
        self._state_control[0] = self._initial_condition
        self._control[0] = self._control_bias
        control = self._control[0]
        for t in range(1, len(self._time)):
            previous_state = self._state_control[t-1]
            process_value = self.process(self._forcing[t], self._delta_time,
                                         previous_state, control)
            self._state_control[t] = process_value
            if t % self._control_interval == 0:
                control_delta = self._pid.control(process_value,
                                                  self._delta_time)
                control = self._control_bias - control_delta
            # NOTE(bja, 2016-11) for plotting. Want control at all
            # time points, not just when it is being changed!
            self._control[t] = control

    def plot(self):
        """
        """
        nrows = 3
        ncols = 1
        plt.figure(1)
        plt.subplot(nrows, ncols, 1)
        plt.plot(self._time, self._state_control, label='controled')
        plt.plot(self._time, self._state_no_control, label='no control')
        set_point = self._set_point * np.ones(len(self._time))
        plt.plot(self._time, set_point, label='set point')
        plt.legend(loc='best', ncol=2)
        plt.ylabel("Process variable [{0}]".format(self._units['process']))

        plt.subplot(nrows, ncols, 2)
        plt.plot(self._time, self._control, label='control variable')
        control_bias = self._control_bias * np.ones(len(self._time))
        plt.plot(self._time, control_bias, label='control_bias')
        plt.legend(loc='best', ncol=2)
        plt.ylabel("control variable [{0}]".format(self._units['control']))

        plt.subplot(nrows, ncols, 3)
        plt.plot(self._time, self._forcing, label='forcing')
        forcing_mean = self._forcing_mean * np.ones(len(self._time))
        plt.plot(self._time, forcing_mean, label='forcing mean')

        plt.legend(loc='best', ncol=2)
        plt.ylabel("Forcing [{0}]".format(self._units['forcing']))
        plt.xlabel("time [{0}]".format(self._units['time']))
        plt.show()

    def summary(self):
        """summar of the final system state
        """
        print("System summary:")
        print("  Without control:")
        value = self._state_no_control[-1]
        print("    Final process value = {0:1.6e} [{1}]".format(
            value, self._units['process']))
        print("    pv - sp = {0:1.6e} [{1}]".format(
            value - self._set_point, self._units['process']))

        print("  With control:")
        value = self._state_no_control[-1]
        print("    Final process value = {0:1.6e} [{1}]".format(
            value, self._units['process']))
        print("    pv - sp = {0:1.6e} [{1}]".format(
            value - self._set_point, self._units['process']))
        value = self._control[-1]
        print("    Final control value = {0:1.6e} [{1}]".format(
            value, self._units['control']))
        print("    control - bias = {0:1.6e} [{1}]".format(
            value - self._control_bias, self._units['control']))

    def run(self):
        """
        """
        self.simulate_no_control()
        self.simulate_with_control()
        self.summary()
        self.plot()

    @abc.abstractmethod
    def process(self, forcing, delta_time, previous_state, control_bias):
        """
        """
        return None

    @abc.abstractmethod
    def _calculate_control_bias(self, steady_state_forcing, set_point):
        """
        """
        return None

    @abc.abstractmethod
    def _calculate_set_point(self):
        """
        """
        return None

    @abc.abstractmethod
    def _calculate_dCVdPV(self):
        """Calculate the steady state dCV/dPV as an approximation for Kp.
        """
        return None

    @abc.abstractmethod
    def _calculate_time_scales(self, q_in, h_sp, a_out, h):
        """Estimate the time scales of the problem:
        """
        return None


if __name__ == "__main__":
    try:
        print("Module has no main functionality. Please run pid-driver.py")
        sys.exit(0)
    except Exception as error:
        print(str(error))
        traceback.print_exc()
        sys.exit(1)
