from pytest import raises
from unittest import TestCase  #Usefull when testing classes

import compilation.configuration as configuration


class DummyArgs:
    def __init__(self, cpu_cores):
        self.cpu_cores = cpu_cores


def test_create_configuration():
    # We test if we have any throw, which should never happen
    configuration.create_configuration(DummyArgs(0))
    configuration.create_configuration(DummyArgs(-1000000))
    configuration.create_configuration(DummyArgs(1000000))


def test_print_environment_details():
    configuration.print_configuration(
        configuration.create_configuration(DummyArgs(0)))
