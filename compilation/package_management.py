## @file package_management.py

import subprocess

from compilation.Logger import COLOR_SUCCESS


def update_system(logger):
    logger.timed_print_output("Updating packages repositories and "
                              "upgrading packages.")
    subprocess.run(
        "apt-get update && apt-file update && apt-get upgrade",
        shell=True,
        check=True,
        stdout=logger.get_stdout_pipe(),
        stderr=logger.get_stderr_pipe()
    )
    logger.timed_print_output(
        "Packages repositories updated and packages upgraded.",
        color=COLOR_SUCCESS
    )


def install_package(logger, package_list=list()):
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
