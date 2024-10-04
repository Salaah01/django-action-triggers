"""Base module containing the logic for handling of bespoke error classes.
Note: An error class is different from an `Exception` class. An `Exception`
class is for handling exceptions and they can be raised. This module contains
what are fundamentally classes for storing and managing error messages.
"""

import typing as _t

from action_triggers.descriptors.error import ErrorField


class MetaError(type):
    """A metaclass for the `Error` class. This metaclass generates and
    attaches methods to aid in adding errors to the fields of the class.
    """

    def __new__(cls, name, bases, dct):
        fields = {
            key: value
            for key, value in dct.items()
            if isinstance(value, ErrorField)
        }

        for field_name in fields:
            dct[f"add_{field_name}_error"] = cls.make_add_error(field_name)

        dct["_fields"] = fields

        return super().__new__(cls, name, bases, dct)

    @staticmethod
    def make_add_error(
        field_name: str,
    ) -> _t.Callable[[_t.Any, str, str], None]:
        """Generate a method for adding an error to a field.

        :param field_name: The name of the field to add the error to.
        :return: A method for adding an error to a field.
        """

        def add_error_wrapper(
            self: "ErrorBase",
            key: str,
            message: str,
        ) -> None:
            getattr(self.__class__, field_name).add_error(
                self,
                key,
                message,
            )

        return add_error_wrapper


class ErrorBase(metaclass=MetaError):
    """A base class for storing errors for a set of fields. For each field, an
    error can be added using the `add_<field_name>_error` method.

    :param error_class: The associated Exception class to raise when there are
        errors. (default: Exception)

    Example:
    --------

    .. code-block:: python

        class MyError(ErrorBase):
            field_1 = ErrorField()
            field_2 = ErrorField()

        error = MyError()
        error.add_field_1_error("key_1", "message_1")
        error.add_field_1_error("key_1", "message_2")
        error.add_field_2_error("key_2", "message_3")

        error.as_dict()

    # Output:

    .. code-block:: python

        {
            "field_1": {
                "key_1": ["message_1", "message_2"]
            },
            "field_2": {
                "key_2": ["message_3"]
            }
        }
    """

    _fields: _t.Dict[str, ErrorField]
    error_class: _t.Type[Exception] = Exception

    def as_dict(self) -> _t.Dict[str, _t.Dict[str, _t.List[str]]]:
        """Convert the errors to a dictionary.

        :return: The errors as a dictionary.
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
