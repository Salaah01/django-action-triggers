"""Base module for handling the configuration for a given Action Trigger.

Note: This is not used in the current implementation. It is a work in progress
and a placeholder for future work.
"""

from abc import ABC, abstractproperty  # pragma: no cover
import typing as _t  # pragma: no cover

from action_triggers.base.validation import (  # pragma: no cover
    ConfigValidationBase,
)


class ConfigBase(ABC):  # pragma: no cover
    @abstractproperty
    def required_fields(self) -> _t.List[str]:
        pass

    @abstractproperty
    def validator(self) -> ConfigValidationBase:
        pass
