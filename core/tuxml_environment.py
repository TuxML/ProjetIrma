#!/usr/bin/python3

import os
import sys
import subprocess
import re
import shutil
import multiprocessing
import platform

#tuxml_environment is a basic utilitary to retreieve informations about the local machine,
#like the distribution, the kernel version or CPU info...

# authors : LE FLEM Erwan
# retrieve informations about the operating system and return those in a form of a dictionary (with string both for keys and values).
#
# For example, print(get_hardware()["kernel"]) will display the kernel version.
#
# The keys of the returned dictionary are :
# - os The name of the System, e.g Linux.
# - distribution The specific distribution e.g Debian, Arch, and so on...
# - version The version of the distribution, currently it only return an empty string.
# - kernel the version of the kernel
def get_os_detail():
    system = {
        "os": os.uname().sysname,
        "distribution": platform.linux_distribution()[0],
        "version": "",
        "kernel": os.uname().release
    }
    return system

# authors : LE FLEM Erwan
# retrieve informations about the hardware and return those in a form of a dictionary (with string both for keys and values).
#
# For example, print(get_hardware()["cpu"]) will display the CPU's name.
#
# The keys of the returned dictionary are :
# - cpu The name of the CPU. Can include the frequency in Ghz but not always.
# - cpu_freq The frequency of the CPU in MHz.
# - ram the total quantity of Random Access Memory in the system.
# - arch The architecture of the CPU, e.g x86_64
# - cpu_cores The number of physical cores. Those are the physical cores, the virtual ones (i.e hyperthreading) are not counted.
def get_hardware():

    #TODO refactoring with smaller function
    with open('/proc/cpuinfo') as f:
        for line in f:
            if line.strip():
                if line.rstrip('\n').startswith('model name'):
                    cpu_name = line.rstrip('\n').split(':')[1]
                if line.rstrip('\n').startswith('cpu MHz'):
                    cpu_freq = line.rstrip('\n').split(':')[1]
                    cpu_freq = cpu_freq.split('.')[0]

        with open('/proc/meminfo') as f:
            for line in f:
                if line.strip():
                    if line.rstrip('\n').startswith('MemTotal'):
                        #Le deuxième strip élimite l'unité 'kB' de la chaîne
                        memory = line.rstrip('\n').split(':')[1].strip().split(' ')[0]

    hw = {
        "cpu": cpu_name,
        "cpu_freq": cpu_freq,
        "ram": memory,
        "arch": os.uname().machine,
        "cpu_cores": multiprocessing.cpu_count()
    }

    return hw

#
# TODO
#
def compilation_details():
    env = {
        "version": platform.libc_ver()[1]
    }

    return env


#Temporaires, affichage pour tester.
dico = get_os_detail()
print(dico)
print(get_hardware())
print(compilation_details())
