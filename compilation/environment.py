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
        "distribution_version": platform.linux_distribution()[1],
        "os_kernel_version": platform.release()
    }
    return system


## __get_type_of_disk
# @author LE FLEM Erwan, MERZOUK Fahim, PICARD Michaël
# @version 2
# @return 0 if the disk is a SSD, 1 if the disk is a regular HDD.
# @todo Will the kernel will always be compiled in the same disk where tuxml scripts are located?
def __get_type_of_disk():
    disk = psutil.disk_partitions()[0][0].split("/")[2]
    disk = ''.join(i for i in disk if not i.isdigit())
    try:
        result = subprocess.check_output(
            ["cat", "/sys/block/{}/queue/rotational".format(disk)],
            universal_newlines=True)
    except subprocess.CalledProcessError:
        return '-1'
    return result.split('\n')[0].strip()


## __get_hardware_details()
# @author LE FLEM Erwan, PICARD Michaël
# @version 2
def __get_hardware_details():
    # Ugly code but :
    # -> Do we have a cleaner way to get model name and computation power of our
    # cpu?
    # For the name of our processor, it's enough, but other solution exist :
    # (https://www.binarytides.com/linux-cpu-information/
    # https://www.poftut.com/get-cpu-info-number-cpus-linux/)
    # But for computation power, we have a problem : with cpuinfo, we get the
    # actual computation power used right now, but this value change over time!
    # It will probably be wiser to get the min and the max value?
    # -> Same question for ram size?
    with open('/proc/cpuinfo') as f:
        for line in f:
            if line.strip():
                if line.rstrip('\n').startswith('model name'):
                    cpu_name = line.rstrip('\n').split(':')[1].strip()
                if line.rstrip('\n').startswith('cpu MHz'):
                    cpu_freq = line.rstrip('\n').split(':')[1]
                    cpu_freq = cpu_freq.split('.')[0].strip()

        with open('/proc/meminfo') as f:
            for line in f:
                if line.strip():
                    if line.rstrip('\n').startswith('MemTotal'):
                        # Le deuxième strip élimite l'unité 'kB' de la chaîne
                        memory = line.rstrip('\n').split(
                            ':')[1].strip().split(' ')[0]

    hw = {
        "cpu": cpu_name,
        "cpu_freq": cpu_freq,
        "ram": memory,
        "arch": platform.machine(),
        "cpu_cores": str(os.cpu_count()),
        "mechanical_drive": __get_type_of_disk()
    }

    return hw


## get_environment_details
# @author LEBRETON Mickaël
def get_environment_details():
    env = {
        "system": __get_system_details(),
        "hardware": __get_hardware_details(),
        "compilation": ""
    }

    return env
