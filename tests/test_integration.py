"""Integration tests."""

import asyncio
import json

import boto3
import pytest

try:
    from aio_pika.exceptions import QueueEmpty
except ImportError:
    pass
from aioresponses import aioresponses
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from model_bakery import baker

from tests.models import CustomerModel
from tests.utils.aws import can_connect_to_localstack
from tests.utils.kafka import can_connect_to_kafka, get_kafka_consumer
from tests.utils.rabbitmq import can_connect_to_rabbitmq, get_rabbitmq_conn
from tests.utils.redis import can_connect_to_redis, get_redis_conn


@pytest.fixture(autouse=True, scope="module")
def sqs_user(sqs_user_mod):
    yield sqs_user_mod


@pytest.fixture(autouse=True, scope="module")
def sqs_queue(sqs_queue_mod):
    yield sqs_queue_mod


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
                await queue.purge()

        asyncio.run(purge_messages())

    @pytest.mark.django_db(transaction=True)
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


@pytest.mark.skipif(
    not can_connect_to_redis(),
    reason="Cannot connect to Redis",
)
@pytest.mark.django_db(transaction=True)
class TestIntegrationRedis:
    """Integration tests where the action to be triggered is sending a payload
    to a Redis message broker.
    """

    channel = settings.ACTION_TRIGGERS["brokers"]["redis_with_host"]["params"][  # type: ignore[index]  # noqa: E501
        "channel"
    ]

    @pytest.fixture(autouse=True)
    def purge_all_messages(self):
        async def purge_messages():
            async with get_redis_conn() as conn:
                await conn.delete("test_channel")

        asyncio.run(purge_messages())

    async def get_next_message(self):
        async with get_redis_conn() as conn:
            async with conn.pubsub() as pubsub:
                await pubsub.subscribe(self.channel)
                i = 0
                while i < 10:
                    msg = await pubsub.get_message(
                        ignore_subscribe_messages=True
                    )
                    if msg:
                        return msg
                    i += 1
                    await asyncio.sleep(0.5)

    @pytest.mark.asyncio
    async def test_simple_basic_json_message(
        self,
        customer_redis_post_save_signal,
        customer,
    ):
        consumer_task = asyncio.create_task(self.get_next_message())
        await sync_to_async(baker.make)(CustomerModel)
        message = await consumer_task
        assert message["data"] == b'{"message": "Hello, World!"}'

    @pytest.fixture
    def fixture_simple_basic_plain_message(
        self,
        customer_redis_post_save_signal,
    ):
        config = customer_redis_post_save_signal.config
        config.payload = "Hello World!"
        config.save()
        baker.make(CustomerModel)

    @pytest.mark.asyncio
    async def test_simple_basic_plain_message(
        self,
        fixture_simple_basic_plain_message,
    ):
        consumer_task = asyncio.create_task(self.get_next_message())
        await sync_to_async(baker.make)(CustomerModel)
        message = await consumer_task
        assert message["data"] == b'"Hello World!"'

    @pytest.fixture
    def fixture_does_not_work_for_models_that_are_not_allowed(
        self,
        customer_redis_post_save_signal,
    ):
        config = customer_redis_post_save_signal.config
        config.content_types.set([ContentType.objects.get_for_model(User)])
        config.save()
        baker.make(User)

    @pytest.mark.asyncio
    async def test_does_not_work_for_models_that_are_not_allowed(
        self,
        fixture_does_not_work_for_models_that_are_not_allowed,
    ):
        consumer_task = asyncio.create_task(self.get_next_message())
        await sync_to_async(baker.make)(User)
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(consumer_task, timeout=5)


@pytest.mark.skipif(
    not can_connect_to_localstack(),
    reason="Cannot connect to SQS, localstack (AWS emulator) is not running.",
)
@pytest.mark.django_db(transaction=True)
class TestIntegrationMessageBrokerAwsSqs:
    """Integration tests where the action to be triggered is sending a payload
    to an AWS SQS message broker.
    """

    QUEUE_NAME = settings.ACTION_TRIGGERS["brokers"]["aws_sqs"]["params"][  # type: ignore[index]  # noqa: E501
        "queue_name"
    ]

    @pytest.fixture(autouse=True)
    def purge_all_sqs_messages(self, sqs_client):
        try:
            sqs_client.purge_queue(
                QueueUrl=sqs_client.get_queue_url(QueueName=self.QUEUE_NAME)[
                    "QueueUrl"
                ]
            )
        except Exception:
            pass

    def test_simple_basic_json_message(
        self,
        customer_aws_sqs_post_save_signal,
        customer,
        sqs_client,
    ):
        baker.make(CustomerModel)
        response = sqs_client.receive_message(
            QueueUrl=sqs_client.get_queue_url(QueueName=self.QUEUE_NAME)[
                "QueueUrl"
            ],
            MaxNumberOfMessages=1,
        )
        message = response["Messages"][0]
        assert message["Body"] == '{"message": "Hello, World!"}'
        sqs_client.delete_message(
            QueueUrl=sqs_client.get_queue_url(QueueName=self.QUEUE_NAME)[
                "QueueUrl"
            ],
            ReceiptHandle=message["ReceiptHandle"],
        )

    @pytest.fixture
    def fixture_simple_basic_plain_message(
        self,
        customer_aws_sqs_post_save_signal,
        sqs_client,
    ):
        config = customer_aws_sqs_post_save_signal.config
        config.payload = "Hello World!"
        config.save()

    def test_simple_basic_plain_message(
        self,
        fixture_simple_basic_plain_message,
        sqs_client,
    ):
        baker.make(CustomerModel)
        response = sqs_client.receive_message(
            QueueUrl=sqs_client.get_queue_url(QueueName=self.QUEUE_NAME)[
                "QueueUrl"
            ],
            MaxNumberOfMessages=1,
        )
        message = response["Messages"][0]
        assert message["Body"] == '"Hello World!"'
        sqs_client.delete_message(
            QueueUrl=sqs_client.get_queue_url(QueueName=self.QUEUE_NAME)[
                "QueueUrl"
            ],
            ReceiptHandle=message["ReceiptHandle"],
        )


@pytest.mark.skipif(
    not can_connect_to_localstack(),
    reason="Cannot connect to SQS, localstack (AWS emulator) is not running.",
)
@pytest.mark.django_db(transaction=True)
class TestIntegrationMessageBrokerAwsSns:
    """Integration tests where the action to be triggered is sending a payload
    to an AWS SNS message broker.
    """

    @pytest.fixture(autouse=True)
    def purge_all_messages(self, sns_client):
        response = sns_client.list_topics()
        for topic in response["Topics"]:
            sns_client.delete_topic(TopicArn=topic["TopicArn"])

    def test_simple_basic_json_message(
        self,
        customer_aws_sns_post_save_signal,
        sns_client,
        sqs_client,
    ):
        queue_url = sqs_client.create_queue(QueueName="test_queue_1")[
            "QueueUrl"
        ]
        topic_arn = sns_client.create_topic(Name="test_topic_1")["TopicArn"]
        sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol="sqs",
            Endpoint=sqs_client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=["QueueArn"],
            )["Attributes"]["QueueArn"],
        )
        baker.make(CustomerModel)
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )

        assert (
            json.loads(response["Messages"][0]["Body"])["Message"]
            == '{"message": "Hello, World!"}'
        )

        sqs_client.delete_queue(QueueUrl=queue_url)

    @pytest.fixture
    def fixture_simple_basic_plain_message(
        self,
        customer_aws_sns_post_save_signal,
        sns_client,
        sqs_client,
    ):
        config = customer_aws_sns_post_save_signal.config
        config.payload = "Hello Plain World!"
        config.save()

    def test_simple_basic_plain_message(
        self,
        fixture_simple_basic_plain_message,
        sns_client,
        sqs_client,
    ):
        queue_url = sqs_client.create_queue(QueueName="test_queue_1")[
            "QueueUrl"
        ]
        topic_arn = sns_client.create_topic(Name="test_topic_1")["TopicArn"]
        sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol="sqs",
            Endpoint=sqs_client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=["QueueArn"],
            )["Attributes"]["QueueArn"],
        )
        baker.make(CustomerModel)
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )

        assert (
            json.loads(response["Messages"][0]["Body"])["Message"]
            == '"Hello Plain World!"'
        )

        sqs_client.delete_queue(QueueUrl=queue_url)


@pytest.mark.skipif(
    not can_connect_to_localstack(),
    reason=(
        "Cannot connect to AWS Lambda, localstack (AWS emulator) is not "
        "running."
    ),
)
@pytest.mark.django_db(transaction=True)
class TestIntegrationActionAwsLambda:
    """Integration tests where the action to be triggered is invoking an AWS
    Lambda function.
    """

    ACTION_CONFIG = settings.ACTION_TRIGGERS["actions"][
        "aws_lambda_forward_to_sqs"
    ]
    QUEUE_NAME = "echo-back-queue"

    @pytest.fixture(autouse=True)
    def purge_all_messages(self):
        """Delete all messages in the SQS queue."""
        self.sqs_client().purge_queue(QueueUrl=self.queue_url)

    def sqs_client(self):
        return boto3.client("sqs", **self.ACTION_CONFIG["conn_details"])

    @property
    def queue_url(self):
        return self.sqs_client().get_queue_url(QueueName=self.QUEUE_NAME)[
            "QueueUrl"
        ]

    def test_simple_basic_json_message(
        self,
        customer_aws_lambda_post_save_signal,
    ):
        baker.make(CustomerModel)
        response = self.sqs_client().receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )

        assert json.loads(json.loads(response["Messages"][0]["Body"])) == {
            "message": "Hello, World!"
        }

    @pytest.fixture
    def fixture_simple_basic_plain_message(
        self,
        customer_aws_lambda_post_save_signal,
    ):
        config = customer_aws_lambda_post_save_signal.config
        config.payload = "Hello Plain World!"
        config.save()

    def test_simple_basic_plain_message(
        self,
        fixture_simple_basic_plain_message,
    ):
        baker.make(CustomerModel)
        response = self.sqs_client().receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )

        assert (
            json.loads(json.loads(response["Messages"][0]["Body"]))
            == "Hello Plain World!"
        )
