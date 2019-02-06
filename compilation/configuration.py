# @file configuration.py
# @author PICARD Michaël


def create_configuration(args):
    configuration = {

    }
    return configuration


def print_configuration(configuration, print_method=print):
    for primary_key in configuration:
        print_method("    --> {}: {}".format(
            primary_key, configuration[primary_key]))
