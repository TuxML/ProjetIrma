# @file Compilator.py

import re
import subprocess
import shutil
import time
import os
import bz2

from compilation.Logger import *
import compilation.settings as settings


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
        self.__compilation_success = True
        self.__compilation_time = 0
        self.__installed_package = list()
        self.__kernel_size = -1
        self.__kernel_compressed_size = ""
        self.__result_dictionary = {}

    def run(self):
        file = self.__args.config
        if self.__optional_config_file is not None:
            file = self.__optional_config_file
        self.__linux_config_generator(self.__args.tiny, file)
        self.__do_a_compilation()

        if self.__compilation_success:
            self.__retrieve_kernel_size()
            self.__get_compressed_kernel_size()

        self.__set_result_dictionary()

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
                self.__logger("Restarting compilation", color=COLOR_SUCCESS)
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
                args="KCONFIG_ALLCONFIG={} make -C {} tinyconfig".format(
                    settings.TINY_CONFIG_SEED_FILE,
                    self.__kernel_path
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
                args="KCONFIG_ALLCONFIG={} make -C {} randconfig".format(
                    settings.CONFIG_SEED_FILE,
                    self.__kernel_path
                ),
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=self.__logger.get_stderr_pipe(),
                check=True
            )

    def __compile(self):
        self.__logger.timed_print_output("Compilation in progress")
        failure = subprocess.call(
            args="make -C {} -j{} | ts -s".format(
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
                    files.append(line.split(":")[4])
                elif re.search("Command not found", line):
                    # case "make[4]: <command> : command not found"
                    packages.append(line.split(":")[1])
                elif re.search("not found", line):
                    if len(line.split(":")) == 4:
                        # case "/bin/sh: 1: <command>: not found"
                        files.append(line.split(":")[2])
                    else:
                        # ./scripts/gcc-plugin.sh: 11: ./scripts/gcc-plugin.sh: <package>: not found
                        packages.append(line.split(":")[3])

        success = len(files) > 0 or len(packages) > 0
        if success:
            self.__logger.timed_print_output(
                "Missing file(s)/package(s) found.", color=COLOR_SUCCESS)
        else:
            self.__logger.timed_print_output(
                "Unable to find the missing package(s).", color=COLOR_ERROR)
        return success, files, packages

    def is_successful(self):
        return self.__compilation_success

    def get_compilation_dictionary(self):
        return self.__result_dictionary

    def __retrieve_kernel_size(self):
        full_filename = "{}/vmlinux".format(self.__kernel_path)
        if os.path.isfile(full_filename):
            self.__kernel_size = os.path.getsize(full_filename)

    def __get_compressed_kernel_size(self):
        # TODO
        pass

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
