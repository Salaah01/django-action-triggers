"""This module contains the base class for handing errors in the application.
It provides the building blocks for creating error classes that can be used
to store errors for specific fields.
"""

import typing as _t
from collections import defaultdict


class ErrorField:
    """A class for storing errors for a specific field.

    :param field_name: The name of the field.
    """

    def __init__(self, field_name):
        self.field_name = field_name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        # Ensure instance-specific storage for errors
        if self.field_name not in instance.__dict__:
            instance.__dict__[self.field_name] = defaultdict(list)
        return instance.__dict__[self.field_name]

    def add_error(self, instance, key: str, message: str) -> None:
        """Adds an error for the field.

        :param instance: The instance of the class.
        :param key: The key for the error.
        :param message: The error message.
        """

        errors = self.__get__(instance, type(instance))
        errors[key].append(message)


class MetaError(type):
    """A metaclass for the Error class. This metaclass automatically generates
    methods for adding errors to the fields of the `Error` class.
    """

    def __new__(cls, name, bases, dct):
        fields = {
            key: value
            for key, value in dct.items()
            if isinstance(value, ErrorField)
        }

        # Generate add_error methods for each field
        def make_add_error(field_name):
            def add_error_wrapper(self, key: str, message: str):
                getattr(self.__class__, field_name).add_error(
                    self,
                    key,
                    message,
                )

            return add_error_wrapper

        for field_name in fields:
            dct[f"add_{field_name}_error"] = make_add_error(field_name)

        dct["_fields"] = fields

        return super().__new__(cls, name, bases, dct)


class ErrorBase(metaclass=MetaError):
    """A base class for storing errors for a set of fields. For each field, an
    error can be added using the `add_<field_name>_error` method.


    :param error_class: The class of the error to raise when the error is not
        valid.

    Example:
    --------

    .. code-block:: python

        class MyError(ErrorBase):
            field_1 = ErrorField("field_1")
            field_2 = ErrorField("field_2")

        error = MyError()
        error.add_field_1_error("key_1", "message_1")
        error.add_field_1_error("key_1", "message_2")
        error.add_field_2_error("key_2", "message_3")

        error.as_dict()
        # {
        #     "field_1": {"key_1": ["message_1", "message_2"]},
        #     "field_2": {"key_2": ["message_3"]},
        # }

        # Raises an exception if the error is not valid.
        error.is_valid(raise_exception=True)

    """

    _fields: _t.Dict[str, ErrorField]
    error_class: _t.Type[Exception] = Exception

    def as_dict(self) -> dict:
        """Return the error message as a dictionary.

        :return: A dictionary containing the errors.
        """

        return {
            field_name: dict(getattr(self, field_name))
            for field_name in self._fields.keys()
        }

    def is_valid(self, raise_exception: bool = False) -> bool:
        """Check if the error is valid.

        :param raise_exception: Whether to raise an exception if
            `raise_exception` is `True` and there are errors.
        :return: True if the error is valid, False otherwise.
        """

        has_error = any(error for error in self.as_dict().values())

        if has_error and raise_exception:
            raise self.error_class(self.as_dict())

        return not has_error
