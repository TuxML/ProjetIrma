#!/usr/bin/python3

## @file tuxml_environment.py
# @author LE FLEM Erwan, LEBRETON Mickaël, PICARD Michaël
# @version 2
# @brief python3 methods to get data about compilation environment
# @details This file contains method to get data about compilation environment :
# - system :
#   + os
#   + distribution
#   + distrib_version
#   + os_kernel_version
# - hardware :
#   + cpu
#   + cpu_freq
#   + cpu_cores
#   + ram
#   + architecture
#   + mechanical_drive : Boolean
# - libs :
#   + libc_version
#   + gcc_version
# - others :
#   + core_used ? Should be the same as the number of core that the machine got,
#       so we make a duplicate here?
#   + kernel_compiled ? needed, but it's not environment data
#   + branch ? empty, so not needed? docker_image useless also?
#   + tuxml_version ? Could be usefull, but needed to be hardcoded in a settings
#        file
#   + incremental_mod ? shouldn't be in the environnement details, isn't it?

import platform
import os
import psutil
import subprocess


## _get_system_details
# @author LE FLEM Erwan, PICARD Michaël
# @version 2
# @brief Returns a dictionary containing system details
def __get_system_details():
    # Something smell bad here : we retrieve the os but already assume that is
    # an linux... so we try to get its distribution. With method that are
    # deprecated. Also, what if we try to get from a Mac/Windows/Java os?
    # If we always want to compile on a debian image (which imply that os and
    # distribution are always Linux and Debian) we should just get
    # distribution_version and os_kernel_version, which are mandatory to ensure
    # that any update have been recorded. Also, each entries correspond to an
    # entries on the database, with some obvious always the same result.
    # So what about change to something like :
    # - debian_version :
    # - kernel_version :
    # Even if we want to ensure that we can change the distribution
    # (e.g. alpine), the os entry will still be Linux.
    # About the deprecation, we can ignore it if we stick to a Python 3 version
    # before 3.7, where this method will be removed. (Deprecated with 3.5 :
    # https://docs.python.org/fr/3.5/library/platform.html#platform.linux_distribution)
    system = {
        "os": platform.system(),
        "distribution": platform.linux_distribution()[0],
        "distrib_version": platform.linux_distribution()[1],
        "os_kernel_version": platform.release()
    }
    return system


## __is_mechanical_disk
# @author LE FLEM Erwan, MERZOUK Fahim, THOMAS Luis, PICARD Michaël
# @version 2
# @brief Determine if TuxML project's content is located in a mechanical disk
# @return False if the disk is a SSD, True if the disk is a regular HDD.
# @todo Will the kernel will always be compiled in the same disk where tuxml scripts are located?
def __is_mechanical_disk():
    disk = psutil.disk_partitions()[0][0].split("/")[2]
    disk = ''.join(i for i in disk if not i.isdigit())
    if os.path.exists("/sys/block/{}/queue/rotational".format(disk)):
        with open("/sys/block/{}/queue/rotational".format(disk)) \
                as disk_type_descriptor:
            return bool(disk_type_descriptor.read(1))
    else:
        return False


## __get_ram_size
# @author PICARD Michaël
# @version 1
# @brief Retrieve the ram size in kB
# @return a string corresponding to the size of the ram, in kB
def __get_ram_size():
    # The result is in Byte, so we divide by 1024 (2^10) in order to get it in
    # kB.
    return psutil.virtual_memory().total//1024


## __get_cpu_freq()
# @author PICARD Michaël
# @version 1
# @brief Retrieve and return the current frequencies of the 1st cpu
def __get_cpu_freq():
    # But for computation power, we have a problem : with cpuinfo, we get the
    # actual computation power used right now, but this value change over time!
    # It will probably be wiser to get the min and the max value?
    frequencies = psutil.cpu_freq()
    return int(frequencies.current)


## __get_cpu_name()
# @author PICARD Michaël
# @version 2
# @brief Retrieve and return the brand name of the cpu
# @raises EnvironmentError if the cpu model name hasn't been retrieved
def __get_cpu_name():
    with open('/proc/cpuinfo') as cpuinfo:
        for line in cpuinfo:
            if line.startswith('model name'):
                return line.split(':')[1].strip()
        raise EnvironmentError("No cpu model name has been retrieved!")


## __get_hardware_details()
# @author LE FLEM Erwan, PICARD Michaël
# @version 2
def __get_hardware_details():
    hw = {
        "cpu": __get_cpu_name(),
        "cpu_freq": __get_cpu_freq(),
        "ram": __get_ram_size(),
        "arch": platform.machine(),
        "cpu_cores": os.cpu_count(),
        "mechanical_drive": __is_mechanical_disk()
    }

    return hw


## get_environment_details
# @author LEBRETON Mickaël, PICARD Michaël
# @version 2
def get_environment_details():
    env = {
        "system": __get_system_details(),
        "hardware": __get_hardware_details(),
        "compilation": ""
    }

    return env


## print_environment_details
# @author LEBRETON Mickaël, PICARD Michaël
# @version 2
# @brief Using the print_method, pretty_print the environment details.
def print_environment_details(environment_details, print_method=print):
    for primary_key in environment_details:
        print_method("    ==> {}".format(primary_key), flush=True)
        for secondary_key in environment_details[primary_key]:
            print_method(
                "      --> {}: {}".format(
                    secondary_key,
                    environment_details[primary_key][secondary_key]
                ), flush=True)


if __name__ == "__main__":
    print_environment_details(get_environment_details())
