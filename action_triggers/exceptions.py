"""Module containing custom exceptions."""

import json


class DisallowedEndpointError(ValueError):
    """Exception raised when an endpoint is disallowed."""


class DisallowedWebhookEndpointError(DisallowedEndpointError):
    """Exception raised when a webhook endpoint is disallowed."""

    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Webhook endpoint '{url}' is not whitelisted.")


class ConnectionValidationError(ValueError):
    """Exception raised when connection parameters are invalid."""

    def __init__(self, message: dict):
        super().__init__(message)

    def as_dict(self) -> dict:
        """Return the error message as a dictionary."""
        return dict(self.args[0])

    def as_json(self) -> str:
        """Return the error message as a JSON string."""
        return json.dumps(self.as_dict())
