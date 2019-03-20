#!/usr/bin/python3

import argparse
import os
import shutil

from compilation.environment import get_environment_details, print_environment_details
from compilation.configuration import create_configuration, print_configuration
from compilation.package_manager import PackageManager
from compilation.logger import Logger, COLOR_SUCCESS
from compilation.compiler import Compiler
from compilation.boot_checker import BootChecker
from compilation.database_management import fetch_connection_to_database, insert_if_not_exist_and_fetch_hardware, insert_if_not_exist_and_fetch_software, insert_and_fetch_compilation, insert_incrementals_compilation, insert_boot_result
import compilation.settings as settings


## parser
# @author PICARD Michaël
# @version 1
# @brief Parse the commandline and return the parsed argument.
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


## create_logger
# @author PICARD Michaël
# @version 1
# @brief Create the logger object and return it.
def create_logger(silent):
    return Logger(
        settings.OUTPUT_FILE,
        settings.STDOUT_FILE,
        settings.STDERR_FILE,
        settings.BOOT_FILE,
        silent
    )


## retrieve_and_display_environment
# @author PICARD Michaël
# @version 1
# @brief Retrieve and display the environment dictionary.
def retrieve_and_display_environment(logger):
    logger.timed_print_output("Getting environment details.")
    environment = get_environment_details()
    print_environment_details(environment, logger.print_output)
    return environment


## retrieve_and_display_configuration
# @author PICARD Michaël
# @version 1
# @brief Retrieve and display the configuration dictionary.
def retrieve_and_display_configuration(logger, args):
    logger.timed_print_output("Getting configuration details.")
    configuration = create_configuration(int(args.cpu_cores), args.incremental != 0)
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
    file = args.config
    if optional_config_file is not None:
        file = optional_config_file
    compiler = Compiler(
        logger=logger,
        package_manager=package_manager,
        nb_core=args.cpu_cores,
        kernel_path=configuration['kernel_path'],
        kernel_version=configuration['kernel_version_compilation'],
        tiny=args.tiny,
        config_file=file
    )
    compiler.run()
    compilation_result = compiler.get_compilation_dictionary()

    boot_result = None
    if compiler.is_successful():
        boot_checker = BootChecker(logger, configuration)
        boot_checker.run()
        boot_result = boot_checker.get_boot_dictionary()
    else:
        logger.reset_boot_pipe()

    cid = insert_result_into_database(
        logger,
        compilation_result,
        environment['hardware'],
        environment['software'],
        cid_before,
        boot_result
    )

    archive_log(cid)

    return cid


## archive_log
# @author PICARD Michaël
# @version 1
# @brief Retrieve the logs file, create a directory named <cid>, and put the log
# in the created directory.
def archive_log(cid):
    directory = "{}/{}".format(settings.LOG_DIRECTORY, cid)
    os.makedirs(directory)
    file_list = [file for file in os.listdir(settings.LOG_DIRECTORY)
                 if os.path.isfile(os.path.join(settings.LOG_DIRECTORY, file))]
    for file in file_list:
        shutil.copy2(
            os.path.join(settings.LOG_DIRECTORY, file),
            os.path.join(directory, file))


## insert_result_into_database
# @author PICARD Michaël
# @version 1
# @brief Send the sample result onto the data.
def insert_result_into_database(logger, compilation, hardware, software,
                                cid_incremental=None, boot=None):
    logger.timed_print_output("Sending result to database.")
    connection = fetch_connection_to_database(
        settings.IP_BDD,
        settings.USERNAME_BDD,
        settings.PASSWORD_USERNAME_BDD,
        settings.NAME_BDD)
    cursor = connection.cursor()

    hid = insert_if_not_exist_and_fetch_hardware(connection, cursor, hardware)
    sid = insert_if_not_exist_and_fetch_software(connection, cursor, software)
    compilation['hid'] = str(hid)
    compilation['sid'] = str(sid)
    cid = insert_and_fetch_compilation(connection, cursor, compilation)
    if cid_incremental is not None:
        insert_incrementals_compilation(
            connection, cursor,
            {'cid': str(cid), 'cid_base': str(cid_incremental)})
    if boot is not None:
        boot['cid'] = str(cid)
        insert_boot_result(connection, cursor, boot)

    logger.timed_print_output("Successfully send result with cid : {}".format(
        cid), color=COLOR_SUCCESS)
    return cid


## remove_logs_file
# @author PICARD Michaël
# @version 1
# @brief Remove logs files, but not the logs that are "archived" ie put in a
# subdirectory.
def remove_logs_file():
    file_list = [file for file in os.listdir(settings.LOG_DIRECTORY)
                 if os.path.isfile(os.path.join(settings.LOG_DIRECTORY, file))]
    for file in file_list:
        os.remove(os.path.join(settings.LOG_DIRECTORY, file))


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

    # Cleaning the container
    del logger
    remove_logs_file()
