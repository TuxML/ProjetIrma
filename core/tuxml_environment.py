#!/usr/bin/python3

import os
import subprocess
import multiprocessing
import platform
import csv
import tuxml_settings as tset
import tuxml_common as tcom


# tuxml_environment  is  a basic  utilitary to retreieve informations  about the
# local machine, like the distribution, the kernel version or CPU info...

# TODO pretty printer pour les dicos


# author : LE FLEM Erwan
#
# retrieve informations about the operating system and return those in a form of
# a dictionary (with string both for keys and values).
#
# For example, print(get_os_details()["kernel"]) will display the kernel version.
#
# The keys of the returned dictionary are :
#   - os The name of the System, e.g Linux.
#   - distribution The specific distribution e.g Debian, Arch, and so on...
#   - version The version of the distribution, currently  it only  return an empty
#     string.
#   - kernel the version of the kernel
#
# return value :
#   system The dictionary
def get_os_details():
    system = {
        "os": os.uname().sysname,
        "distribution": platform.linux_distribution()[0],
        "distrib_version": platform.linux_distribution()[1],
        "kernel": os.uname().release
    }
    return system


def __get_partition():
        path = os.path.dirname(os.path.abspath( __file__ ))
        result = subprocess.check_output(["stat", "--format=%m", path], universal_newlines=True)
        return result.split('\n')[0].strip()


def __get_mount_point():
        #spaces near {} are here to handle the case where the partition where tuxml is used is \
        result = subprocess.check_output(["cat /proc/mounts | grep \" {} \" ".format(__get_partition())],
        shell=True, universal_newlines=True)
        return result.split(' ')[0].strip()


def __get_type_of_disk():
    #TODO Will kernel will always be compiled in the same disk where tuxml script are located?
    disk = __get_mount_point().translate({ord(k): None for k in ("0","1","2","3","4","5","6","7","8","9")})
    if disk.strip() == "overlay" or disk == "overlay2":
        disk = overlay_to_partition()
    disk = disk.split("/")[2]
    disk = ''.join(i for i in disk if not i.isdigit())
    result = subprocess.check_output(["cat", "/sys/block/{}/queue/rotational".format(disk)], universal_newlines=True)
    return result.split('\n')[0].strip()


# author : LE FLEM Erwan
#
# retrieve  informations  about  the  hardware and  return those in a  form of a
# dictionary (with string both for keys and values).
# For example, print(get_hardware_details()["cpu"]) will display the CPU's name.
#
# The keys of the returned dictionary are :
# - cpu The name of the CPU. Can include the frequency in Ghz but not always.
# - cpu_freq The frequency of the CPU in MHz.
# - ram the total quantity of Random Access Memory in the system.
# - arch The architecture of the CPU, e.g x86_64
# - cpu_cores The number of  physical cores. Those  are the  physical cores, the
#   virtual ones (i.e hyperthreading) are not counted.
# - disk_type The type of disk where tuxml scripts are located :
#   0 for a non mecanical drive (e.g SSD)
#   1 for a classical mecanical hard disk.
#
# Note that disk_type is currently not reliable on RAID disk.
# Note that the CPU cores here is the number of available cores, NOT the number
# of core actually used during the kernel compilation.
#
# return value :
#   hw The dictionary
def get_hardware_details():
    # TODO refactoring with smaller function
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


# TODO enlever la parenthèse à la fin
def __get_libc_version():
        result = subprocess.check_output(["ldd", "--version"], universal_newlines=True)
        return result.strip().split(' ')[3].split('\n')[0].split(')')[0]


# TODO enlever la parenthèse à la fin
def __get_gcc_version():
        result = subprocess.check_output(["gcc", "--version"], universal_newlines=True)
        return result.strip().split(' ')[2].split('\n')[0].split(')')[0]


def __get_tuxml_version():
        path = os.path.dirname(os.path.abspath( __file__ ))
        result = subprocess.check_output([path + "/tuxml.py", "-V"], universal_newlines=True)
        return result.split('.py')[1].split('\n')[0].strip()


# author : LE FLEM Erwan
#
# retrieve informations about the compilation environment.
#
# For  example,  print(get_compilation_details["gcc_version"])  will display the
# installed version of gcc.
#
# The keys of the returned dictionary are :
# - tuxml_version TuxML version.
# - libc_version The libs version used.
# - gcc_version The installed version of gcc.
# - core_used The number of cores actually used during the compilation process.
# - incremental_mod True if TuxML didn't erase files from previous compilations.
#
# return value :
#   comp The dictionary
def get_compilation_details():
    brim = ["", ""]
    try:
        with open(tset.CONF_FILE, "r") as conf_file:
            i = 0
            for line in conf_file:
                brim[i] = line.split("=")[1][1:-1] #format : OPTION=value
                i += 1
    except EnvironmentError:
        tcom.pprint(1, "Unable to find {}".format(tset.CONF_FILE))

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



# author : LE FLEM Erwan
#
# Export the environment detail in a csvfile.
#
# The export file is tuxml_environment.csv and is stored in the  directory where
# you are when executing this script.
def export_as_csv(os_details, hw_details, comp_details):
    with open('tuxml_environment.csv', 'w', newline='') as csvfile:
        # merged_dict = {**hw_details, **os_details, **comp_details}
        merged_dict = hw_details.copy()
        merged_dict.update(os_details)
        merged_dict.update(comp_details)
        writer = csv.DictWriter(csvfile, merged_dict.keys())
        writer.writeheader()
        writer.writerow(merged_dict)


# author : LEBRETON Mickaël
#
# Display all the environment's details
def environment_pprinter(env_details):
    for dico in env_details:
        print(tset.GRAY + " " * 4 + "==> "+ dico)
        for key in env_details[dico]:
            print(tset.GRAY + " " * 6 + "--> " + key + ": " + env_details[dico][key])

# author : LEBRETON Mickaël
#
# Get all the environment's details thanks to the getters, print them and return
# the result as a dictionnary.
#
# The keys are :
#   - system Result of the system getter function
#   - hardware Result of the hardware getter function
#   - compilation Result of the compilation getter function
#
# return value :
#   env The dictionary
def get_environment_details():
    tcom.pprint(2, "Getting environment details")
    env = {
        "system": get_os_details(),
        "hardware": get_hardware_details(),
        "compilation": get_compilation_details()
    }

    if tset.VERBOSE > 1:
        environment_pprinter(env)

    # TODO changer ça car c'est très moche :
    export_as_csv(env["system"], env["hardware"], env["compilation"])

    return env


def overlay_to_partition():
    inode = subprocess.check_output(["df -i | grep overlay | awk '{print $3}' "], shell=True, universal_newlines=True).strip()
    result = subprocess.check_output(["df -i | grep {} |grep  -v overlay | awk '{{print $1}}'".format(inode)], shell=True, universal_newlines=True)
    return result.split('\n')[0].strip()


# Test code (temp)
def main():
    env = get_environment_details()

# ============================================================================ #


if __name__ == '__main__':
    main()
