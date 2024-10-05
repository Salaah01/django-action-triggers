"""Base module for handling the configuration for a given Action Trigger.

Note: This is not used in the current implementation. It is a work in progress
and a placeholder for future work.
"""

import typing as _t
from abc import ABC, abstractproperty, abstractmethod

from action_triggers.config_required_fields import RequiredFieldBase
from action_triggers.base.error import ErrorBase


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
    def error_class(self) -> ErrorBase:
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
        # self.validate()
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

    # def validate(self):
    #     """Validate the connection details and parameters provided by the
    #     user.
    #     """

    #     self.validator(self).validate()
