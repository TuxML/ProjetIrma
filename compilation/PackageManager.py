## @file PackageManager.py

import subprocess

from compilation.Logger import COLOR_SUCCESS, COLOR_ERROR


class PackageManager:
    def __init__(self, logger, dependencies_file):
        self.__logger = logger
        with open(dependencies_file, "r") as dependencies:
            self.__package_list = [x for y in dependencies.read().splitlines()
                                   for x in y.split(' ')]

    def update_system(self):
        self.__logger.timed_print_output("Updating packages repositories and "
                                         "upgrading packages.")
        subprocess.run(
            "apt-get update && apt-file update && apt-get upgrade -y",
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=self.__logger.get_stderr_pipe()
        )
        self.__logger.timed_print_output(
            "Packages repositories updated and packages upgraded.",
            color=COLOR_SUCCESS
        )

    def install_package(self, package_list):
        self.__logger.timed_print_output(
            "Installing package(s) : {}".format(" ".join(package_list)))
        for package in package_list:
            if not self.__install_one_package(package):
                self.__logger.timed_print_output(
                    "Error while installing the package {}.".format(package),
                    color=COLOR_ERROR
                )
                return False
        self.__logger.timed_print_output(
            "All the packages were found and installed.",
            color=COLOR_SUCCESS
        )

    def __install_one_package(self, package):
        try:
            subprocess.run(
                "apt-get -y install {}".format(package),
                shell=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=self.__logger.get_stderr_pipe()
            )
            self.__package_list.append(package)
            return True
        except subprocess.CalledProcessError:
            return False

    def fix_missing_dependencies(self, missing_files, missing_packages):
        # TODO: translate tuxml_depman.build_dependencies
        new_packages = list()
        return False

    def get_package_list_copy(self):
        return self.__package_list.copy()
