"""Module contains descriptors relating to the storing of error messages for
later use.
"""

import typing as _t
from collections import defaultdict


class ErrorField:
    """Descriptor for storing error messages for a field."""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(
        self,
        instance: object,
        owner: type,
    ) -> _t.Union[dict, "ErrorField"]:
        if instance is None:
            return self

        # Ensure instance-specific storage for errors
        if self.name not in instance.__dict__:
            instance.__dict__[self.name] = defaultdict(list)
        return instance.__dict__[self.name]

    def add_error(self, instance: object, key: str, message: str) -> None:
        """Adds an error for the field.

        :param instance: The instance of the class.
        :param key: The key for the error.
        :param message: The error message.
        """

        errors = _t.cast(
            _t.Dict[str, _t.List[str]],
            self.__get__(instance, type(instance)),
        )
        errors[key].append(message)
