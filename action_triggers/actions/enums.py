"""Enums specific to Action Trigger action."""

from enum import Enum


class ActionType(Enum):
    """Represents the types of actions supported by the application."""

    AWS_LAMBDA = "aws_lambda"