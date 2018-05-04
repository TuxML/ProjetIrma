#!/usr/bin/python3

# -*- coding: utf-8 -*-

#   Copyright 2018 TuxML Team
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


## @file tuxml_environment.py
#  @author LE FLEM Erwan
#  @author LEBRETON Mickaël
#  @copyright Apache License 2.0
#  @brief tuxml_environment  is  a basic  utilitary to retreieve informations
#  about the local machine, like the distribution, the kernel version or CPU info...
#  @details get_environment_details() is the main useful fonction of this file and
#  return a dict where the key is what class of details we want to obtains (system,
#  harware, os), the second key is which specific detail.
#
#  Examples of usage :
#  @code
#  env = get_environment_details()
#  env["os"]["distribution"] # e.g Debian
#  env["hardware"]["cpu"] # e.g Debian
#  env["harware"]["cpu_freq"] " e.g 2800 (for 2.8 Ghz)
#  env["compilation"]["gcc_version"] # e.g 7.2.2
#  @endcode
#  The list of every possible keys and what they correspond to is described in the
#  documentation of the following methods:
#  get_environment_details(), get_hardware_details(), get_os_details(), and
#  get_compilation_details().
#
#  @copyright Apache License, Version 2.0


import os
import subprocess
import multiprocessing
import platform
import csv
import tuxml_settings as tset
import tuxml_common as tcom
import psutil


## @author LE FLEM Erwan
#
#  @brief retrieve informations about the operating system and return those in a
#  form of a dictionary (with string both for keys and values).
#
#  @details For example, print(get_os_details()["kernel"]) will display the kernel
#  version.
#  The keys of the returned dictionary are :
#    - os The name of the System, e.g Linux.
#    - distribution The specific distribution e.g Debian, Arch, and so on...
#    - version The version of the distribution, currently  it only  return an empty
#      string.
#    - kernel the version of the kernel
#
#  @returns A dictionary with the keys listed above
def get_os_details():
    system = {
        "os": os.uname().sysname,
        "distribution": platform.linux_distribution()[0],
        "distrib_version": platform.linux_distribution()[1],
        "kernel": os.uname().release
    }
    return system


## @author LE FLEM Erwan
#
#  @brief retrieve the mount point of the partition where TUXML is located.
#  @details We use the stat command to find the mount point, with this file's name as argument.
#  We assume that all files of TUXML are located on the same partition.
#
#  @return The mount point from where this file (hence tuxml), is located, e.g /,
#  /mnt/myMountPoint, etc.
def __get_mount_point():
        path = os.path.dirname(os.path.abspath( __file__ ))
        result = subprocess.check_output(["stat", "--format=%m", path], universal_newlines=True)
        return result.split('\n')[0].strip()


## @author LE FLEM Erwan
#
#  @brief retrieve the partition where TUXML is located.
#  @details We use /proc/mounts to find this partition, by checking the line
#  containing the mount point retieved by  __get_mount_point().
#  We assume that all files of TUXML are located on the same partition.
#
#  @return The partion where this file (hence tuxml), is located, e.g /dev/sda1,
#  /dev/sdb2, etc.
def __get_partition():
        #spaces near {} are here to handle the case where the partition where tuxml is used is \
        result = subprocess.check_output(["cat /proc/mounts | grep \" {} \" ".format(__get_mount_point())],
        shell=True, universal_newlines=True)
        return result.split(' ')[0].strip()


## @author LE FLEM Erwan, MERZOUK Fahim
#
#  @brief Retrieve the type of disk where TUXML is located.
#  @details On a docker, container this method can be uncertain because of docker virtual filesystem.
#
#  @return 0 if the disk is a SSD, 1 if the disk is a regular harddisk.
#
#  @bug This method currently do not work properly if using LVM logical volumes.
#  @todo Will the kernel will always be compiled in the same disk where tuxml scripts are located?
#  __get_partition().translate(...) allows to only keep the disk not the partition, as
#  /sys/block/{}/queue/rotational need the disk in the path.
#  (e.g sda2 will become sda)
def __get_type_of_disk():
    disk = __get_partition().translate({ord(k): None for k in ("0","1","2","3","4","5","6","7","8","9")})
    if disk.strip() == "overlay" or disk == "overlay2":
        disk = overlay_to_partition()
    elif len(disk.split("/")) < 2 or "mapper" in disk:
        disk = __get_disk_docker()
    else:
        disk = disk.split("/")[2]
    disk = ''.join(i for i in disk if not i.isdigit())

    try:
        result = subprocess.check_output(["cat", "/sys/block/{}/queue/rotational".format(disk)], universal_newlines=True)
        return result.split('\n')[0].strip()
    except subprocess.CalledProcessError:
        disk = __get_disk_docker()
        disk = ''.join(i for i in disk if not i.isdigit())
        result = subprocess.check_output(["cat", "/sys/block/{}/queue/rotational".format(disk)], universal_newlines=True)
        return result.split('\n')[0].strip()


## @author LE FLEM Erwan
#  @author MERZOUK Fahim
#
#  @brief Return the first physical disk (e.g. sda) found, we assume it is the
#  only one visible as the container is stored on one disk
def __get_disk_docker():
    return psutil.disk_partitions()[0][0].split("/")[2]


## @author LE FLEM Erwan
#
#  @brief Retrieve informations  about the  hardware and  return those in a  form
#  of a dictionary (with string both for keys and values).
#
#  @details For example, print(get_hardware_details()["cpu"]) will display the CPU's name.
#  The keys of the returned dictionary are :
#  - cpu The name of the CPU. Can include the frequency in Ghz but not always.
#  - cpu_freq The frequency of the CPU in MHz.
#  - ram the total quantity of Random Access Memory in the system.
#  - arch The architecture of the CPU, e.g x86_64
#  - cpu_cores The number of  physical cores. Those  are the  physical cores, the
#    virtual ones (i.e hyperthreading) are not counted.
#  - disk_type The type of disk where tuxml scripts are located :
#    0 for a non mecanical drive (e.g SSD)
#    1 for a classical mecanical hard disk.
#
#
# @return A dictionary with the keys listed above
#
# @bug disk_type is currently not reliable on RAID disk.
# @warning Note that the CPU cores here is the number of available cores, NOT the number
# of core actually used during the kernel compilation.
# @todo refactoring with smaller function
def get_hardware_details():
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
                        memory = line.rstrip('\n').split(':')[1].strip().split(' ')[0]

    hw = {
        "cpu": cpu_name,
        "cpu_freq": cpu_freq,
        "ram": memory,
        "arch": os.uname().machine,
        "cpu_cores": str(multiprocessing.cpu_count()),
        "mechanical_drive": __get_type_of_disk()
    }

    return hw


## @author LE FLEM Erwan
#
#  @brief Retrieve the version of the libc on this machine.
#  @details We retrieve the libc version using ldd and grep.
#
#  @retuns The libc version e.g 2.27
def __get_libc_version():
        result = subprocess.check_output(["ldd", "--version"], universal_newlines=True)
        return result.strip().split(' ')[3].split('\n')[0].split(')')[0]


## @author LE FLEM Erwan
#
#  @brief Retrieve the version of the gcc compiler on this machine.
#
#  @returns The gcc version, e.g 7.3.1
def __get_gcc_version():
        result = subprocess.check_output(["gcc", "--version"], universal_newlines=True)
        return result.strip().split(' ')[2].split('\n')[0].split(')')[0]


## @author LE FLEM Erwan
#
#  @brief Retrieve the version of TuxML
#
#  @returns The TuxML version, e.g pre-alpha v0.2
def __get_tuxml_version():
        path = os.path.dirname(os.path.abspath( __file__ ))
        result = subprocess.check_output([path + "/tuxml.py", "-V"], universal_newlines=True)
        return result.split('.py')[1].split('\n')[0].strip()


## @author LE FLEM Erwan
#  @author LEBRETON Mickaël
#  @brief Retrieve informations about the compilation environment.
#
#  @details For example, print(get_compilation_details["gcc_version"]) will display
#  the installed version of gcc.
#
#  The keys of the returned dictionary are :
#    - tuxml_version TuxML version.
#    - libc_version The libs version used.
#    - gcc_version The installed version of gcc.
#    - core_used The number of cores actually used during the compilation process.
#    - incremental_mod True if TuxML didn't erase files from previous compilations.
#
#  @return A dictionary with the keys listed above
def get_compilation_details():
    brim = ["", ""]
    try:
        with open(tset.CONF_FILE, "r") as conf_file:
            i = 0
            for line in conf_file:
                brim[i] = line.split("=")[1][1:-1] #format : OPTION=value
                i += 1
    except EnvironmentError:
        tcom.pprint(4, "Unable to find {}".format(tset.CONF_FILE))

    comp = {
        "tuxml_version": __get_tuxml_version(),
        "libc_version": __get_libc_version(),
        "gcc_version": __get_gcc_version(),
        "core_used": str(tset.NB_CORES),
        "incremental_mod": str(tset.INCREMENTAL_MOD),
        "git_branch": brim[0],
        "docker_image": brim[1]
    }
    return comp


## @author LE FLEM Erwan
#
#  @brief Export the environment detail in a csvfile.
#
#  @details The export file is tuxml_environment.csv and is stored in the directory
#  where you are when executing this script.
#
#  @param os_details  The dictionnary returned by get_os_details()
#  @param hw_details  The dictionnary returned by get_hardware_details()
#  @param comp_details The dictionnary returned by get_compilation_details()
def export_as_csv(os_details, hw_details, comp_details):
    with open('tuxml_environment.csv', 'w', newline='') as csvfile:
        # merged_dict = {**hw_details, **os_details, **comp_details}
        merged_dict = hw_details.copy()
        merged_dict.update(os_details)
        merged_dict.update(comp_details)
        writer = csv.DictWriter(csvfile, merged_dict.keys())
        writer.writeheader()
        writer.writerow(merged_dict)


## @author LEBRETON Mickaël
#
#  @brief Display all the environment's details
#  @details Display system, hardware and compilation details
#
#  @param env_details The environment dictionnary is the merged dictionnary
#  between os, hardware and compilation dictionnaries
def environment_pprinter(env_details):
    for dico in env_details:
        print(" " * 4 + "==> "+ dico)
        for key in env_details[dico]:
            print(" " * 6 + "--> " + key + ": " + env_details[dico][key])


## @author LEBRETON Mickaël
#
#  @brief Get all the environment's details thanks to the getters, print them,
#  export the .csv and return the result as a dictionnary.
#
#  @details The keys are :
#    - system Result of the system getter function
#    - hardware Result of the hardware getter function
#    - compilation Result of the compilation getter function
#
#  @return A dictionary with the keys listed above
def get_environment_details():
    tcom.pprint(2, "Getting environment details")
    env = {
        "system": get_os_details(),
        "hardware": get_hardware_details(),
        "compilation": get_compilation_details()
    }

    if tset.VERBOSE > 1:
        environment_pprinter(env)

    export_as_csv(env["system"], env["hardware"], env["compilation"])

    return env


## @author LE FLEM Erwan
#
#  @brief Find the actual partition where tuxml is instead of overlay
#  @details Docker use virtual partition "overlay", but seeking the type of disk
#  by using cat /sys/block/overlay/queue/rotational will fail as we need the actual
#  physical disk in the path, e.g /sys/block/sda/queue/rotational.
#  This method try to find the actual partition where tuxml is instead of overlay.
def overlay_to_partition():
    inode = subprocess.check_output(["df -i | grep overlay | awk '{print $3}' "], shell=True, universal_newlines=True).strip()
    result = subprocess.check_output(["df -i | grep {} |grep  -v overlay | awk '{{print $1}}'".format(inode)], shell=True, universal_newlines=True)
    return result.split('\n')[0].strip()


# ============================================================================ #


if __name__ == '__main__':
    env = get_environment_details()
    print(env)
