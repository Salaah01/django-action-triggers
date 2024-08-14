from abc import ABC, abstractmethod
import typing as _t

from django.conf import settings
from action_triggers.message_broker.enums import BrokerType
from action_triggers.message_broker.error import Error


class ConnectionBase(ABC):
    """Base class for establishing a connection to a message broker.

    Args:
        conn_params: The connection parameters to use for establishing the
            connection.
    """

    def __init__(self, conn_params: dict, params: dict):
        self.conn_params = conn_params
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
        pass

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

    Args:
        conn_params: The connection parameters to use for establishing the
            connection.
        **kwargs: Additional keyword arguments to pass to the subclass.
    """

    broker_type: BrokerType
    conn_class: _t.Type[ConnectionBase]

    def __init__(
        self,
        broker_key: str,
        conn_params: _t.Union[dict, None],
        params: _t.Union[dict, None],
        **kwargs,
    ):
        self.broker_key = broker_key
        self.config = settings.ACTION_TRIGGERS["brokers"][broker_key]
        self.conn_params = {
            **(self.config["conn_details"] or {}),
            **(conn_params or {}),
        }
        self.params = {
            **(self.config["params"] or {}),
            **(params or {}),
        }
        self.kwargs = kwargs
        self._conn = self.conn_class(self.conn_params, self.params)

    def send_message(self, message: str) -> None:
        """Starts a connection with the message broker and sends a message.

        Args:
            message: The message to send to the message

        Returns:
            None
        """

        with self._conn as conn:
            self._send_message_impl(conn, message)

    @abstractmethod
    def _send_message_impl(self, conn: _t.Any, message: str) -> None:
        """Implementation of sending a message to the message broken given an
        established connection.

        Args:
            conn: The established connection to the message broker.
            message: The message to send to the message broker.

        Returns:
            None
        """
