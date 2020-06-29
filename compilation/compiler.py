
"""Management of the compiler

:author: LEBRETON Mickaël, PICARD Michaël, POLES Malo, LE MASLE Alexis
:version: 2
"""
# @file compiler.py

import re
import subprocess
import shutil
import time
import os
import bz2

from compilation.logger import *
import compilation.settings as settings


## Compiler
# @author PICARD Michaël
# @version 1
# @brief Compiler object is a wrapper to do a compilation.
# @details Compiler object handle everything related to a compilation.
# To use it, create it, call the method run once and you can retrieve all the
# compilation result with is_successful and and get_compilation_dictionary.
class Compiler:
    """Wrapper for the compilation. Handle everything related to compiling
    the kernel. To use the compiler class, create a ``Compiler``
    instance then run it with the ``run`` method. The method
    ``is_successful`` will tell if the compilation was made
    successfully and more info about compilation can be retrieve with
    the method ``get_compilation_dictionary``.

    :param logger: Log (output) manager
    :type logger: `Logger <logger.html>`_
    :param package_manager: package manager to use
    :type package_manager: `PackageManager <package_manager.html>`_
    :param nb_core: number of cores to use for the compilation
    :type nb_core: int
    :param kernel_path: path to the Linux kernel directory
    :type kernel_path: str
    :param kernel_version: version of the Linux kernel
    :type kernel_version: str
    :param tiny: tiny configuration of the Linux kernel
    :type tiny: bool
    :param config_file: path to the configuration file (``.config``)
    :type config_file: str

    """    
    def __init__(self, logger, package_manager, nb_core, kernel_path,
                 kernel_version, tiny=False, config_file=None):
        """Constructor method

        """
        assert(logger is not None)
        assert(package_manager is not None)
        if config_file is not None:
            assert(not tiny)

        self.__logger = logger
        self.__nb_core = nb_core
        self.__kernel_path = kernel_path
        self.__package_manager = package_manager
        self.__kernel_version = kernel_version
        self.__tiny = tiny
        self.__config_file = config_file

        # Variables results
        self.__compilation_success = False
        self.__compilation_time = 0
        self.__kernel_size = -1
        self.__kernel_compressed_size = ""
        self.__result_dictionary = {}

        # Presetting of __kernel_compressed_size
        for compression in settings.KERNEL_COMPRESSION_TYPE:
            for typ in ["-bzImage", "-vmlinux", ""]:
                self.__kernel_compressed_size = "{}{}{} : -1 , ".format(
                    self.__kernel_compressed_size,
                    compression,
                    typ
                )
        self.__kernel_compressed_size = self.__kernel_compressed_size[:-3]

    ## run
    # @author PICARD Michaël
    # @version 1
    # @brief Call it once to do the whole compilation process.
    # @details Thread like method.
    def run(self):
        """Generates a configuration, launch compilation and retrieve data
        about the process.

        """
        self.__linux_config_generator(self.__tiny, self.__config_file)
        self.__do_a_compilation()

        if self.__compilation_success:
            self.__kernel_size = self.__retrieve_kernel_size(
                "{}/vmlinux".format(self.__kernel_path))
            self.__get_compressed_kernel_size()

        self.__set_result_dictionary()

    ## __do_a_compilation
    # @author LEBRETON Mickaël, PICARD Michaël
    # @version 2
    # @brief Run a compilation, with autofix and timer.
    def __do_a_compilation(self):
        """Run a compilation, with autofix and timer.

        .. note:: *Autofix* fixes automatically dependencies of tools
         used for the compilation

        """
        start_compilation_timer = time.time()
        install_time_cpt = 0
        self.__logger.reset_stdout_pipe()
        self.__logger.reset_stderr_pipe()
        self.__compilation_success = True

        while self.__compilation_success and not self.__compile():
            start_installation_timer = time.time()

            success, missing_files, missing_package = self.__log_analyser()
            retry = success\
                and self.__package_manager\
                        .fix_missing_dependencies(missing_files,
                                                  missing_package)

            stop_installation_timer = time.time()
            install_time_cpt += \
                stop_installation_timer - start_installation_timer
            if retry:
                self.__logger.timed_print_output("Restarting compilation",
                                                 color=COLOR_SUCCESS)
                self.__logger.reset_stdout_pipe()
                self.__logger.reset_stderr_pipe()
            else:
                self.__compilation_success = False

        end_compilation_timer = time.time()
        self.__compilation_time = \
            end_compilation_timer - start_compilation_timer - install_time_cpt

        # Logging compilation result
        if self.is_successful():
            self.__logger.timed_print_output(
                "Successfully compiled in {} (installation_time = {})".format(
                    time.strftime(
                        "%H:%M:%S",
                        time.gmtime(self.__compilation_time)),
                    time.strftime(
                        "%H:%M:%S",
                        time.gmtime(install_time_cpt)),
                ),
                color=COLOR_SUCCESS
            )
        else:
            self.__logger.timed_print_output(
                "Unable to compile in {} (installation_time = {})".format(
                    time.strftime(
                        "%H:%M:%S",
                        time.gmtime(self.__compilation_time)),
                    time.strftime(
                        "%H:%M:%S",
                        time.gmtime(install_time_cpt)),
                ),
                color=COLOR_ERROR
            )

    ## __linux_config_generator
    # @author LEBRETON Mickaël, PICARD Michaël
    # @version 2
    # @brief Generate .config in the kernel folder, in order to compile with it.
    def __linux_config_generator(self, tiny, specific_config):
        """Generates .config in the kernel directory. (Calls tinyconfig or
        randconfig)

        :param tiny: set to True if you want a tiny Linux
        configuration. False otherwise.
        :type tiny: bool
        :param specific_config: path to a .config
        :type specific_config: str
        """
        if specific_config is not None:
            self.__logger.timed_print_output("Using specific KCONFIG file.")
            shutil.copyfile(
                specific_config, "{}/.config".format(self.__kernel_path))
        elif tiny:
            self.__logger.timed_print_output(
                "Tiny config with preset values here : {} .".format(
                    settings.TINY_CONFIG_SEED_FILE))
            subprocess.run(
                args="KCONFIG_ALLCONFIG={} make -C {} tinyconfig -j{}".format(
                    settings.TINY_CONFIG_SEED_FILE,
                    self.__kernel_path,
                    self.__nb_core
                ),
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=self.__logger.get_stderr_pipe(),
                check=True
            )
        else:
            self.__logger.print_output(
                "Random config based on the following preset values : ")
            with open(settings.CONFIG_SEED_FILE, 'r') as seed_list:
                self.__logger.print_output(seed_list.read())
            subprocess.run(
                args="KCONFIG_ALLCONFIG={} make -C {} randconfig -j{}".format(
                    settings.CONFIG_SEED_FILE,
                    self.__kernel_path,
                    self.__nb_core
                ),
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=self.__logger.get_stderr_pipe(),
                check=True
            )

    ## __compile
    # @author LEBRETON Mickaël, PICARD Michaël
    # @version 2
    # @brief Run a compilation and return is successful or not.
    # @details The main difference here is that this method don't count time
    # spend nor try to fix if the compilation fail. It just call the make and
    # return if the make is successful or not.
    def __compile(self):
        """Compile a Linux kernel and returns the status of the compilation
        (success or not). this method don't count time spend nor try
        to fix if the compilation fail. It just call the make and
        return if the make is successful or not.

        :return: status of the compilation: True if successful, False
        otherwise
        :rtype: bool
        """
        self.__logger.timed_print_output("Compilation in progress")
        failure = subprocess.call(
            args="make -C {} -j{}".format(
                self.__kernel_path,
                self.__nb_core
            ),
            shell=True,
            stdout=self.__logger.get_stdout_pipe(),
            stderr=self.__logger.get_stderr_pipe()
        )
        if not failure:
            self.__logger.timed_print_output(
                "Compilation successful.",
                color=COLOR_SUCCESS)
            return True
        else:
            self.__logger.timed_print_output(
                "Compilation failed, exit status : {}.".format(failure),
                color=COLOR_ERROR)
            return False

    ## log_analyser
    # @author LEBRETON Mickaël, PICARD Michaël
    # @version 2
    # @brief Analyse settings.STDERR_FILE
    # @return (status, missing_files, missing_packages)
    def __log_analyser(self):
        """Analyses ``settings.STDERR_FILE`` (log file).

        :return: Tuple like so: ``(status, missing_files,
        missing_packages)``
        :rtype: tuple
        """
        self.__logger.timed_print_output(
            "Analysing {}".format(settings.STDERR_FILE))
        files, packages = list(), list()

        with open(settings.STDERR_FILE, 'r') as err_logs:
            for line in err_logs:
                if re.search("fatal error", line):
                    # case "file.c:48:19: fatal error: <file.h>: No such file or directory"
                    files.append(line.split(":")[4].strip())
                elif re.search("Command not found", line):
                    # case "make[4]: <command> : command not found"
                    packages.append(line.split(":")[1].strip())
                elif re.search("not found", line):
                    if len(line.split(":")) == 4:
                        # case "/bin/sh: 1: <command>: not found"
                        packages.append(line.split(":")[2].strip())
                    else:
                        # ./scripts/gcc-plugin.sh: 11: ./scripts/gcc-plugin.sh: <package>: not found
                        packages.append(line.split(":")[3].strip())

        success = len(files) > 0 or len(packages) > 0
        if success:
            self.__logger.timed_print_output(
                "Missing file(s)/package(s) found.", color=COLOR_SUCCESS)
        else:
            self.__logger.timed_print_output(
                "Unable to find the missing package(s).", color=COLOR_ERROR)
        return success, files, packages

    ## is_successful
    # @author PICARD Michaël
    # @version 1
    def is_successful(self):
        """Predicate on the status of the previous compilation

        :return: either the compilation was successful or not
        :rtype: bool
        """
        return self.__compilation_success

    ## get_compilation_dictionary
    # @author PICARD Michaël
    # @version 1
    # @brief Return a dictionary containing all the data about compilation.
    # @details All the key represent each field (minus cid) of the bdd.
    def get_compilation_dictionary(self):
        """Gives all the data about the previous compilation. 

        Each key of the dictionary represents each field of the
        database (minus cid).

        :return: info about the compilation
        :rtype: dictionary
        """
        return self.__result_dictionary

    ## __retrieve_kernel_size
    # @author PICARD Michaël
    # @version 1
    # @brief Retrieve the kernel size
    # @details Check if the path exist, if yes, returns its size. If not, return
    # -1. Note that this method name is such, because this method is only use to
    # retrieve size of a kernel. But it could have been name __retrieve_size.
    @staticmethod
    def __retrieve_kernel_size(compiled_kernel_path):
        """Retrieve kernel size. 

        Checks if the path exists and if so, returns the size of the
        kernel. Otherwise, returns ``-1``.

        :param compiled_kernel_path: path to the compiled kernel
        :type compiled_kernel_path: str
        :return: size of the kernel if ``compiled_kernel_path`` does
        exists. ``-1`` otherwise.
        :rtype: int
        """
        if os.path.exists(compiled_kernel_path):
            return os.path.getsize(compiled_kernel_path)
        return -1

    ## __get_compressed_kernel_size
    # @author LE MASLE Alexis, PICARD Michaël
    # @version 2
    # @brief Get the size of the 18 differents compressed kernels
    # @return A string representing the result. The string is formatted like
    # "<compressed_kernel> : <size>"(" , <compressed_kernel> : <size>")*
    def __get_compressed_kernel_size(self):
        """Get size of each compressed kernel using 18 types of compression.

        :return: description of the result like so:
        ``<compressed_kernel> : <size> (, <compressed_kernel> :
        <size>)*``
        :rtype: str
        """
        self.__logger.timed_print_output("Computing compressed kernel size.")

        # saving the configuration file
        with open("{}/.config".format(self.__kernel_path), "rb") as config:
            basic_config = config.read()

        self.__kernel_compressed_size = ""
        for i in range(len(settings.KERNEL_COMPRESSION_TYPE)):
            compression = settings.KERNEL_COMPRESSION_TYPE[i]
            extension = settings.KERNEL_COMPRESSION_EXTENSIONS[i]

            self.__enable_only_one_compression_option(compression)
            subprocess.run(
                args="make -C {} -j{}".format(
                    self.__kernel_path,
                    self.__nb_core
                ),
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # bzImage
            self.__kernel_compressed_size = "{}{}-bzImage : {} , ".format(
                self.__kernel_compressed_size,
                compression,
                self.__retrieve_kernel_size(
                    "{}/arch/x86/boot/bzImage".format(
                        self.__kernel_path))
            )
            # vmlinux
            self.__kernel_compressed_size = "{}{}-vmlinux : {} , ".format(
                self.__kernel_compressed_size,
                compression,
                self.__retrieve_kernel_size(
                    "{}/arch/x86/boot/compressed/vmlinux".format(
                        self.__kernel_path))
            )
            # compressed
            path = "{}/arch/x86/boot/compressed".format(self.__kernel_path)
            size = -1
            for file in os.listdir(path):
                if os.path.isfile(os.path.join(path, file)) and file.endswith(extension):
                    size = self.__retrieve_kernel_size(os.path.join(path, file))
                    break
            self.__kernel_compressed_size = "{}{} : {} , ".format(
                self.__kernel_compressed_size,
                compression,
                size
            )
        self.__kernel_compressed_size = self.__kernel_compressed_size[:-3]

        # reset the configuration file to its earlier state
        with open("{}/.config".format(self.__kernel_path), "wb") as config:
            config.write(basic_config)
            config.flush()
            subprocess.run(
                args="make -C {} -j{}".format(
                    self.__kernel_path,
                    self.__nb_core
                ),
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        self.__logger.timed_print_output(
            "Successfully retrieve compressed kernel size.",
            color=COLOR_SUCCESS
        )

    ## __enable_only_one_compression_option
    # @author POLES Malo, PICARD Michaël
    # @version 2
    # @brief Enable one of the compression option.
    # @details The given compression_type have to be one of the
    # settings.KERNEL_COMPRESSION_TYPE. (And it's check at the beginning.)
    def __enable_only_one_compression_option(self, compression_type):
        """Enable one compression option.

        :param compression_type: type of compression name
        :type compression_type: str

        .. note:: ``compression_type`` should be in
        ``settings.KERNEL_COMPRESSION_TYPE``.

        :raises AssertionError: if ``compresion_type`` not in
        ``settings.KERNEL_COMPRESSION_TYPE``.
        """
        assert compression_type in settings.KERNEL_COMPRESSION_TYPE, \
            "{} isn't in {}!".format(compression_type,
                                     settings.KERNEL_COMPRESSION_TYPE)

        for c in settings.KERNEL_COMPRESSION_TYPE:
            self.__rewrite_option_config(
                "CONFIG_KERNEL_{}=y".format(c),
                "# CONFIG_KERNEL_{} is not set".format(c))
            self.__rewrite_option_config(
                "CONFIG_KERNEL_{}=m".format(c),
                "# CONFIG_KERNEL_{} is not set".format(c))
        self.__rewrite_option_config(
            "# CONFIG_KERNEL_{} is not set".format(compression_type),
            "CONFIG_KERNEL_{}=y".format(compression_type)
        )

    ## __rewrite_option_config
    # @author POLES Malo, PICARD Michaël
    # @version 2
    # @brief Rewrite one option of the linux configuration file.
    def __rewrite_option_config(self, before, after):
        """Rewrite an option of the .config

        :param before: initial name of the option
        :type before: str
        :param after: the new name of the option
        :type after: str
        """
        return not bool(subprocess.check_call(
            args="sed 's|{}|{}|' -i {}/.config".format(
                before,
                after,
                self.__kernel_path
            ),
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ))

    ## __set_result_dictionary
    # @author PICARD Michaël
    # @version 1
    # @brief Build the result dictionary by retrieving all its entry.
    def __set_result_dictionary(self):
        """Retrieve data about compilation and updates ``__result_dictionary``

        """
        self.__result_dictionary = {
            "compilation_date": time.strftime("%Y-%m-%d %H:%M:%S",
                                              time.localtime(time.time())),
            "compilation_time": self.__compilation_time,
            "config_file": bz2.compress(
                open("{}/.config".format(self.__kernel_path), "rb").read()),
            "stdout_log_file": bz2.compress(
                open(self.__logger.get_stdout_file(), "rb").read()),
            "stderr_log_file": bz2.compress(
                open(self.__logger.get_stderr_file(), "rb").read()),
            "user_output_file": bz2.compress(
                open(self.__logger.get_user_output_file(), "rb").read()),
            "compiled_kernel_size": self.__kernel_size,
            "compressed_compiled_kernel_size": self.__kernel_compressed_size,
            "dependencies": " ".join(
                self.__package_manager.get_package_list_copy()),
            "number_cpu_core_used": self.__nb_core,
            "compiled_kernel_version": self.__kernel_version
        }
