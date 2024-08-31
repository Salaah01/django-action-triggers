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

    def __init__(self, config: dict, conn_details: dict, params: dict):
        self.config = config
        self.conn_details = conn_details
        self.params = params
        self._errors = Error()
        self.validate()
        self.conn: _t.Any = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def validate(self) -> None:
        """Validate the connection parameters. Raise an exception if
        invalid.
        """
        self.validate_connection_details_not_overwritten()
        self.validate_params_not_overwritten()
        self._errors.is_valid(raise_exception=True)

    @abstractmethod
    async def connect(self) -> None:
        """Establish a connection to the message broker."""

    @abstractmethod
    async def close(self) -> None:
        """Close the connection to the message broker."""

    def validate_connection_details_not_overwritten(self) -> None:
        """Validate that the base connection details are not overwritten."""

        conn_details_from_settings = self.config.get("conn_details")
        if not conn_details_from_settings:
            return

        for key, value in conn_details_from_settings.items():
            if key in self.conn_details and self.conn_details[key] != value:
                self._errors.add_connection_params_error(  # type: ignore[attr-defined]  # noqa: E501
                    key, f"Connection details for {key} cannot be overwritten."
                )

    def validate_params_not_overwritten(self) -> None:
        """Validate that the base parameters are not overwritten."""

        params_from_settings = self.config.get("params")
        if not params_from_settings:
            return

        for key, value in params_from_settings.items():
            if key in self.params and self.params[key] != value:
                self._errors.add_params_error(  # type: ignore[attr-defined]
                    key, f"{key} cannot be overwritten."
                )


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
        self.config = _t.cast(dict, settings.ACTION_TRIGGERS["brokers"])[
            broker_key
        ]
        self.conn_details = replace_dict_values_with_results(
            {
                **(conn_details or {}),
                **(_t.cast(dict, self.config["conn_details"]) or {}),
            }
        )
        self.params = replace_dict_values_with_results(
            {
                **(params or {}),
                **(_t.cast(dict, self.config["params"]) or {}),
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
