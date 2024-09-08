from abc import ABC, abstractmethod, abstractproperty
import typing as _t


class RequiredFieldBase(ABC):
    """Represents a required field for the connection details and parameters
    that must be provided by the user.
    """

    def __init__(self, field: str, *args, **kwargs) -> None:
        self.field = field
        self.args = args
        self.kwargs = kwargs
        self._validate_init_params()

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


class HasField(RequiredFieldBase):
    """Represents a required field that must be present in the context."""

    def check(self, context: dict) -> bool:
        """Check if the field is present in the context.

        :param context: The context to check.
        :return: True if the field is present, False otherwise.
        """

        return all(field in context.keys() for field in self.fields)

    @property
    def error_msg(self) -> str:
        """The error message to display if the field is not present."""

        return f"The field {self.field} must be provided."


class HasAtLeastOneOffField(RequiredFieldBase):
    """Represents a required field that requires at least one of the fields to
    be present in the context.
    """

    def _validate_init_params(self) -> None:
        if self.field:
            raise ValueError(
                "`field` parameter not supported for this class. Use "
                "`fields` keyword argument instead."
            )

        self.fields = self.kwargs.get("fields")
        if not self.fields or not isinstance(self.fields, _t.Sequence):
            raise ValueError(
                "`fields` keyword argument must be a non-empty sequence."
            )

    def check(self, context: dict) -> bool:
        """Check if at least one of the fields is present in the context.

        :param context: The context to check.
        :return: True if at least one of the fields is present,
            False otherwise.
        """

        return set(self.fields).intersection(context.keys())

    @property
    def error_msg(self) -> str:
        """The error message to display if at least one of the fields is not
        present.
        """

        return f"At least one of the fields {self.fields} must be provided."
