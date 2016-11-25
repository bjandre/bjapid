#!/usr/bin/env python3
"""ctypes wrapper for pid controller.

Copyright (c) 2016 Benjamin J. Andre

This Source Code Form is subject to the terms of the Mozilla Public
License, v.  2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""


#
# built-in modules
#
import ctypes
import sys
import traceback

#
# other modules in this package
#
bjautil = ctypes.cdll.LoadLibrary('libbjautil.A.dylib')

if sys.hexversion < 0x03050000:
    print(70 * "*")
    print("ERROR: {0} requires python >= 3.5.x. ".format(sys.argv[0]))
    print("It appears that you are running python {0}".format(
        ".".join(str(x) for x in sys.version_info[0:3])))
    print(70 * "*")
    sys.exit(1)


class PID(object):
    """ctypes wrapper for pid controller
    """

    def __init__(self, history_length=5, setpoint=0.0, Kp=1.0, Ki=0.0, Kd=0.0):
        """Create and initialize a PID controller.

        Create and initialize a PID controller. If no gains are
        specified, defaults to a P, pure proportional, controller.

        Keyword arguments:

        history_length -- length of history buffer to save for
        integral term. [int]

        setpoint -- setpoint for the process. [float]

        Kp, Ki, Kd -- gains for proportional, integral and derivative
        terms. [float]

        """
        self._pid_prototypes()

        history_length_c = ctypes.c_uint8(history_length)
        setpoint_c = ctypes.c_float(setpoint)
        Kp_c = ctypes.c_float(Kp)
        Ki_c = ctypes.c_float(Ki)
        Kd_c = ctypes.c_float(Kd)

        pid = bjautil.pid_init(history_length_c, setpoint_c,
                               Kp_c, Ki_c, Kd_c)

        self._pid = ctypes.c_void_p(pid)
        print("&pid = {0}".format(self._pid))

    def _pid_prototypes(self):
        """set all the wrapper function prototypes
        """
        bjautil.pid_init.restype = ctypes.c_void_p
        bjautil.pid_init.argtypes = [
            ctypes.c_uint8, ctypes.c_float,
            ctypes.c_float, ctypes.c_float, ctypes.c_float, ]

        bjautil.pid_control.restype = ctypes.c_float
        bjautil.pid_control.argstypes = [
            ctypes.c_void_p, ctypes.c_float, ctypes.c_float, ]

    def control(self, process_value, delta_time):
        """Compute the control output.

        Compute the control output for a given process value and time
        interval.

        Positional arguments:
        process_value -- current process value. [float]
        delta_time -- time interval since last control calculation. [float]

        Returns:
        control output -- controller output. [float]

        """
        process_value_c = ctypes.c_float(process_value)
        delta_time_c = ctypes.c_float(delta_time)

        control = bjautil.pid_control(self._pid, process_value_c, delta_time_c)

        return control


if __name__ == "__main__":
    try:
        message = "pid.py does not contain any independent functionality."
        print(message)
        sys.exit(0)
    except Exception as error:
        print(str(error))
        traceback.print_exc()
        sys.exit(1)
