"""Base module for handling the configuration for a given Action Trigger"""

from abc import ABC, abstractproperty
import typing as _t

from action_triggers.base.validation import ConfigValidationBase


class ConfigBase(ABC):
    @abstractproperty
    def required_fields(self) -> _t.List[str]:
        pass

    @abstractproperty
    def validator(self) -> ConfigValidationBase:
        pass
