import json


class ConnectionValidationError(RuntimeError):
    """Exception raised when connection parameters are invalid."""

    def __init__(self, message: dict):
        super().__init__(message)

    def as_dict(self) -> dict:
        """Return the error message as a dictionary."""
        return dict(self.args[0])

    def as_json(self) -> str:
        """Return the error message as a JSON string."""
        return json.dumps(self.as_dict())
