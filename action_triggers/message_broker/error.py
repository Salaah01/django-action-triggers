from collections import defaultdict
import json
from action_triggers.message_broker.exceptions import ConnectionValidationError


class Error:
    def __init__(self):
        self._errors = {
            "connection_params": defaultdict(list),
            "params": defaultdict(list),
        }

    def add_connection_error(self, key: str, message: str) -> None:
        self._errors["connection_params"][key].append(message)

    def add_param_error(self, key: str, message: str) -> None:
        self._errors["params"][key].append(message)

    def as_json(self) -> str:
        return json.dumps(self._errors)

    def is_valid(self, raise_exception: bool = False) -> bool:
        is_valid = not any(self._errors.values())
        if not is_valid and raise_exception:
            raise ConnectionValidationError(self.as_json())
        return is_valid
