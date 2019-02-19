## @file package_management.py

import subprocess

from compilation.Logger import COLOR_SUCCESS, COLOR_FAILURE


def update_system(logger):
    logger.timed_print_output("Updating packages repositories and "
                              "upgrading packages.")
    subprocess.run(
        "apt-get update && apt-file update && apt-get upgrade -y",
        shell=True,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=logger.get_stderr_pipe()
    )
    logger.timed_print_output(
        "Packages repositories updated and packages upgraded.",
        color=COLOR_SUCCESS
    )


def install_package(logger, package_list):
    logger.timed_print_output(
        "Installing package(s) : {}".format(" ".join(package_list)))
    try:
        subprocess.run(
            "apt-get -y install {}".format(" ".join(package_list)),
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=logger.get_stderr_pipe()
        )
        logger.timed_print_output(
            "All the packages were found and installed.",
            color=COLOR_SUCCESS
        )
        return True
    except subprocess.CalledProcessError:
        logger.timed_print_output(
            "Error while installing the packages.",
            color=COLOR_FAILURE
        )
        return False


def build_dependencies(missing_files, missing_packages):
    # TODO: translate tuxml_depman.build_dependencies
    return False
