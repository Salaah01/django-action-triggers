import pytest
from django.conf import settings

try:
    import boto3
except ImportError:
    boto3 = None  # type: ignore[assignment]
