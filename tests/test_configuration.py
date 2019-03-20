from pytest import raises
from unittest import TestCase  #Usefull when testing classes

import compilation.configuration as configuration


def test_create_configuration():
    # We test if we have any throw, which should never happen
    configuration.create_configuration(0, False)
    configuration.create_configuration(-1000000, False)
    configuration.create_configuration(1000000, False)


def test_print_environment_details():
    configuration.print_configuration(
        configuration.create_configuration(0, False))
