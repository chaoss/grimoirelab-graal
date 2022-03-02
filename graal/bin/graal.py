#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2020 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Valerio Cosentino <valcos@bitergia.com>
#     inishchith <inishchith@gmail.com>
#     pranjal.aswani <pranjal.aswani@halodoc.com>
#

import argparse
import logging
import sys

import graal.graal
import graal.backends.core


GRAAL_USAGE_MSG = """%(prog)s [-g] <backend> [<args>] | --help | --version"""

GRAAL_DESC_MSG = """Start a Graal quest to retrieve source code data from Git repositories.

Repositories are reached using specific backends, which are:

    cocom            Fetch code complexity for many programming languages
    codep            Fetch package and class dependencies of Python modules
    colang           Fetch code language distribution
    colic            Fetch license & copyright information
    coqua            Fetch code quality data of Python code
    covuln           Fetch security vulnerabilities in Python code

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show version
  -g, --debug           set debug mode on
"""

GRAAL_EPILOG_MSG = """Run '%(prog)s <backend> --help' to get information about a specific backend."""

GRAAL_VERSION_MSG = """%(prog)s """ + graal.backends.core.__version__


# Logging formats
GRAAL_LOG_FORMAT = "[%(asctime)s] - %(message)s"
GRAAL_DEBUG_LOG_FORMAT = "[%(asctime)s - %(name)s - %(levelname)s] - %(message)s"


def main():
    args = parse_args()

    _, GRAAL_CMDS = graal.graal.find_backends(graal.backends)

    if args.backend not in GRAAL_CMDS:
        raise RuntimeError("Unknown backend %s" % args.backend)

    configure_logging(args.debug)

    logging.info("Starting the quest for the Graal.")

    klass = GRAAL_CMDS[args.backend]
    cmd = klass(*args.backend_args)
    cmd.run()

    logging.info("Quest completed.")


def parse_args():
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(usage=GRAAL_USAGE_MSG,
                                     description=GRAAL_DESC_MSG,
                                     epilog=GRAAL_EPILOG_MSG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     add_help=False)

    parser.add_argument('-h', '--help', action='help',
                        help=argparse.SUPPRESS)
    parser.add_argument('-v', '--version', action='version',
                        version=GRAAL_VERSION_MSG,
                        help=argparse.SUPPRESS)
    parser.add_argument('-g', '--debug', dest='debug',
                        action='store_true',
                        help=argparse.SUPPRESS)
    parser.add_argument('backend', help=argparse.SUPPRESS)
    parser.add_argument('backend_args', nargs=argparse.REMAINDER,
                        help=argparse.SUPPRESS)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def configure_logging(debug=False):
    """Configure Graal logging

    The function configures the log messages produced by Graal.
    By default, log messages are sent to stderr. Set the parameter
    `debug` to activate the debug mode.

    :param debug: set the debug mode
    """
    if not debug:
        logging.basicConfig(level=logging.INFO,
                            format=GRAAL_LOG_FORMAT)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urrlib3').setLevel(logging.WARNING)
    else:
        logging.basicConfig(level=logging.DEBUG,
                            format=GRAAL_DEBUG_LOG_FORMAT)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        s = "\n\nReceived Ctrl-C or other break signal. Exiting.\n"
        sys.stderr.write(s)
        sys.exit(0)
