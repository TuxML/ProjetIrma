## @file tuxml_environment.py
# @author LE FLEM Erwan, LEBRETON Mickaël, PICARD Michaël
# @version 2
# @brief python3 methods to get data about compilation environment
# @details This file contains method to get data about compilation environment :
# - system :
#   + os
#   + distribution
#   + distrib_version
#   + kernel => os_kernel_version
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
#   + tuxml_version
# - others :
#   + core_used ? Should be the same as the number of core that the machine got,
#       so we make a duplicate here?
#   + branch ? empty, so not needed? docker_image useless also?
#   + incremental_mod ? shouldn't be in the environnement details, isn't it?

import platform
import os
import psutil
import subprocess

from compilation.settings import TUXML_VERSION


## _get_system_details
# @author LE FLEM Erwan, PICARD Michaël
# @version 2
# @brief Returns a dictionary containing system details
def __get_system_details():
    system = {
        "system_kernel": platform.system(),
        "linux_distribution": platform.linux_distribution()[0],
        "linux_distribution_version": platform.linux_distribution()[1],
        "system_kernel_version": platform.release()
    }
    return system


## __is_mechanical_disk
# @author LE FLEM Erwan, MERZOUK Fahim, THOMAS Luis, PICARD Michaël
# @version 3
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


## __get_max_cpu_freq()
# @author PICARD Michaël
# @version 3
# @brief Retrieve and return the max frequencies of the 1st cpu, in MHz
def __get_max_cpu_freq():
    cpu_info_max_freq = "/sys/devices/system/cpu/cpufreq/policy0/cpuinfo_max_freq"
    if os.path.exists(cpu_info_max_freq):
        with open(cpu_info_max_freq) as cpu_max_freq:
            return int(cpu_max_freq.read().strip())/1000
    else:
        with open("/proc/cpuinfo") as cpuinfo:
            for line in cpuinfo:
                if line.startswith('cpu MHz'):
                    return int(line.split(':')[1].strip())
    raise EnvironmentError("No cpu max frequencies has been retrieved!")


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
        "cpu_brand_name": __get_cpu_name(),
        "cpu_max_frequency": __get_max_cpu_freq(),
        "ram_size": __get_ram_size(),
        "architecture": platform.machine(),
        "number_cpu_core": os.cpu_count(),
        "mechanical_disk": __is_mechanical_disk()
    }
    return hw


## __get_libc_version
# @author LE FLEM Erwan, PICARD Michaël
# @version 2
# @brief Retrieve the version of the libc on this machine.
def __get_libc_version():
    return subprocess.check_output(
        "ldd --version",
        universal_newlines=True,
        shell=True
    ).split(" ")[3][:-1]


## __get_gcc_version
# @author LE FLEM Erwan, PICARD Michaël
# @version 2
# @brief Retrieve the version of the gcc compiler on this machine.
def __get_gcc_version():
        return subprocess.check_output(
            "gcc --version",
            universal_newlines=True,
            shell=True
        ).split(" ")[2][:-1]


def __get_software_details():
    software = {
        "tuxml_version": TUXML_VERSION,
        "libc_version": __get_libc_version(),
        "gcc_version": __get_gcc_version(),
    }
    software.update(__get_system_details())
    return software


## get_environment_details
# @author LEBRETON Mickaël, PICARD Michaël
# @version 2
def get_environment_details():
    env = {
        "hardware": __get_hardware_details(),
        "software": __get_software_details()
    }

    return env


## print_environment_details
# @author LEBRETON Mickaël, PICARD Michaël
# @version 2
# @brief Using the print_method, pretty_print the environment details.
def print_environment_details(environment_details, print_method=print):
    for primary_key in environment_details:
        print_method("    ==> {}".format(primary_key))
        for secondary_key in environment_details[primary_key]:
            print_method(
                "      --> {}: {}".format(
                    secondary_key,
                    environment_details[primary_key][secondary_key]
                ))
