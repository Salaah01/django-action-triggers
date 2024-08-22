"""Utility functions for managing imports."""

import importlib


class MissingImportWrapper:
    """A wrapper to indicate that an import is missing the next time it is
    accessed. Judging from the code, that is not at all the case. However, this
    is primary used whenever a module is not found, but we do not want to raise
    an exception immediately. Instead, we want to raise an exception when the
    module is accessed.
    """

    def __init__(
        self,
        import_path: str,
    ):
        self.import_path = import_path

    def __getattr__(self, item):
        importlib.import_module(self.import_path)[item]
