#!/usr/bin/env python3
"""driver for testing pid controller.

Author: Ben Andre <bjandre@gmail.com>

"""


#
# built-in modules
#
import argparse
import configparser
import ctypes
import os
import sys
import traceback

if sys.hexversion < 0x02070000:
    print(70 * "*")
    print("ERROR: {0} requires python >= 2.7.x. ".format(sys.argv[0]))
    print("It appears that you are running python {0}".format(
        ".".join(str(x) for x in sys.version_info[0:3])))
    print(70 * "*")
    sys.exit(1)

#
# installed dependencies
#

#
# other modules in this package
#
bjautil = ctypes.cdll.LoadLibrary('libbjautil.A.dylib')


# -------------------------------------------------------------------------------
#
# User input
#
# -------------------------------------------------------------------------------
def commandline_options():
    """Process the command line arguments.

    """
    parser = argparse.ArgumentParser(
        description='FIXME: python program template.')

    parser.add_argument('--backtrace', action='store_true',
                        help='show exception backtraces as extra debugging '
                        'output')

    parser.add_argument('--debug', action='store_true',
                        help='extra debugging output')

    parser.add_argument('--config', nargs=1, required=False,
                        help='path to config file')

    options = parser.parse_args()
    return options


def read_config_file(filename):
    """Read the configuration file and process

    """
    print("Reading configuration file : {0}".format(filename))

    cfg_file = os.path.abspath(filename)
    if not os.path.isfile(cfg_file):
        raise RuntimeError("Could not find config file: {0}".format(cfg_file))

    config = configparser()
    config.read(cfg_file)

    return config


# -------------------------------------------------------------------------------
#
# work functions
#
# -------------------------------------------------------------------------------
def pid_init(history_length, setpoint, Kp, Ki, Kd):
    """
    """
    history_length_c = ctypes.c_uint8(history_length)
    setpoint_c = ctypes.c_float(setpoint)
    Kp_c = ctypes.c_float(Kp)
    Ki_c = ctypes.c_float(Ki)
    Kd_c = ctypes.c_float(Kd)

    bjautil.pid_init.restype = ctypes.c_void_p
    bjautil.pid_init.argtypes = [
        ctypes.c_uint8, ctypes.c_float,
        ctypes.c_float, ctypes.c_float, ctypes.c_float, ]

    pid = ctypes.c_void_p(bjautil.pid_init(history_length_c, setpoint_c,
                                           Kp_c, Ki_c, Kd_c))

    return pid


def pid_control(pid, process_value, delta_time):
    """
    """
    process_value_c = ctypes.c_float(90.0)
    delta_time_c = ctypes.c_float(1.0)

    bjautil.pid_control.restype = ctypes.c_float
    bjautil.pid_control.argstypes = [
        ctypes.c_void_p, ctypes.c_float, ctypes.c_float, ]

    control = bjautil.pid_control(pid, process_value_c, delta_time_c)

    return control


# -------------------------------------------------------------------------------
#
# main
#
# -------------------------------------------------------------------------------
def main(options):
    if options.config:
        config = read_config_file(options.config[0])

    history_length = 5
    setpoint = 100.0
    Kp = 1.5
    Ki = 0.0
    Kd = 0.0

    pid = pid_init(history_length, setpoint, Kp, Ki, Kd)

    print("&pid = {0}".format(pid))

    process_value = 90.0
    delta_time = 1.0
    control = pid_control(pid, process_value, delta_time)
    print("control = {0}".format(control))

    return 0


if __name__ == "__main__":
    options = commandline_options()
    try:
        status = main(options)
        sys.exit(status)
    except Exception as error:
        print(str(error))
        if options.backtrace:
            traceback.print_exc()
        sys.exit(1)
