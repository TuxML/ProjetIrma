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


# Development part : have to be removed
if __name__ == "__main__":
    print(__get_system_details())
