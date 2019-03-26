# @file configuration.py
# @author PICARD Michaël

import os
import compilation.settings as settings


## __get_kernel_version_and_path
# @author PICARD Michaël
# @version 2
def __get_kernel_version_and_path():
    with open(settings.KERNEL_VERSION_FILE, "r") as version_file:
        kernel_version = version_file.read().strip()
        kernel_path = "/TuxML/linux-{}".format(kernel_version)
        return kernel_version, kernel_path


## __get_cpu_cores_to_use
# @author PICARD Michaël
# @version 1
# @brief Return the number of cpu to use when compiling.
# @details If the nb_cpu_core is negative, null or bigger than the number of
# available cpu_core, the return's value is the number of available cpu_core.
def __get_cpu_cores_to_use(nb_cpu_core=0):
    max_nb_core = os.cpu_count()
    if nb_cpu_core <= 0:
        return max_nb_core
    else:
        return min(nb_cpu_core, max_nb_core)


## create_configuration
# @author PICARD Michaël
# @version 1
# @brief Return a dictionary about some setting made by the user.
def create_configuration(nb_cpu_cores=0, incremental_mod=False):
    kernel_version, kernel_path = __get_kernel_version_and_path()
    configuration = {
        "core_used": __get_cpu_cores_to_use(nb_cpu_cores),
        "incremental_mod": incremental_mod,
        "kernel_version_compilation": kernel_version,
        "kernel_path": kernel_path
    }
    return configuration


## print_configuration
# @author PICARD Michaël
# @version 1
# @brief Using the print_method, pretty print the environment details.
# @todo It's in a simple state. It can be improve to have a more stable output.
def print_configuration(configuration, print_method=print):
    for primary_key in configuration:
        print_method("    --> {}: {}".format(
            primary_key, configuration[primary_key]))
