"""Validation to support with the validation of the configuration."""

import typing as _t

from action_triggers.base.validation import ConfigValidationBase
from action_triggers.config_required_fields import RequiredFieldBase


def validate_required_keys(
    required_fields: _t.Sequence[RequiredFieldBase],
    context: _t.Dict[str, _t.Any],
    error_handler: _t.Callable[[str, str], None],
) -> None:
    """Validate that the required keys are present in the provided context.

    :param required_fields: The required fields to check.
    :param context: The context to check.
    :param error_handler: The function to call if the required fields are not
    """

    for field in required_fields:
        if not field.check(context):
            error_handler(field.key_repr, field.error_msg)


def validate_context_not_overwritten(
    context: _t.Dict[str, _t.Any],
    user_context: _t.Dict[str, _t.Any],
    error_handler: _t.Callable[[str, str], None],
) -> None:
    """Validate that the context is not overwritten.

    :param context: The context to check.
    :param user_context: The user context to check.
    :param error_handler: The function to call if the required fields are not
    """

    for key, value in context.items():
        if key in user_context and user_context[key] != value:
            error_handler(key, f"{key} cannot be overwritten.")


class ConnectionValidationCore(ConfigValidationBase):
    """The core validation class for the configuration. This class should
    cover the basic validation requirements for any connection.
    """

    def get_validators(
        self,
    ) -> _t.Sequence[
        _t.Tuple[_t.Callable[[_t.Any], _t.Any], _t.Dict[str, str]]
    ]:
        """Get the validators for the configuration."""
        return [
            (
                validate_required_keys,
                {
                    "required_fields": self.instance.required_conn_detail_fields,
                    "context": self.instance.conn_details,
                },
            ),
        ]
