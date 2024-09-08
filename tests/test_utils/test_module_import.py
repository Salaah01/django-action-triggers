"""Tests for the `utils.module_import` module."""

import importlib
import os

import pytest

from action_triggers.utils.module_import import MissingImportWrapper


class TestMissingImportWrapper:
    """Tests for the `MissingImportWrapper` class."""

    def test_can_be_initialised_with_an_installed_package(self):
        inst = MissingImportWrapper("os")
        assert inst.import_path == "os"
        assert importlib.import_module(inst.import_path) is os

    def test_can_be_initialised_with_a_missing_package(self):
        inst = MissingImportWrapper("missing_package")
        assert inst.import_path == "missing_package"
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(inst.import_path)

    def test_get_attr_returns_the_attribute(self):
        inst = MissingImportWrapper("os")
        assert inst.path is os.path

    def test_get_attr_raises_an_exception_if_the_module_is_missing(self):
        inst = MissingImportWrapper("missing_package")
        with pytest.raises(ModuleNotFoundError):
            inst.path
