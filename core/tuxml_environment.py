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
# - os The name of the System, e.g Linux.
# - distribution The specific distribution e.g Debian, Arch, and so on...
# - version The version of the distribution, currently  it only  return an empty
#   string.
# - kernel the version of the kernel
def get_os_details():
    system = {
        "os": os.uname().sysname,
        "distribution": platform.linux_distribution()[0],
        "distrib_version": platform.linux_distribution()[1],
        "kernel": os.uname().release
    }
    return system


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
#
# Note that the CPU cores here is the number of available cores, NOT  the number
# core actually used during the kernel compilation.
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
        "cpu_cores": multiprocessing.cpu_count()
    }

    return hw


def __get_libc_version():
        result = subprocess.run(["ldd", "--version"], stdout=subprocess.PIPE, universal_newlines=True).stdout
        return result.strip().split(' ')[3].split('\n')[0]


def __get_gcc_version():
        result = subprocess.run(["gcc", "--version"], stdout=subprocess.PIPE, universal_newlines=True).stdout
        return result.strip().split(' ')[2].split('\n')[0]


def __get_tuxml_version():
        path = os.path.dirname(os.path.abspath( __file__ ))
        result = subprocess.run([path + "/tuxml.py", "-V"], stdout=subprocess.PIPE, universal_newlines=True).stdout
        return result.split('.py')[1].split('\n')[0].strip()


# author : LE FLEM Erwan
#
# retrieve informations about the compilation environment.
#
# For  example,  print(get_compilation_details["gcc_version"])  will display the
# installed version of gcc.
#
# The keys of the returned dictionary are :
# - tuxml_version La version de tuxml.
# - libc_version The libs version used.
# - gcc_version The installed version of gcc.
# - core_used The number of cores actually used during the compilation process.
def get_compilation_details():
    env = {
        "tuxml_version": __get_tuxml_version(),
        "libc_version": __get_libc_version(),
        "gcc_version": __get_gcc_version(),
        "core_used": tset.NB_CORES
    }
    return env


# author : LE FLEM Erwan
#
# Export the environment detail in a csvfile.
#
# The export file is tuxml_environment.csv and is stored in the  directory where
# you are when executing this script.
def export_as_csv(os_details, hw_details, comp_details):
    with open('tuxml_environment.csv', 'w', newline='') as csvfile:
        merged_dict = {**hw_details, **os_details, **comp_details}
        writer = csv.DictWriter(csvfile, merged_dict.keys())
        writer.writeheader()
        writer.writerow(merged_dict)


# author : LEBRETON Mickaël
#
# Return all the environment details as a triplet.
def get_environment_details():
    tcom.pprint(2, "Getting environment details")
    os   = get_os_details()
    hw   = get_hardware_details()
    comp = get_compilation_details()

    # TODO pretty pretting
    if tset.VERBOSE > 0:
        print(os)
        print(hw)
        print(comp)

    export_as_csv(os, hw, comp)
    return os, hw, comp


# Code de test (temporaire).
def main():
    os, hw, comp = get_environment_details()
    print(os)
    print(hw)
    print(comp)
    export_as_csv(os, hw, comp)


# ============================================================================ #


if __name__ == '__main__':
    main()
