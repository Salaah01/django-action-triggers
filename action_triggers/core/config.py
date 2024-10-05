"""Note: This is not used in the current implementation. It is a work in
progress and a placeholder for future work.
"""

import typing as _t

from action_triggers.base.config import ConnectionBase
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
    context: _t.Union[_t.Dict[str, _t.Any], None],
    user_context: _t.Dict[str, _t.Any],
    error_handler: _t.Callable[[str, str], None],
) -> None:
    """Validate that the context is not overwritten.

    :param context: The context to check.
    :param user_context: The user context to check.
    :param error_handler: The function to call if the required fields are not
    """

    if context is None:
        return

    for key, value in context.items():
        if key in user_context and user_context[key] != value:
            error_handler(key, f"{key} cannot be overwritten.")


class ConnectionValidationMixin:
    """The core validation class for the configuration. This class should
    cover the basic validation requirements for any connection.
    """

    required_conn_detail_fields: _t.Sequence[RequiredFieldBase]
    required_params_fields: _t.Sequence[RequiredFieldBase]
    config: _t.Dict[str, _t.Any]
    conn_details: _t.Dict[str, _t.Any]
    params: _t.Dict[str, _t.Any]
    _user_conn_details: _t.Dict[str, _t.Any]
    _user_params: _t.Dict[str, _t.Any]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate()

    def validate(self) -> None:
        """Validate the configuration."""
        self.validate_required_conn_details()
        self.validate_required_params()
        self.validate_connection_details_not_overwritten()
        self.validate_params_not_overwritten()

        self._errors.is_valid(raise_exception=True)  # type: ignore[attr-defined]  # noqa: E501

    def validate_connection_details_not_overwritten(self) -> None:
        """Validate that the base connection details are not overwritten."""

        validate_context_not_overwritten(
            self.config.get("conn_details"),
            self._user_conn_details,
            self._errors.add_connection_params_error,  # type: ignore[attr-defined]  # noqa: E501
        )

    def validate_params_not_overwritten(self) -> None:
        """Validate that the base parameters are not overwritten."""

        validate_context_not_overwritten(
            self.config.get("params"),
            self._user_params,
            self._errors.add_params_error,  # type: ignore[attr-defined]
        )

    def validate_required_conn_details(self) -> None:
        """Validate that the required connection details are present."""
        validate_required_keys(
            self.required_conn_detail_fields,
            self.conn_details,
            self._errors.add_connection_params_error,  # type: ignore[attr-defined]  # noqa: E501
        )

    def validate_required_params(self) -> None:
        """Validate that the required parameters are present."""
        validate_required_keys(
            self.required_params_fields,
            self.params,
            self._errors.add_params_error,  # type: ignore[attr-defined]
        )


class ConnectionCore(ConnectionValidationMixin, ConnectionBase):
    """The core connection class with some common validation that should be
    applied to all connections.
    """
