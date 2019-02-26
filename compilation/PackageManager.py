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
        return True

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
        self.__logger.timed_print_output(
            "Fixing missing file(s)/package(s) dependencies."
        )
        new_packages = list()

        # Getting new package for each missing file.
        for file in missing_files:
            try:
                output = subprocess.check_output(
                    args="apt-file search {}".format(file),
                    shell=True,
                    stderr=self.__logger.get_stderr_pipe()
                ).decode(errors="replace")
                lines = output.splitlines()

                # We could have multiple package proposed. In this case, we
                # select to install the first package who isn't already
                # installed. Also, we have to be sure that the result is really
                # the requested file.
                package_found = False
                for line in lines:
                    package = line.split(":")[0]
                    file_check = line.split(':')[1].split('/')[-1]
                    if file_check != file:
                        continue  # Not the right file
                    if package in self.__package_list:
                        continue  # Already installed
                    # Because of the linux self management package dependencies,
                    # we can't be 100% sure that our package is already here. So
                    # we verify with a subprocess call.
                    # A call returning 1 mean that the package isn't
                    # installed.
                    # Note that if it is already installed, we could have add it
                    # to the __package_list, but we choose to don't do it,
                    # because it will be present, whether we check it or not and
                    # this could mess with the database. This behaviour could be
                    # changed later.
                    if subprocess.call(
                        args="dpkg-query -l | grep {}".format(package),
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    ):
                        # Not need to add a package twice to the list of new
                        # packages.
                        if package not in new_packages:
                            new_packages.append(package)
                        package_found = True
                        break
                if not package_found:
                    # Not the proper way, but we avoid recopying code with this.
                    raise subprocess.CalledProcessError(0, '')
            except subprocess.CalledProcessError:
                self.__logger.timed_print_output(
                    "Unable to find the missing package for missing file : "
                    "{}".format(file),
                    color=COLOR_ERROR
                )
                return False

        # Adding all the missing_packages if not already in the new_packages
        # list.
        # Note that we double check every package to be sure that it's not
        # already installed and mean something corrupted occur.
        for package in missing_packages:
            if package in self.__package_list or not subprocess.call(
                    args="dpkg-query -l | grep {}".format(file),
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
            ):
                self.__logger.timed_print_output(
                    "Fatal error : a package is called missing while he is "
                    "already present!",
                    color=COLOR_ERROR
                )
                return False
            if package not in new_packages:
                new_packages.append(package)

        # We now install all the new_packages.
        ret = self.install_package(new_packages)
        if ret:
            self.__logger.timed_print_output(
                "Missing file(s)/package(s) dependencies should have "
                "been fixed."
            )
        return ret

    def get_package_list_copy(self):
        return self.__package_list.copy()
