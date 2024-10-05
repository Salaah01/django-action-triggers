"""Base module for handling the configuration for a given Action Trigger.

Note: This is not used in the current implementation. It is a work in progress
and a placeholder for future work.
"""

import typing as _t
from abc import ABC, abstractmethod, abstractproperty

from django.conf import settings

from action_triggers.base.error import ErrorBase
from action_triggers.config_required_fields import RequiredFieldBase
from action_triggers.dynamic_loading import replace_dict_values_with_results
from action_triggers.enums import ActionTriggerType


class ConnectionBase(ABC):
    """Base class for establishing a connection. This class provides the
    capability to marry the configuration provided in the settings with the
    connection details and parameters provided by the user. However, this
    enforces a one-sided relationship where the user cannot overwrite the base
    configuration as defined in the settings as the base configuration always
    takes precedence.

    :param config: The configuration as defined in `settings.ACTION_TRIGGERS`
        for a given action trigger type.
    :param conn_details: Additional connection parameters to use for
        establishing the connection provided by the user.
    :param params: Additional parameters to use for the action trigger provided
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

    @abstractproperty
    def error_class(self) -> _t.Type[ErrorBase]:
        """The error class to use for storing errors."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish a connection to the message broker."""

    @abstractmethod
    async def close(self) -> None:
        """Close the connection to the message broker."""

    def __init__(self, config: dict, conn_details: dict, params: dict):
        self.config = config
        self._user_conn_details = conn_details
        self._user_params = params

        self._conn_details: _t.Optional[dict] = None
        self._params: _t.Optional[dict] = None

        self._errors = self.error_class()
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

        if self._params is None:
            self._params = {
                **self.config.get("params", {}),
                **self._user_params,
            }
        return self._params


class ActionTriggerActionBase(ABC):
    """Base class for triggering an action. This class should be subclassed to
    implement the specific action for an action trigger.

    :param key: The key for the action trigger (must exist in the
        `settings.ACTION_TRIGGERS[self.action_trigger_type]` dictionary).
    :param conn_details: The connection parameters to use for establishing the
        connection.
    :param params: Additional parameters to use for the action trigger.
    :param kwargs: Additional keyword arguments to pass to the subclass.
    """

    @abstractproperty
    def action_trigger_type(self) -> ActionTriggerType:
        """The type of action trigger."""

    @abstractproperty
    def conn_class(self) -> _t.Type[ConnectionBase]:
        """The connection class to use for establishing a connection to the
        service which the action will interact with.
        """

    def __init__(
        self,
        key: str,
        conn_details: _t.Union[dict, None],
        params: _t.Union[dict, None],
        **kwargs,
    ):
        self.key = key
        self.config = _t.cast(
            dict, settings.ACTION_TRIGGERS[self.action_trigger_type.value]
        )[key]
        self.conn_details = self._build_and_merge_config(
            conn_details,
            self.config.get("conn_details"),
        )
        self.params = self._build_and_merge_config(
            params,
            self.config.get("params"),
        )
        self.kwargs = kwargs
        self._conn = self.conn_class(
            self.config,
            self.conn_details,
            self.params,
        )

    def _build_and_merge_config(
        self,
        user_config: _t.Union[dict, None],
        base_config: _t.Union[dict, None],
    ) -> dict:
        """Builds and merges the user provided configuration with the base
        configuration. The building process involves computing certain values
        in the merged configuration.
        Note: The base configuration always takes precedence over the user
        provided configuration.

        :param user_config: The user provided configuration.
        :param base_config: The base configuration.
        :return: The merged configuration.
        """

        return replace_dict_values_with_results(
            {
                **(user_config or {}),
                **(base_config or {}),
            }
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
