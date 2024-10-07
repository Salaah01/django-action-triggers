import pytest

from action_triggers.exceptions import ConnectionValidationError
from action_triggers.message_broker.gcp_pubsub import (
    GCPPubSubConnection,
    GCPPubSubBroker,
)
from tests.utils.gcp.pubsub import CONN_DETAILS, can_connect_to_pubsub

try:
    from google.cloud import pubsub_v1
except ImportError:
    pubsub_v1 = None  # type: ignore[assignment]


@pytest.mark.skipif(
    not can_connect_to_pubsub(),
    reason="GCP Pub/Sub is not available.",
)
class TestGCPPubSubConnection:
    """Tests for the `GCPPubSubConnection` class."""

    def test_raise_exception_if_no_project_found(self):
        with pytest.raises(ConnectionValidationError):
            GCPPubSubConnection(
                config={},
                conn_details={"topic": "test_topic"},
                params={},
            )

    def test_raises_exception_if_no_topic_found(self):
        with pytest.raises(ConnectionValidationError):
            GCPPubSubConnection(
                config={},
                conn_details={"project": "test_project"},
                params={},
            )

    def test_passes_when_project_and_topic_exist(self):
        GCPPubSubConnection(
            config={},
            conn_details=CONN_DETAILS,
            params={},
        )

    @pytest.mark.asyncio
    async def test_connection_and_close_mechanism_using_conn_details(
        self,
    ):
        conn = GCPPubSubConnection(
            config={},
            conn_details=CONN_DETAILS,
            params={},
        )
        await conn.connect()
        assert conn.conn is not None
        assert conn.topic_path is not None
        await conn.close()
        assert conn.conn is None
        assert conn.topic_path is None


@pytest.mark.skipif(
    not can_connect_to_pubsub(),
    reason="GCP Pub/Sub is not available.",
)
class TestGCPPubSubBroker:
    """Tests for the `GCPPubSubBroker` class."""

    @pytest.mark.asyncio
    async def test_send_message(self, gcp_pubsub_topic_refresh):
        broker = GCPPubSubBroker(
            key="gcp_pubsub_test_topic",
            conn_details={},
            params={},
        )
        await broker.send_message("test_message")
