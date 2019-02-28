# @file configuration.py
# @author PICARD Michaël

import os
import compilation.settings as settings


def __get_kernel_version_and_path():
    with open(settings.KERNEL_VERSION_FILE, "r") as version_file:
        kernel_version = version_file.read().strip()
        kernel_path = "/TuxML/linux-{}".format(kernel_version)
        return kernel_version, kernel_path


def __get_cpu_cores_to_use(nb_cpu_core):
    max_nb_core = os.cpu_count()
    if nb_cpu_core <= 0:
        return max_nb_core
    else:
        return min(nb_cpu_core, max_nb_core)


def create_configuration(args):
    kernel_version, kernel_path = __get_kernel_version_and_path()
    configuration = {
        "core_used": __get_cpu_cores_to_use(int(args.cpu_cores)),
        "incremental_mod": args.incremental != 0,
        "kernel_version_compilation": kernel_version,
        "kernel_path": kernel_path
    }
    return configuration


def print_configuration(configuration, print_method=print):
    for primary_key in configuration:
        print_method("    --> {}: {}".format(
            primary_key, configuration[primary_key]))
