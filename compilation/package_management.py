## @file package_management.py

import subprocess

from compilation.Logger import COLOR_SUCCESS
from compilation.settings import COMPILER_DEPENDENCIES, MOST_COMMON_DEPENDENCIES


def update_system(logger):
    logger.timed_print_output("Updating packages repositories.")
    subprocess.run(
        "apt-get update && apt-file update",
        shell=True,
        check=True,
        stdout=logger.get_stdout_pipe(),
        stderr=logger.get_stderr_pipe()
    )
    logger.timed_print_output(
        "Packages repositories updated.",
        color=COLOR_SUCCESS
    )


def __install_package(logger, package_list=list()):
    logger.timed_print_output(
        "Installing package(s) : {}".format(" ".join(package_list)))
    subprocess.run(
        "apt-get -y install {}".format(" ".join(package_list)),
        shell=True,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=logger.get_output_pipe()
    )
    logger.timed_print_output(
        "All the packages were found and installed.",
        color=COLOR_SUCCESS
    )


## install_compiler_dependencies
# @author LE FLEM Erwan, FAHIM Merzouk, PICARD Michaël
# @version 2
# @brief Install the compiler and its dependencies, if needed
def install_compiler_dependencies(logger):
    logger.timed_print_output("Installing compiler's dependencies.")
    __install_package(logger, COMPILER_DEPENDENCIES)
    logger.timed_print_output(
        "Compiler's dependencies successfully installed.",
        color=COLOR_SUCCESS
    )


## install_most_common_dependencies
# @author LE FLEM Erwan, FAHIM Merzouk, PICARD Michaël
# @version 2
# @brief Install the most commonly needed dependencies in order to compile a
# kernel.
def install_most_common_dependencies(logger):
    logger.timed_print_output("Installing most common dependencies.")
    __install_package(logger, MOST_COMMON_DEPENDENCIES)
    logger.timed_print_output(
        "Most common dependencies successfully installed.",
        color=COLOR_SUCCESS
    )
