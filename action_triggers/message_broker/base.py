import typing as _t
from abc import ABC, abstractmethod, abstractproperty

from django.conf import settings

from action_triggers.base.config import ConnectionBase
from action_triggers.dynamic_loading import replace_dict_values_with_results


class BrokerBase(ABC):
    """Base class for a message broker. This class should be subclassed
    to implement the specific message broker.

    :param conn_details: The connection parameters to use for establishing the
        connection.
    :param params: Additional parameters to use for the message broker.
    :param kwargs: Additional keyword arguments to pass to the subclass.
    """

    @abstractproperty
    def conn_class(self) -> _t.Type[ConnectionBase]:
        """The connection class to use for establishing a connection to the
        message broker.
        """

    def __init__(
        self,
        broker_key: str,
        conn_details: _t.Union[dict, None],
        params: _t.Union[dict, None],
        **kwargs,
    ):
        self.broker_key = broker_key
        self.config = _t.cast(dict, settings.ACTION_TRIGGERS["brokers"])[
            broker_key
        ]
        self.conn_details = replace_dict_values_with_results(
            {
                **(conn_details or {}),
                **(_t.cast(dict, self.config.get("conn_details")) or {}),
            }
        )
        self.params = replace_dict_values_with_results(
            {
                **(params or {}),
                **(_t.cast(dict, self.config.get("params")) or {}),
            }
        )
        self.kwargs = kwargs
        self._conn = self.conn_class(
            self.config,
            self.conn_details,
            self.params,
        )

    async def send_message(self, message: str) -> None:
        """Starts a connection with the message broker and sends a message.

        :param message: The message to send to the message broker.
        """

        async with self._conn as conn:
            await self._send_message_impl(conn, message)

    @abstractmethod
    async def _send_message_impl(self, conn: _t.Any, message: str) -> None:
        """Implementation of sending a message to the message broken given an
        established connection.

        :param conn: The established connection to the message broker.
        :param message: The message to send to the message broker.
        """
