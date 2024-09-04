"""Contains the error class for generic message broker errors relating to the
connection and parameters.
"""

from action_triggers.error.base import ErrorBase, ErrorField
from action_triggers.message_broker.exceptions import ConnectionValidationError


class MessageBrokerError(ErrorBase):
    """A class for storing errors for a message broker."""

    error_class = ConnectionValidationError

    connection_params = ErrorField("connection_params")
    params = ErrorField("params")
