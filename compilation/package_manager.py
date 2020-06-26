"""
:author: LE FLEM Erwan, LEBRETON Mickaël, MERZOUK Fahim, PICARD Michaël
:version: 2
"""

import subprocess

from compilation.logger import COLOR_SUCCESS, COLOR_ERROR


## PackageManager
# @author PICARD Michaël
# @version 1
# @brief PackageManager object manage all package related method. It update the
# system package manager, install new package, search for package to install
# when dependencies and more importantly, keep a list of all the installed
# package into the container.
class PackageManager:
    """Manageùent of all package related methods. It updates the system
    package manager, installs new package, search for package to
    install and dependencies. 
    
    .. note:: ``PackageManager`` keeps a list of all the installed\
    package into the container.

    :param logger: log manager
    :type logger: `Logger <logger.html>`_
    :param dependencies_file: path to the file containing all the\
    installed packages
    :type dependencies_file: str
    """
    # @param dependencies_file Path to the file containing all the installed
    # packages.
    def __init__(self, logger, dependencies_file):
        self.__logger = logger
        with open(dependencies_file, "r") as dependencies:
            self.__package_list = [x.strip() for y in dependencies.read().splitlines()
                                   for x in y.split(' ')]

    ## update_system
    # @author LE FLEM Erwan, LEBRETON Mickaël, MERZOUK Fahim, PICARD Michaël
    # @version 2
    # @brief Update package list and upgrade package who need it.
    def update_system(self):
        """Update package list and upgrade if in need

        """
        self.__logger.timed_print_output("Updating packages repositories.")
        subprocess.run(
            "apt-get update && apt-file update",
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=self.__logger.get_stderr_pipe()
        )
        self.__logger.timed_print_output(
            "Packages repositories updated and packages upgraded.",
            color=COLOR_SUCCESS
        )

    ## install_package
    # @author LE FLEM Erwan, LEBRETON Mickaël, MERZOUK Fahim, PICARD Michaël
    # @version 2
    # @brief Install a list of package and add them to the list of installed
    # package.
    # @return True if successful.
    def install_package(self, package_list):
        """Install a package and add it to the list of installed packages.

        :param package_list: packages to install
        :type package_list: list
        :return: either the package was installed successfully or not
        :rtype: bool
        """
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

    ## __install_one_package
    # @author LE FLEM Erwan, LEBRETON Mickaël, MERZOUK Fahim, PICARD Michaël
    # @version 2
    # @brief Install a package and add it to the list of installed
    # package.
    # @return True if successful.
    def __install_one_package(self, package):
        """Install a package and add it to the list of installed packages

        :param package: 
        :type package:
        :return: either the package was installed successfully or not
        :rtype: bool
        """
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

    ## fix_missing_dependencies
    # @author LE FLEM Erwan, LEBRETON Mickaël, MERZOUK Fahim, PICARD Michaël
    # @version 2
    # @brief Given a list of missing files and missing_packages, try to fix
    # missing dependencies.
    # @return True if successful.
    def fix_missing_dependencies(self, missing_files, missing_packages):
        """ Fix missing dependencies
        
        :param missing_files: files that are missing
        :type missing_files: list
        :param missing_packages: packages that are missing 
        :type missing_packages: list
        :return: either the dependencies were fixed or not
        :rtype: bool
        """
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

                    # Because of the linux self management package
                    # dependencies, we can't be 100% sure that our
                    # package is already here. So we verify with a
                    # subprocess call.  A call returning 1 mean that
                    # the package isn't installed.  Note that if it is
                    # already installed, we could have add it to the
                    # __package_list, but we choose to don't do it,
                    # because it will be present, whether we check it
                    # or not and this could mess with the
                    # database. This behaviour could be changed later.
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
                    # Not the proper way, but we avoid recopying code
                    # with this.
                    raise subprocess.CalledProcessError(0, '')
            except subprocess.CalledProcessError:
                self.__logger.timed_print_output(
                    "Unable to find the missing package for missing file : "
                    "{}".format(file),
                    color=COLOR_ERROR
                )
                return False

        # Adding all the missing_packages if not already in the
        # new_packages list.
        
        # Note that we double check every package to be sure that it's
        # not already installed and mean something corrupted occur.

        # TODO: what if the program is already present? like an error
        # while calling it?
        for package in missing_packages:
            if package in self.__package_list:
                self.__logger.timed_print_output(
                    "Fatal error : '{}' is called missing while he is "
                    "already present!".format(package),
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
                "been fixed.",
                color=COLOR_SUCCESS
            )
        return ret

    ## get_package_list_copy
    # @author PICARD Michaël
    # @version 1
    # @brief return the list of installed packages
    # @return list(str)
    def get_package_list_copy(self):
        """Gives the list of installed packages

        :return: installed packages
        :rtype: list
        """
        return self.__package_list.copy()
