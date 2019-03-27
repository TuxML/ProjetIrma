# @file boot_checker.py

import bz2
import subprocess
from time import time, sleep

from compilation.logger import COLOR_ERROR, COLOR_SUCCESS
from compilation.settings import BOOTING_KERNEL_PATH, INITRAMFS_PATH, \
    MAX_TIME_BOOT


## BootChecker
# @author PICARD Michaël
# @author ROYON CHALENDARD Julien
# @author HAMON Cyril
# @author SAFFRAY Paul
class BootChecker:
    def __init__(self, logger, kernel_path):
        self.__logger = logger
        self.__executable_path = BOOTING_KERNEL_PATH.format(kernel_path)

        # Variables results
        self.__boot_success = False
        self.__boot_time = 0
        self.__result_dictionary = {}

    def run(self):
        self.__logger.reset_boot_pipe()
        self.__logger.timed_print_output("Checking if the kernel can boot.")

        boot_process = self.__bootprocess_create()

        timer_begin = time()
        while (time() - timer_begin) < MAX_TIME_BOOT:
            if self.__have_finished():
                break
            sleep(1)

        boot_process.kill()
        self.__boot_time = self.__get_result()
        if self.__boot_time == -2:
            self.__logger.timed_print_output(
                "Test took too much time (over {} seconds). "
                "Cancel the boot.".format(MAX_TIME_BOOT),
                color=COLOR_ERROR
            )
        elif self.__boot_time == -1:
            self.__logger.timed_print_output(
                "Boot failure.",
                color=COLOR_ERROR
            )
        else:
            self.__logger.timed_print_output(
                "Boot successful in {} seconds".format(self.__boot_time),
                color=COLOR_SUCCESS
            )
        self.__boot_success = self.__boot_time >= 0
        self.__set_result_dictionary()

    def __bootprocess_create(self):
        return subprocess.Popen(
            args="qemu-system-x86_64 -kernel {} -initrd {} -nographic "
                 "-append \"console=ttyS0\"".format(
                    self.__executable_path,
                    INITRAMFS_PATH),
            shell=True,
            stdout=self.__logger.get_boot_pipe(),
            stderr=subprocess.STDOUT
        )

    def __have_finished(self):
        with open(self.__logger.get_boot_file(), 'r') as output:
            content = output.read()
            return "Boot took" in content or "Kernel panic" in content

    def __get_result(self):
        with open(self.__logger.get_boot_file(), 'r') as output:
            for line in output.read().splitlines():
                if "Boot took" in line:
                    return float(line.split(' ')[2])
                if "Kernel panic" in line:
                    return -1
            return -2

    def __set_result_dictionary(self):
        self.__result_dictionary = {
            "boot_time": self.__boot_time,
            "boot_log_file": bz2.compress(
                open(self.__logger.get_boot_file(), "rb").read())
        }

    ## is_successful
    # @author PICARD Michaël
    # @version 1
    def is_successful(self):
        return self.__boot_success

    ## get_boot_dictionary
    # @author PICARD Michaël
    # @version 1
    # @brief Return a dictionary containing all the data about boot.
    # @details All the key represent each field (minus cid) of the bdd.
    def get_boot_dictionary(self):
        return self.__result_dictionary
