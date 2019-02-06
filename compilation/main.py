#!/usr/bin/python3

import argparse

from compilation.environment import get_environment_details, print_environment_details
from compilation.configuration import create_configuration, print_configuration
from compilation.Logger import Logger

def parser():
    parser = argparse.ArgumentParser(
        description=""  # TODO: Fill the description
    )
    parser.add_argument(
        "incremental",
        type=int,
        help="Optional. Provide the number of additional incremental "
             "compilation. Have to be 0 or over.",
        nargs='?',
        default=0
    )
    parser.add_argument(
        "-s", "--silent",
        action="store_true",
        help="Prevent printing on standard output when compiling."
    )
    parser.add_argument(
        "--tiny",
        action="store_true",
        help="Use Linux tiny configuration. Incompatible with --config "
             "argument."
    )
    parser.add_argument(
        "--config",
        help="Give a path to specific configuration file. Incompatible with "
             "--tiny argument."
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parser()

    logger = Logger(
        "/TuxML/output",
        "/TuxML/out.log",
        "/TuxML/err.log",
        args.silent)

    logger.timed_print_output("Getting environment details.")
    environment = get_environment_details()
    print_environment_details(environment, logger.print_output)

    logger.timed_print_output("Getting configuration details.")
    configuration = create_configuration(args)
    print_configuration(configuration, logger.print_output)
