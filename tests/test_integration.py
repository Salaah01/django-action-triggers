"""Integration tests."""

from model_bakery import baker

from action_triggers.registry import add_to_registry
from tests.models import CustomerModel
from tests.utils import get_rabbitmq_conn


class TestSignalIntegrationMessageBroker:
    """Integration tests pertaining for the message broker triggers."""

    def test_simple_basic_json_message(
        self,
        customer_rabbitmq_post_save_signal,
    ):
        add_to_registry(CustomerModel)
        baker.make(CustomerModel)

        with get_rabbitmq_conn() as conn:
            channel = conn.channel()
            method_frame, header_frame, body = channel.basic_get(
                queue="test_queue_1",
                auto_ack=True,
            )

            assert body == b'{"message": "Hello, World!"}'

    def test_simple_basic_plain_message(
        self,
        customer_rabbitmq_post_save_signal,
    ):
        config = customer_rabbitmq_post_save_signal.config
        config.payload = "Hello World!"
        config.save()

        add_to_registry(CustomerModel)
        baker.make(CustomerModel)

        with get_rabbitmq_conn() as conn:
            channel = conn.channel()
            method_frame, header_frame, body = channel.basic_get(
                queue="test_queue_1",
                auto_ack=True,
            )

            assert body.decode() == '"Hello World!"'
