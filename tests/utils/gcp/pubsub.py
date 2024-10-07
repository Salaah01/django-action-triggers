from functools import lru_cache

from django.conf import settings

try:
    from google.cloud import pubsub_v1  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    pubsub_v1 = None


CONFIG = settings.ACTION_TRIGGERS["brokers"]["gcp_pubsub_test_topic"]  # type: ignore[index]  # noqa E501
CONN_DETAILS = CONFIG["conn_details"]  # type: ignore[index]


@lru_cache
def can_connect_to_pubsub() -> bool:
    """Check if the service can connect to GCP Pub/Sub.

    :return: True if the service can connect to GCP Pub/Sub, False otherwise
    """

    try:
        publisher = pubsub_v1.PublisherClient()
        publisher.topic_path(**CONN_DETAILS)
        return True
    except Exception:
        return False


def create_topic(project_id: str, topic_id: str) -> None:
    """Create a topic in GCP Pub/Sub.

    :param project_id: The ID of the project.
    :param topic_id: The ID of the topic.
    :return: None
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    publisher.create_topic(request={"name": topic_path})
