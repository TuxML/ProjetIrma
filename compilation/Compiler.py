# @file Compilator.py

import re
import subprocess
import shutil
import time

from compilation.Logger import *
from compilation.package_management import *
import compilation.settings as settings


class Compiler:
    def __init__(self, logger, configuration, args, optional_config_file=None):
        self.__logger = logger
        self.__nb_core = configuration['core_used']
        self.__kernel_path = configuration['kernel_path']

        # Variables results
        self.__compilation_time = 0
        self.__installed_package = list()
        self.__kernel_size = -1
        self.__kernel_compressed_size = ""

        file = args.config
        if optional_config_file is not None:
            file = optional_config_file
        self.__linux_config_generator(args.tiny, file)
        self.__do_a_compilation()
        # Logging compilation result
        if self.is_successful():
            self.__logger.timed_print_output(
                "Successfully compiled in {}".format(
                    time.strftime("%H:%M:%S",
                                  time.gmtime(self.__compilation_time))
                ),
                color=COLOR_SUCCESS
            )
        else:
            self.__logger.timed_print_output(
                "Unable to compile using this KCONFIG_FILE, status={}".format(
                    self.__compilation_time),
                color=COLOR_ERROR
            )

    def __do_a_compilation(self):
        start_compilation_timer = time.time()
        install_time_cpt = 0
        self.__logger.reset_stdout_pipe()
        self.__logger.reset_stderr_pipe()

        while not self.__compile():
            start_installation_timer = time.time()

            success, missing_files, missing_package = self.__log_analyser()
            if not success:
                self.__compilation_time = -2
                return
            elif self.__install_missing(missing_files, missing_package):
                self.__logger("Restarting compilation",
                              color=COLOR_SUCCESS)
            else:
                self.__compilation_time = -3
                return
            stop_installation_timer = time.time()

            install_time_cpt += \
                stop_installation_timer - start_installation_timer
            self.__logger.reset_stdout_pipe()
            self.__logger.reset_stderr_pipe()

        end_compilation_timer = time.time()
        self.__compilation_time = \
            end_compilation_timer - start_compilation_timer - install_time_cpt

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
            args="make -C {} -j | ts -s".format(
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

    def __install_missing(self, files, packages):
        return build_dependencies(files, packages) and \
               install_package(self.__logger, packages)

    def is_successful(self):
        return self.__compilation_time > 0

    def get_compilation_dictionary(self):
        # TODO
        pass
