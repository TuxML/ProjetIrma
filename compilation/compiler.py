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
    def __init__(self, logger, configuration, args, package_manager, optional_config_file=None):
        self.__logger = logger
        self.__nb_core = configuration['core_used']
        self.__kernel_path = configuration['kernel_path']
        self.__configuration = configuration
        self.__args = args
        self.__package_manager = package_manager
        self.__optional_config_file = optional_config_file

        # Variables results
        self.__compilation_success = False
        self.__compilation_time = 0
        self.__kernel_size = -1
        self.__kernel_compressed_size = ""
        self.__result_dictionary = {}

        # Presetting of __kernel_compressed_size
        for compression in settings.KERNEL_COMPRESSION_TYPE:
            for typ in ["-bzimage", "-vmlinux", ""]:
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
        file = self.__args.config
        if self.__optional_config_file is not None:
            file = self.__optional_config_file
        self.__linux_config_generator(self.__args.tiny, file)
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
        start_compilation_timer = time.time()
        install_time_cpt = 0
        self.__logger.reset_stdout_pipe()
        self.__logger.reset_stderr_pipe()
        self.__compilation_success = True

        while self.__compilation_success and not self.__compile():
            start_installation_timer = time.time()

            success, missing_files, missing_package = self.__log_analyser()
            retry = success and self.__package_manager.fix_missing_dependencies(
                missing_files, missing_package)

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
            self.__logger.timed_print_output(
                "Random config with preset values here : {} .".format(
                    settings.CONFIG_SEED_FILE))
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
        return self.__compilation_success

    ## get_compilation_dictionary
    # @author PICARD Michaël
    # @version 1
    # @brief Return a dictionary containing all the data about compilation.
    # @details All the key represent each field (minus cid) of the bdd.
    def get_compilation_dictionary(self):
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
            "compiled_kernel_version":
                self.__configuration['kernel_version_compilation']
        }
