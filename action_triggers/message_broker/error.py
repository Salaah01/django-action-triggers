from action_triggers.error.base import ErrorField, ErrorBase
from action_triggers.message_broker.exceptions import ConnectionValidationError


class MessageBrokerError(ErrorBase):
    """A class for storing errors for a message broker."""

    error_class = ConnectionValidationError

    connection_params = ErrorField("connection_params")
    params = ErrorField("params")
