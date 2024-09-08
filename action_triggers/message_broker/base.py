import typing as _t
from abc import ABC, abstractmethod, abstractproperty

from django.conf import settings

from action_triggers.config_required_fields import RequiredFieldBase
from action_triggers.dynamic_loading import replace_dict_values_with_results
from action_triggers.message_broker.error import MessageBrokerError


# TODO: The following class seems to hav two responsibilities. It should be
# split into two classes: one for managing the config details and the other
# for validating the connection details and parameters.
class ConnectionBase(ABC):
    """Base class for establishing a connection to a message broker. This class
    provides the capability to marry the configuration provided in the settings
    with the connection details and parameters provided by the user. However,
    this enforces a one-sided relationship where the user cannot overwrite
    the base configuration as defined in the settings as the base configuration
    always takes precedence.

    :param config: The configuration for the message broker as defined in
        `settings.ACTION_TRIGGERS["brokers"]`.
    :param conn_details: Additional connection parameters to use for
        establishing the connection provided by the user.
    :param params: Additional parameters to use for the message broker provided
        by the user.
    """

    @abstractproperty
    def required_conn_detail_fields(self) -> _t.Sequence[RequiredFieldBase]:
        """The required connection detail fields that must be provided by the
        user.
        """

    @abstractproperty
    def required_params_fields(self) -> _t.Sequence[RequiredFieldBase]:
        """The required parameters fields that must be provided by the user."""

    def __init__(self, config: dict, conn_details: dict, params: dict):
        self.config = config
        self._user_conn_details = conn_details
        self._user_params = params

        self._conn_details: _t.Optional[dict] = None
        self._parmas: _t.Optional[dict] = None

        self._errors = MessageBrokerError()
        self.validate()
        self.conn: _t.Any = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @property
    def conn_details(self) -> dict:
        """Lazy load the the merged connection details. When merging the
        connection details, the user provided base connection details take
        precedence over the base configuration.

        :return: The merged connection details.
        """

        if self._conn_details is None:
            self._conn_details = {
                **self.config.get("conn_details", {}),
                **self._user_conn_details,
            }
        return self._conn_details

    @property
    def params(self) -> dict:
        """Lazy load the the merged parameters. When merging the parameters,
        the user provided base parameters take precedence over the base
        configuration.

        :return: The merged parameters.
        """

        if self._parmas is None:
            self._parmas = {
                **self.config.get("params", {}),
                **self._user_params,
            }
        return self._parmas

    def validate(self) -> None:
        """Validate the connection parameters. Raise an exception if
        invalid.
        """
        self.validate_connection_details_not_overwritten()
        self.validate_params_not_overwritten()
        self.validate_required_conn_details()
        self.validate_required_params()
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
            if (
                key in self._user_conn_details
                and self._user_conn_details[key] != value
            ):
                self._errors.add_connection_params_error(  # type: ignore[attr-defined]  # noqa: E501
                    key, f"Connection details for {key} cannot be overwritten."
                )

    def validate_params_not_overwritten(self) -> None:
        """Validate that the base parameters are not overwritten."""

        params_from_settings = self.config.get("params")
        if not params_from_settings:
            return

        for key, value in params_from_settings.items():
            if key in self._user_params and self._user_params[key] != value:
                self._errors.add_params_error(  # type: ignore[attr-defined]
                    key, f"{key} cannot be overwritten."
                )

    @staticmethod
    def validate_required_keys(
        required_fields: _t.Sequence[RequiredFieldBase],
        settings_context: _t.Dict[str, _t.Any],
        err_fn: _t.Callable[[str, str], None],
    ) -> None:
        """Validate that the required keys are present in the connection
        details and parameters.

        :param required_fields: The required fields to check.
        :param settings_context: The context to check.
        :param err_fn: The function to call if the required fields are not
        """

        for field in required_fields:
            if not field.check(settings_context):
                err_fn(field.key_repr, field.error_msg)

    def validate_required_conn_details(self) -> None:
        """Validate that the required connection details are present."""
        self.validate_required_keys(
            self.required_conn_detail_fields,
            self.conn_details,
            self._errors.add_connection_params_error,  # type: ignore[attr-defined]  # noqa: E501
        )

    def validate_required_params(self) -> None:
        """Validate that the required parameters are present."""
        self.validate_required_keys(
            self.required_params_fields,
            self.params,
            self._errors.add_params_error,  # type: ignore[attr-defined]
        )


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
