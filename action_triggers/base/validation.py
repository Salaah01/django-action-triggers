"""Module containing logic for handling the validation."""

import typing as _t

T_Validators = _t.Sequence[_t.Callable[[_t.Any], _t.Any]]


class ConfigValidationMeta(type):
    """Metaclass for `ConfigValidationBase`. The metaclass checks that the
    class has been setup correctly. Specifically, it will check to ensure that
    either `validators` vis not `None` or the `get_validators` method has been
    overwritten.

    Technically, this can be done without the use of a metaclass and can be
    done when the method is executed. However, we want to alert the user right
    when they implement the class rather than waiting for them to actually
    execute the code.
    """

    def __new__(cls, name, bases, dct):
        if name == "ConfigValidationBase":
            return super().__new__(cls, name, bases, dct)

        if (
            dct.get("validators") is not None
            or dct.get("get_validators") is not None
        ):
            return super().__new__(cls, name, bases, dct)

        raise TypeError(
            "Either `validators` must be set or `get_validators` must be "
            "implemented."
        )


class ConfigValidationBase(metaclass=ConfigValidationMeta):
    """Handles teh validation of the configuration (from
    `settings.ACTION_TRIGGERS`).
    """

    # TODO: How do we handle error messages?
    # Does it need to be provided with the error object?
    # Perhaps it just returns the error message and the user needs to map the
    # validator to some field and key?
    validators: _t.Optional[T_Validators] = None
    get_validators: _t.Optional[_t.Callable[[], T_Validators]]

    def validate(self):
        pass
