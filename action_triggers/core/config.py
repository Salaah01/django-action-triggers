"""Note: This is not used in the current implementation. It is a work in
progress and a placeholder for future work.
"""

from action_triggers.base.config import ConfigBase  # pragma: no cover


class ConfigCore(ConfigBase):  # pragma: no cover
    def validate(self):
        self.validator().validate()
