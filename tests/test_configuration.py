from pytest import raises
from unittest import TestCase  #Usefull when testing classes
from os import cpu_count

import compilation.configuration as configuration


def test_create_configuration_basic_use_case():
    config = configuration.create_configuration()
    assert(config['core_used'] == cpu_count())
    assert(not config['incremental_mod'])


def test_create_configuration_with_cpu_core_negative():
    config = configuration.create_configuration(nb_cpu_cores=-1000000)
    assert (config['core_used'] == cpu_count())


def test_create_configuration_with_cpu_core_over_the_max():
    config = configuration.create_configuration(nb_cpu_cores=1000000)
    assert (config['core_used'] == cpu_count())


def test_create_configuration_with_incremental_mod_true():
    conf = configuration.create_configuration(incremental_mod=True)
    assert(conf['incremental_mod'])


def test_create_configuration_with_one_cpu():
    conf = configuration.create_configuration(nb_cpu_cores=1)
    assert(conf['core_used'] == 1)


def test_print_environment_details():
    configuration.print_configuration(configuration.create_configuration())
