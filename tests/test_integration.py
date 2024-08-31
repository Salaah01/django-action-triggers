"""Integration tests."""

import asyncio

import pytest
from aioresponses import aioresponses
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from model_bakery import baker
from aio_pika.exceptions import QueueEmpty
from asgiref.sync import sync_to_async

from tests.models import CustomerModel
from tests.utils import (
    can_connect_to_kafka,
    can_connect_to_rabbitmq,
    get_rabbitmq_conn,
    get_kafka_consumer,
)


@pytest.mark.skipif(
    not can_connect_to_rabbitmq(),
    reason="Cannot connect to RabbitMQ",
)
class TestIntegrationMessageBrokerRabbitMQ:
    """Integration tests where the action to be triggered is sending a payload
    to a RabbitMQ message broker.
    """

    @pytest.fixture(autouse=True)
    def purge_all_messages(self):
        async def purge_messages():
            async with get_rabbitmq_conn() as conn:
                channel = await conn.channel()
                await channel.set_qos(prefetch_count=1)
                queue = await channel.declare_queue("test_queue_1")
                while True:
                    try:
                        message = await queue.get()
                        await message.ack()
                    except QueueEmpty:
                        break

        asyncio.run(purge_messages())

    @pytest.mark.asyncio
    async def test_simple_basic_json_message(
        self,
        customer_rabbitmq_post_save_signal,
        customer,
    ):
        async with get_rabbitmq_conn() as conn:
            channel = await conn.channel()
            await channel.set_qos(prefetch_count=1)
            queue = await channel.declare_queue("test_queue_1")
            message = await queue.get()
            assert message.body == b'{"message": "Hello, World!"}'

    @pytest.fixture
    def fixture_simple_basic_plain_message(
        self,
        customer_rabbitmq_post_save_signal,
    ):
        config = customer_rabbitmq_post_save_signal.config
        config.payload = "Hello World!"
        config.save()
        baker.make(CustomerModel)

    @pytest.mark.asyncio
    async def test_simple_basic_plain_message(
        self,
        fixture_simple_basic_plain_message,
    ):
        async with get_rabbitmq_conn() as conn:
            channel = await conn.channel()
            await channel.set_qos(prefetch_count=1)
            queue = await channel.declare_queue("test_queue_1")
            message = await queue.get()
            assert message.body == b'"Hello World!"'

    @pytest.fixture
    def fixture_does_not_work_for_models_that_are_not_allowed(
        self,
        customer_rabbitmq_post_save_signal,
    ):
        config = customer_rabbitmq_post_save_signal.config
        config.content_types.set([ContentType.objects.get_for_model(User)])
        config.save()
        baker.make(User)

    @pytest.mark.asyncio
    async def test_does_not_work_for_models_that_are_not_allowed(
        self,
        fixture_does_not_work_for_models_that_are_not_allowed,
    ):
        async with get_rabbitmq_conn() as conn:
            channel = await conn.channel()
            await channel.set_qos(prefetch_count=1)
            queue = await channel.declare_queue("test_queue_1")
            with pytest.raises(QueueEmpty):
                await queue.get()


@pytest.mark.skipif(
    not can_connect_to_kafka(),
    reason="Cannot connect to Kafka",
)
@pytest.mark.django_db(transaction=True)
class TestIntegrationMessageBrokerKafka:
    """Integration tests where the action to be triggered is sending a payload
    to a Kafka message broker.
    """

    @pytest.fixture(autouse=True)
    def purge_all_messages(self):
        async def purge_messages():
            async with get_kafka_consumer() as consumer:
                await consumer.getmany()

        asyncio.run(purge_messages())

    @pytest.mark.asyncio
    async def test_simple_basic_json_message(
        self,
        customer_kafka_post_save_signal,
        customer,
    ):
        async def get_next_message():
            async with get_kafka_consumer() as consumer:
                return await consumer.getone()

        consumer_task = asyncio.create_task(get_next_message())
        await sync_to_async(baker.make)(CustomerModel)
        message = await consumer_task
        assert message.value == b'{"message": "Hello, World!"}'

    @pytest.fixture
    def fixture_simple_basic_plain_message(
        self,
        customer_kafka_post_save_signal,
    ):
        config = customer_kafka_post_save_signal.config
        config.payload = "Hello World!"
        config.save()
        baker.make(CustomerModel)

    @pytest.mark.asyncio
    async def test_simple_basic_plain_message(
        self,
        fixture_simple_basic_plain_message,
    ):
        async def get_next_message():
            async with get_kafka_consumer() as consumer:
                return await consumer.getone()

        consumer_task = asyncio.create_task(get_next_message())
        await sync_to_async(baker.make)(CustomerModel)
        message = await consumer_task
        assert message.value == b'"Hello World!"'


class TestIntegrationWebhook:
    """Integration tests where the action to be triggered is sending a payload
    to a webhook.
    """

    def test_simple_basic_json_message(
        self,
        customer_webhook_post_save_signal,
    ):
        with aioresponses() as mocked_responses:
            mocked_responses.post(
                "https://example.com/",
                payload={"success": "True"},
            )
            baker.make(CustomerModel)

            mocked_responses.assert_called_once()
            assert (
                str(mocked_responses._responses[0].url)
                == "https://example.com/"
            )

    def test_simple_basic_plain_message(
        self,
        customer_webhook_post_save_signal,
    ):
        with aioresponses() as mocked_responses:
            config = customer_webhook_post_save_signal.config
            config.payload = "Hello World!"
            config.save()

            mocked_responses.post(
                "https://example.com/",
                payload={"success": "True"},
            )

            baker.make(CustomerModel)

            mocked_responses.assert_called_once()
            assert (
                str(mocked_responses._responses[0].url)
                == "https://example.com/"
            )

    def test_does_not_work_for_models_that_are_not_allowed(
        self,
        customer_webhook_post_save_signal,
    ):
        with aioresponses() as mocked_responses:
            config = customer_webhook_post_save_signal.config
            config.content_types.set([ContentType.objects.get_for_model(User)])
            config.save()

            mocked_responses.post(
                "https://example.com/",
                payload={"success": "True"},
            )
            baker.make(User)

            mocked_responses.assert_not_called()
