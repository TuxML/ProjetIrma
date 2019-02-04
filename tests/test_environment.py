from pytest import raises
from unittest import TestCase  #Usefull when testing classes

import compilation.environment as environment


def test_get_environment_details():
    # We test if we have any throw, which should never happen
    environment.get_environment_details()
