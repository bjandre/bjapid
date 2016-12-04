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
import math
import os
import sys
import traceback

#
# installed dependencies
#


#
# other modules in this package
#
from demo_tank import DrainingTankDemo


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

    parser.add_argument('--config', nargs=1, required=True,
                        help='path to config file')

    parser.add_argument('--write-template', action='store_true',
                        help='write a template configuration file')

    options = parser.parse_args()
    return options


def read_config_file(filename):
    """Read the configuration file and process

    """
    print("Reading configuration file : {0}".format(filename))

    cfg_file = os.path.abspath(filename)
    if not os.path.isfile(cfg_file):
        raise RuntimeError("Could not find config file: {0}".format(cfg_file))

    config = configparser.ConfigParser()
    config.read(cfg_file)
    check_config_file(config)
    return config


def write_template_config_file():
    """
    """
    template = configparser.ConfigParser()

    section = 'process'
    template.add_section(section)
    template.set(section, 'type', 'string')
    template.set(section, 'initial_condition', 'float')
    template.set(section, 'set_point', 'float')

    section = 'forcing'
    template.add_section(section)
    template.set(section, 'type', 'string: constant, normal')
    template.set(section, 'mean', 'float')
    template.set(section, 'standard_deviation', 'float')

    section = 'time'
    template.add_section(section)
    template.set(section, 'delta', 'float')
    template.set(section, 'max', 'float')

    section = 'control'
    template.add_section(section)
    template.set(section, 'delta', 'float')
    template.set(section, 'history_length', 'int > 0')
    template.set(section, 'control_bias', 'float or "calculate"')
    template.set(section, 'Kp', 'float or "calculate"')
    template.set(section, 'Ki', 'float')
    template.set(section, 'Kd', 'float')

    with open('template.cfg', 'wb') as configfile:
        template.write(configfile)


def check_config_file(config):
    """Check the configuration file for required sections and options.
    """
    section = 'process'
    options = ['type', 'initial_condition', 'set_point', ]
    check_config_required_options(config, section, options)

    # NOTE(bja, 2016-11) standard_deviation isn't always required, so
    # we can't check it here. Adding a sinusoidal would add amplitude,
    # phase and frequency...
    section = 'forcing'
    options = ['type', 'mean', ]
    check_config_required_options(config, section, options)

    section = 'time'
    options = ['delta', 'max', ]
    check_config_required_options(config, section, options)

    # NOTE(bja, 2016-11) right now, we either assign a float or
    # 'calculate' to control_bias and Kp. More robust with a fallback
    # of None and then try to compute...?
    section = 'control'
    options = ['delta', 'history_length', 'control_bias', 'Kp', 'Ki', 'Kd', ]
    check_config_required_options(config, section, options)


def check_config_required_options(config, section, options):
    """
    """
    for opt in options:
        if not config.has_option(section, opt):
            message = ("ERROR: Input file must have section '{0}' with"
                       "option '{1}'".format(section, opt))
            raise RuntimeError(message)


# -------------------------------------------------------------------------------
#
# work functions
#
# -------------------------------------------------------------------------------
def test_pid_wrapper():
    """
    """
    from pid import PID
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

# -------------------------------------------------------------------------------
#
# main
#
# -------------------------------------------------------------------------------
def main(options):
    if options.config:
        config = read_config_file(options.config[0])

    process_type = config["process"]["type"]
    if process_type == "tank":
        process = DrainingTankDemo(config)
    else:
        raise RuntimeError("Unknown ")

    process.run()

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
