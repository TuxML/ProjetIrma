#!/usr/bin/python3

import argparse
import os
import shutil

from compilation.environment import get_environment_details, print_environment_details
from compilation.configuration import create_configuration, print_configuration
from compilation.package_manager import PackageManager
from compilation.logger import Logger
from compilation.compiler import Compiler
from compilation.database_management import stub_insert_new_data_into_database
import compilation.settings as settings


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
    parser.add_argument(
        "--cpu_cores",
        help="Give the number of cpu cores to use. Default to 0, which mean all"
             " the cores.",
        default=0
    )
    return parser.parse_args()


def create_logger(silent):
    return Logger(
        settings.OUTPUT_FILE,
        settings.STDOUT_FILE,
        settings.STDERR_FILE,
        silent
    )


def retrieve_and_display_environment(logger):
    logger.timed_print_output("Getting environment details.")
    environment = get_environment_details()
    print_environment_details(environment, logger.print_output)
    return environment


def retrieve_and_display_configuration(logger, args):
    logger.timed_print_output("Getting configuration details.")
    configuration = create_configuration(args)
    print_configuration(configuration, logger.print_output)
    return configuration


## run
# @author Picard Michaël
# @version 1
# @brief Do all the test, from compilation to sending the result to the database
# @details It does all the job, but for one and only one compilation. Therefore,
# it should be called multiple time for multiple compilation.
def run(logger, configuration, environment, args, package_manager,
        optional_config_file=None, cid_before=None):
    compiler = Compiler(logger, configuration, args, package_manager,
                        optional_config_file)
    compiler.run()
    compilation_result = compiler.get_compilation_dictionary()

    boot_result = None
    if compiler.is_successful():
        # todo
        pass

    cid = stub_insert_new_data_into_database(
        compilation_result,
        environment['hardware'],
        environment['software'],
        cid_incremental=cid_before,
        boot=boot_result
    )

    archive_log(cid)

    return cid


def archive_log(cid):
    directory = "{}/{}".format(settings.LOG_DIRECTORY, cid)
    os.makedirs(directory)
    file_list = [file for file in os.listdir(settings.LOG_DIRECTORY)
                 if os.path.isfile(os.path.join(settings.LOG_DIRECTORY, file))]
    for file in file_list:
        shutil.move(
            os.path.join(settings.LOG_DIRECTORY, file),
            os.path.join(directory, file))


if __name__ == "__main__":
    # Initialisation
    args = parser()
    logger = create_logger(args.silent)
    package_manager = PackageManager(logger, settings.DEPENDENCIES_FILE)
    package_manager.update_system()
    environment = retrieve_and_display_environment(logger)
    configuration = retrieve_and_display_configuration(logger, args)

    # Do a compilation, do the test and send result
    run(logger, configuration, environment, args, package_manager)
