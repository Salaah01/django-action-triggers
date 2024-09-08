"""Provides classes to represent required fields for key/value pairs that must
be presenting in the `settings.ACTION_TRIGGERS` dictionary for a given action.
"""

import typing as _t
from abc import ABC, abstractmethod, abstractproperty


class RequiredFieldBase(ABC):
    """Represents a required field for the connection details and parameters
    that must be provided by the user.
    """

    def __init__(self, field: str, *args, **kwargs) -> None:
        self.field = field
        self.args = args
        self.kwargs = kwargs
        self._validate_init_params()

    def __str__(self) -> str:
        return self.key_repr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.key_repr!r})"

    @abstractmethod
    def check(self, context: dict) -> bool:
        """Check if the required field is present in the context.

        :param context: The context to check.
        :return: True if the field is present, False otherwise.
        """

    @abstractproperty
    def error_msg(self) -> str:
        """The error message to display if the required field is not
        present.
        """

    def _validate_init_params(self) -> None:
        """Validate the initialization parameters.

        :raises ValueError: If there is an issue with the initialisation
            parameters.
        """

    @property
    def key_repr(self) -> str:
        """The key representation of the field."""

        return self.field


class HasField(RequiredFieldBase):
    """Represents a required field that must be present in the context."""

    def check_exists(self, context: dict) -> bool:
        """Check if the field is present in the context.

        :param context: The context to check.
        :return: True if the field is present, False otherwise.
        """
        if self.field in context.keys():
            return True
        else:
            self._error_msg = f"The field '{self.field}' must be provided."
            return False

    def check_type_from_args(self, context: dict) -> bool:
        """Check if the field type is provided in the first positional
        argument, and if so, check if the field is of that type.

        :param context: The context to check.
        :return: True if the field is of the specified type, False otherwise.
        :raises ValueError: If the first positional argument is not a type.
        """

        if not self.args:
            return True

        arg_0 = self.args[0]

        if not isinstance(context[self.field], arg_0):
            self._error_msg = (
                f"The field '{self.field}' must be of type {arg_0.__name__}."
            )
            return False

        return True

    def check_type_from_kwargs(self, context: dict) -> bool:
        """Check if the field type is provided in the `type` keyword argument,
        and if so, check if the field is of that type.

        :param context: The context to check.
        :return: True if the field is of the specified type, False otherwise.
        """

        if "type" not in self.kwargs:
            return True

        arg_0 = self.kwargs["type"]
        if not isinstance(context[self.field], arg_0):
            self._error_msg = (
                f"The field '{self.field}' must be of type {arg_0.__name__}."
            )
            return False

        return True

    def check(self, context: dict) -> bool:
        """Check if the field is present in the context.

        :param context: The context to check.
        :return: True if the field is present, False otherwise.
        """

        checks = (
            self.check_exists,
            self.check_type_from_args,
            self.check_type_from_kwargs,
        )
        return all(check(context) for check in checks)

    @property
    def error_msg(self) -> str:
        """The error message to display if the field is not present."""

        return self._error_msg


class HasAtLeastOneOffField(RequiredFieldBase):
    """Represents a required field that requires at least one of the fields to
    be present in the context.
    """

    def __init__(self, field: str = "", *args, **kwargs) -> None:
        super().__init__(field, *args, **kwargs)

    def _validate_init_params(self) -> None:
        if self.field:
            raise ValueError(
                "'field' parameter not supported for this class. Use "
                "'fields' keyword argument instead."
            )

        self.fields = self.kwargs.get("fields")
        if not self.fields or not isinstance(self.fields, _t.Sequence):
            raise ValueError(
                "'fields' keyword argument must be a non-empty sequence."
            )

    def check(self, context: dict) -> bool:
        """Check if at least one of the fields is present in the context.

        :param context: The context to check.
        :return: True if at least one of the fields is present,
            False otherwise.
        """

        return bool(
            set(_t.cast(_t.Sequence, self.fields)).intersection(context.keys())
        )

    @property
    def error_msg(self) -> str:
        """The error message to display if at least one of the fields is not
        present.
        """

        return f"At least one of the fields {self.fields} must be provided."

    @property
    def key_repr(self) -> str:
        """The key representation of the field."""

        return ", ".join(_t.cast(_t.Sequence, self.fields))
