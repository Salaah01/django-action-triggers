from django.db.models import TextChoices


class HTTPMethodChoices(TextChoices):
    """Represents the supported HTTP methods for webhooks."""

    GET = "GET", "GET"
    POST = "POST", "POST"
    PUT = "PUT", "PUT"
    PATCH = "PATCH", "PATCH"
    DELETE = "DELETE", "DELETE"


class SignalChoices(TextChoices):
    """Represents the supported signals for action triggers."""

    PRE_SAVE = "pre_save", "Pre-save"
    POST_SAVE = "post_save", "Post-save"
    PRE_DELETE = "pre_delete", "Pre-delete"
    POST_DELETE = "post_delete", "Post-delete"
