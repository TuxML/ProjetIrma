# @file configuration.py
# @author PICARD Michaël

import os


def __get_compilation_mode(tiny, config):
    if tiny:
        return "tiny config"
    elif config is not None:
        return "given config"
    else:
        return "random config"


def __get_cpu_cores_to_use(nb_cpu_core):
    max_nb_core = os.cpu_count()
    if nb_cpu_core <= 0:
        return max_nb_core
    else:
        return min(nb_cpu_core, max_nb_core)


def create_configuration(args):
    configuration = {
        "core_used": __get_cpu_cores_to_use(args.cpu_cores),
        "incremental_mod": args.incremental != 0,
        "kernel_version_compilation": "4.13.3",
        "config used": __get_compilation_mode(args.tiny, args.config)
    }
    return configuration


def print_configuration(configuration, print_method=print):
    for primary_key in configuration:
        print_method("    --> {}: {}".format(
            primary_key, configuration[primary_key]))
