from collections import defaultdict

from action_triggers.message_broker.exceptions import ConnectionValidationError


class ErrorField:
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


class Error(metaclass=MetaError):
    connection_params = ErrorField("connection_params")
    params = ErrorField("params")

    def as_dict(self) -> dict:
        """Return the error message as a dictionary.

        Returns:
            A dictionary containing the errors.
        """

        return {
            field_name: dict(getattr(self, field_name))
            for field_name in self._fields.keys()
        }

    def is_valid(self, raise_exception: bool = False) -> bool:
        """Check if the error is valid.

        Returns:
            True if the error is valid, False otherwise.
        """

        has_error = any(error for error in self.as_dict().values())

        if has_error:
            if raise_exception:
                raise ConnectionValidationError(self.as_dict())

        return not has_error
