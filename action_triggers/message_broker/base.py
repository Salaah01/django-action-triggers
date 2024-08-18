import typing as _t
from abc import ABC, abstractmethod

from django.conf import settings

from action_triggers.dynamic_loading import replace_dict_values_with_results
from action_triggers.message_broker.error import Error


class ConnectionBase(ABC):
    """Base class for establishing a connection to a message broker.

    :param conn_details: The connection parameters to use for establishing the
        connection.
    """

    def __init__(self, conn_details: dict, params: dict):
        self.conn_details = conn_details
        self.params = params
        self._errors = Error()
        self.validate()
        self._conn: _t.Any = None

    @abstractmethod
    def validate(self) -> None:
        """Validate the connection parameters. Raise an exception if
        invalid.
        """

    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the message broker."""

    def close(self) -> None:
        """Close the connection to the message broker."""
        if self._conn:
            self._conn.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class BrokerBase(ABC):
    """Base class for a message broker. This class should be subclassed
    to implement the specific message broker.

    :param conn_details: The connection parameters to use for establishing the
        connection.
    :param params: Additional parameters to use for the message broker.
    :param kwargs: Additional keyword arguments to pass to the subclass.
    """

    conn_class: _t.Type[ConnectionBase]

    def __init__(
        self,
        broker_key: str,
        conn_details: _t.Union[dict, None],
        params: _t.Union[dict, None],
        **kwargs,
    ):
        self.broker_key = broker_key
        self.config = settings.ACTION_TRIGGERS["brokers"][broker_key]
        self.conn_details = replace_dict_values_with_results(
            {
                **(_t.cast(dict, self.config["conn_details"]) or {}),
                **(conn_details or {}),
            }
        )
        self.params = replace_dict_values_with_results(
            {
                **(_t.cast(dict, self.config["params"]) or {}),
                **(params or {}),
            }
        )
        self.kwargs = kwargs
        self._conn = self.conn_class(self.conn_details, self.params)

    def send_message(self, message: str) -> None:
        """Starts a connection with the message broker and sends a message.

        :param message: The message to send to the message broker.
        """

        with self._conn as conn:
            self._send_message_impl(conn, message)

    @abstractmethod
    def _send_message_impl(self, conn: _t.Any, message: str) -> None:
        """Implementation of sending a message to the message broken given an
        established connection.

        :param conn: The established connection to the message broker.
        :param message: The message to send to the message broker.
        """
