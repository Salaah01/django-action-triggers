"""Utility functions for managing imports."""

import importlib


class MissingImportWrapper:
    """A wrapper to indicate that an import is missing the next time it is
    accessed.
    """

    def __init__(
        self,
        import_path: str,
    ):
        self.import_path = import_path

    def __getattr__(self, item):
        importlib.import_module(self.import_path)[item]
