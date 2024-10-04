"""Contains the error class for generic message broker errors relating to the
connection and parameters.
"""

from action_triggers.base.error import ErrorBase
from action_triggers.descriptors.error import ErrorField
from action_triggers.exceptions import ConnectionValidationError


class MessageBrokerError(ErrorBase):
    """A class for storing errors for a message broker."""

    error_class = ConnectionValidationError

    connection_params = ErrorField()
    params = ErrorField()
