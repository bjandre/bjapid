#!/usr/bin/env python3
"""Manage updating and maintaining 3rd party libraries

// Copyright (c) 2016 Benjamin J. Andre
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v.  2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

#
# built-in modules
#
import argparse
import configparser
import os
import os.path
import subprocess
import sys
import traceback


#
# installed dependencies
#

#
# other modules in this package
#

if sys.hexversion < 0x03050000:
    print(70 * "*")
    print("ERROR: {0} requires python >= 3.5.x. ".format(sys.argv[0]))
    print("It appears that you are running python {0}".format(
        ".".join(str(x) for x in sys.version_info[0:3])))
    print(70 * "*")
    sys.exit(1)


# -----------------------------------------------------------------------------
#
# User input
#
# -----------------------------------------------------------------------------
def commandline_options():
    """Process the command line arguments.

    """
    description = """Manage 3rd-party libraries.
    Note: For now this must be run from the root of the repository.
"""

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('--backtrace', action='store_true',
                        help='show exception backtraces as extra debugging '
                        'output')

    parser.add_argument('--debug', action='store_true',
                        help='extra debugging output')

    parser.add_argument('--dry-run', action='store_true',
                        help='just print the commands that would be executed')

    parser.add_argument('--config', nargs=1,
                        default=['3rd-party/3rd-party.cfg'],
                        help='path to config file')

    options = parser.parse_args()
    return options


def read_config_file(filename):
    """Read the configuration file

    """
    print("Reading configuration file : {0}".format(filename))

    cfg_file = os.path.abspath(filename)
    if not os.path.isfile(cfg_file):
        raise RuntimeError("Could not find config file: {0}".format(cfg_file))

    config = configparser.ConfigParser()
    config.read(cfg_file)

    return config


# -----------------------------------------------------------------------------
#
# work functions
#
# -----------------------------------------------------------------------------
def process_3rd_party_library(options, name, third_party_lib):
    """determine the type of third party libary that needs to be processed.
    """
    print("Processing: {0}".format(name))
    if options.debug:
        for opt in third_party_lib:
            print("{0} = {1}".format(opt, third_party_lib[opt]))

    try:
        tpl_type = third_party_lib['type'].strip()
    except configparser.NoOptionError as e:
        print(e)
        message = ("Each section must contain a 'type' option specifying"
                   "the source type of the 3rd-party library..")
        raise RuntimeError(message)

    if tpl_type == 'git subtree':
        process_git_subtree(options, name, third_party_lib)
    else:
        print("3rd-party libraryr '{0}'. Unknown type = '{1}'.".format(
            name, tpl_type))


def process_git_subtree(options, name, subtree_info):
    """start processing a git subtree
    """
    try:
        version = subtree_info['version']
        url = subtree_info['url']
    except configparser.NoOptionError as e:
        print(e)
        message = "git subtree requires options for 'url' and 'version'."
        raise RuntimeError(message)

    # subtree requires that the repos status be clean, i.e. no staged
    # files, no modified files in the working directory.
    check_git_status(options.debug)

    subtree_dir = os.path.join('3rd-party', name)
    if os.path.isdir(subtree_dir):
        # directory already exists, try to update
        git_subtree(options, 'pull', subtree_dir, url, version)
    else:
        git_subtree(options, 'add', subtree_dir, url, version)


def git_subtree(options, command, subtree_dir, url, version):
    """process git subtree at the correct version.

    """
    cmd = [
        'git',
        'subtree',
        command,
        '--squash',
        '--prefix',
        subtree_dir,
        url,
        version,
    ]
    print("    {0}".format(' '.join(cmd)))
    if not options.dry_run:
        try:
            subprocess.run(
                cmd, shell=False,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True)
        except subprocess.CalledProcessError:
            git_remove_subtree(cmd, subtree_dir)
            cmd[2] = 'add'
            subprocess.run(
                cmd, shell=False,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True)


def check_git_status(debug):
    """run the git status command, verify that the repo is clean
    """
    if options.debug:
        print("Running git status")
    cmd = [
        "git",
        "status",
        "--untracked-files=no",
        "--porcelain",
    ]
    called_process = subprocess.run(
        cmd, shell=False,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        universal_newlines=True)
    if len(called_process.stdout) > 0:
        print("Repo status not clean :\n{0}".format(called_process.stdout))
        if not options.dry_run:
            message = 'Repository must be clean to manipulate subtrees.'
            raise RuntimeError(message)


def git_remove_subtree(options, subtree_cmd, subtree_dir):
    """When a subtree can't be updated because of a git error, it seems
    like the only path forward is remove it and re-add it. so try
    that...

    """
    cmd = ['git',
           'rm',
           '-r',
           subtree_dir,
           ]
    print("    {0}".format(' '.join(cmd)))
    if not options.dry_run:
        subprocess.run(
            cmd, shell=False,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True)

    message = 'manually remove "{0}" subtree that can not be updated'.format(
        subtree_dir)
    cmd = ['git',
           'commit',
           '-m',
           message,
           ]
    print("    {0}".format(' '.join(cmd)))
    if not options.dry_run:
        subprocess.run(
            cmd, shell=False,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True)


# -----------------------------------------------------------------------------
#
# main
#
# -----------------------------------------------------------------------------

def main(options):
    if options.dry_run:
        print("Dry run")
    config = read_config_file(options.config[0])
    for section in config.sections():
        process_3rd_party_library(options, section, config[section])

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
