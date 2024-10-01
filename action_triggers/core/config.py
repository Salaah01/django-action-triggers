from action_triggers.base.config import ConfigBase


class ConfigCore(ConfigBase):
    def validate(self):
        self.validator().validate()
