from collections import namedtuple

import django
import pytest

try:
    import boto3  # type: ignore[import-untyped]
except ImportError:
    boto3 = None  # type: ignore[assignment]

try:
    from google.cloud import pubsub_v1  # type: ignore[import-untyped]
except ImportError:
    pubsub_v1 = None


django.setup()


from django.conf import settings  # noqa: E402
from django.contrib.auth.models import User  # noqa: E402
from django.contrib.contenttypes.models import ContentType  # noqa: E402
from model_bakery import baker  # noqa: E402

from action_triggers.enums import SignalChoices  # noqa: E402
from action_triggers.models import (  # noqa: E402
    Action,
    Config,
    ConfigSignal,
    MessageBrokerQueue,
    Webhook,
)
from tests.models import CustomerModel, CustomerOrderModel  # noqa: E402
from tests.utils.aws import (  # noqa: E402
    SNSTopic,
    SQSQueue,
    can_connect_to_localstack,
    sqs_user_factory,
)


@pytest.fixture
def config(db):
    return baker.make(Config, payload={"message": "Hello, World!"})


@pytest.fixture
def webhook(config):
    return baker.make(
        Webhook,
        url="https://example.com/",
        config=config,
    )


@pytest.fixture
def webhook_with_headers(config):
    return baker.make(
        Webhook,
        url="https://example-with-headers.com/",
        config=config,
        headers={"Authorization": "Bearer 123"},
    )


@pytest.fixture
def config_add_customer_ct(config):
    config.content_types.add(ContentType.objects.get_for_model(CustomerModel))


@pytest.fixture
def rabbitmq_1_trigger(config):
    return baker.make(
        MessageBrokerQueue,
        name="rabbitmq_1",
        config=config,
    )


@pytest.fixture
def kafka_1_trigger(config):
    return baker.make(
        MessageBrokerQueue,
        name="kafka_1",
        config=config,
    )


@pytest.fixture
def redis_with_host_trigger(config):
    return baker.make(
        MessageBrokerQueue,
        name="redis_with_host",
        config=config,
    )


@pytest.fixture
def aws_sqs_trigger(config):
    return baker.make(
        MessageBrokerQueue,
        name="aws_sqs",
        config=config,
    )


@pytest.fixture
def aws_sns_trigger(config):
    return baker.make(
        MessageBrokerQueue,
        name="aws_sns",
        config=config,
    )


@pytest.fixture
def aws_lambda_trigger(config):
    return baker.make(
        Action,
        name="aws_lambda_forward_to_sqs",
        config=config,
    )


@pytest.fixture
def gcp_pubsub_trigger(config):
    return baker.make(
        MessageBrokerQueue,
        name="gcp_pubsub_test_topic",
        config=config,
    )


@pytest.fixture
def customer_post_save_signal(config):
    return baker.make(
        ConfigSignal,
        config=config,
        signal=SignalChoices.POST_SAVE,
    )


@pytest.fixture
def customer_rabbitmq_post_save_signal(
    config,
    config_add_customer_ct,
    customer_post_save_signal,
    rabbitmq_1_trigger,
):
    return namedtuple("ConfigContext", ["config", "signal", "trigger"])(
        config,
        customer_post_save_signal,
        rabbitmq_1_trigger,
    )


@pytest.fixture
def customer_kafka_post_save_signal(
    config,
    config_add_customer_ct,
    customer_post_save_signal,
    kafka_1_trigger,
):
    return namedtuple("ConfigContext", ["config", "signal", "trigger"])(
        config,
        customer_post_save_signal,
        kafka_1_trigger,
    )


@pytest.fixture
def customer_redis_post_save_signal(
    config,
    config_add_customer_ct,
    customer_post_save_signal,
    redis_with_host_trigger,
):
    return namedtuple("ConfigContext", ["config", "signal", "trigger"])(
        config,
        customer_post_save_signal,
        redis_with_host_trigger,
    )


@pytest.fixture
def customer_aws_sqs_post_save_signal(
    config,
    config_add_customer_ct,
    customer_post_save_signal,
    aws_sqs_trigger,
):
    return namedtuple("ConfigContext", ["config", "signal", "trigger"])(
        config,
        customer_post_save_signal,
        aws_sqs_trigger,
    )


@pytest.fixture
def customer_aws_sns_post_save_signal(
    config,
    config_add_customer_ct,
    customer_post_save_signal,
    aws_sns_trigger,
):
    return namedtuple("ConfigContext", ["config", "signal", "trigger"])(
        config,
        customer_post_save_signal,
        aws_sns_trigger,
    )


@pytest.fixture
def customer_aws_lambda_post_save_signal(
    config,
    config_add_customer_ct,
    customer_post_save_signal,
    aws_lambda_trigger,
):
    return namedtuple("ConfigContext", ["config", "signal", "trigger"])(
        config,
        customer_post_save_signal,
        aws_lambda_trigger,
    )


@pytest.fixture
def customer_gcp_pubsub_post_save_signal(
    config,
    config_add_customer_ct,
    customer_post_save_signal,
    gcp_pubsub_trigger,
):
    return namedtuple("ConfigContext", ["config", "signal", "trigger"])(
        config,
        customer_post_save_signal,
        gcp_pubsub_trigger,
    )


@pytest.fixture
def customer_webhook_post_save_signal(
    config,
    config_add_customer_ct,
    customer_post_save_signal,
    webhook,
):
    return namedtuple("ConfigContext", ["config", "signal", "trigger"])(
        config,
        customer_post_save_signal,
        webhook,
    )


@pytest.fixture
def full_loaded_config(config):
    config.payload = {"key": "value"}
    config.save()

    config.content_types.set(
        [
            ContentType.objects.get_for_model(CustomerModel),
            ContentType.objects.get_for_model(CustomerOrderModel),
        ]
    )

    webhook_1, webhook_2 = baker.make(
        Webhook,
        config=config,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {{ path.to.token }}",
        },
        _quantity=2,
    )
    message_broker_queue_1, message_broker_queue_2 = baker.make(
        MessageBrokerQueue,
        config=config,
        conn_details={"host": "localhost", "port": 5672},
        parameters={"queue": "test_queue_1"},
        _quantity=2,
    )
    action_1, action_2 = baker.make(
        Action,
        config=config,
        conn_details={"host": "localhost", "port": 5672},
        parameters={"queue": "test_queue_1"},
        _quantity=2,
    )
    config_signal_1, config_signal_2 = baker.make(
        ConfigSignal,
        config=config,
        _quantity=2,
    )

    return namedtuple(
        "ConfigContext",
        [
            "config",
            "webhooks",
            "mesage_broker_queues",
            "actions",
            "config_signals",
        ],
    )(
        config,
        [webhook_1, webhook_2],
        [message_broker_queue_1, message_broker_queue_2],
        [action_1, action_2],
        [config_signal_1, config_signal_2],
    )


@pytest.fixture
def superuser():
    return baker.make(User, is_staff=True, is_superuser=True)


@pytest.fixture
def customer():
    return baker.make(CustomerModel)


@pytest.fixture(scope="module")
def sqs_user_mod():
    if not can_connect_to_localstack():
        yield None
    else:
        sqs = sqs_user_factory()
        sqs()
        yield sqs
        sqs.delete_user_if_exists()


@pytest.fixture(scope="module")
def sqs_queue_mod(sqs_user_mod):
    if not can_connect_to_localstack():
        yield None
    else:
        queue = SQSQueue()
        queue()
        yield queue
        queue.delete_queue_if_exists()


@pytest.fixture(scope="module")
def sns_queue_mod(sqs_user_mod):
    if not can_connect_to_localstack():
        yield None
    else:
        queue = SNSTopic()
        queue()
        yield queue
        queue.delete_topic_if_exists()


@pytest.fixture
def sqs_client():
    return boto3.client(
        "sqs",
        **settings.ACTION_TRIGGERS["brokers"]["aws_sqs"]["conn_details"],
    )


@pytest.fixture
def sns_client():
    return boto3.client(
        "sns",
        **settings.ACTION_TRIGGERS["brokers"]["aws_sns"]["conn_details"],
    )


@pytest.fixture
def gcp_pubsub_topic_path():
    publisher = pubsub_v1.PublisherClient()
    conn_details = settings.ACTION_TRIGGERS["brokers"][
        "gcp_pubsub_test_topic"
    ]["conn_details"]
    return publisher.topic_path(**conn_details)


@pytest.fixture
def gcp_pubsub_topic_refresh(gcp_pubsub_topic_path):
    publisher = pubsub_v1.PublisherClient()
    try:
        publisher.delete_topic(request={"topic": gcp_pubsub_topic_path})
    except Exception:
        pass
    return publisher.create_topic(request={"name": gcp_pubsub_topic_path})


@pytest.fixture
def gcp_pubsub_refresh_subscription(gcp_pubsub_topic_path):
    subscription = pubsub_v1.SubscriberClient()
    conn_details = settings.ACTION_TRIGGERS["brokers"][
        "gcp_pubsub_test_topic"
    ]["conn_details"]
    subscription_path = subscription.subscription_path(*conn_details.values())
    try:
        subscription.delete_subscription(
            request={"subscription": subscription_path}
        )
    except Exception:
        pass
    return subscription.create_subscription(
        request={
            "name": subscription_path,
            "topic": gcp_pubsub_topic_path,
        }
    )
