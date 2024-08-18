"""Integration tests."""

from unittest.mock import patch
from model_bakery import baker

from action_triggers.registry import add_to_registry
from tests.models import CustomerModel
from tests.utils import get_rabbitmq_conn


class TestIntegrationMessageBrokerRabbitMQ:
    """Integration tests where the action to be triggered is sending a payload
    to a RabbitMQ message broker.
    """

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


class TestIntegrationMessageBrokerKafka:
    """Integration tests where the action to be triggered is sending a payload
    to a Kafka message broker.
    """

    # TODO: Using actual Kafka broker is not working. Need to investigate why.

    @patch(
        "action_triggers.message_broker.kafka.KafkaBroker._send_message_impl",
        autospec=True,
    )
    def test_simple_basic_json_message(
        self,
        mock_send_message_impl,
        customer_kafka_post_save_signal,
    ):
        add_to_registry(CustomerModel)
        baker.make(CustomerModel)
        mock_send_message_impl.assert_called_once()
