#!/usr/bin/env python3
"""driver for testing pid controller.

Copyright (c) 2016 Benjamin J. Andre

This Source Code Form is subject to the terms of the Mozilla Public
License, v.  2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""


#
# built-in modules
#
import argparse
import configparser
import os
import sys
import traceback

#
# installed dependencies
#

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

    pid = PID(history_length, setpoint, Kp, Ki, Kd)

    process_value = 90.0
    delta_time = 1.0
    control = pid.control(process_value, delta_time)
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
