from enum import Enum
from functools import lru_cache, partial
from string import Template
from uuid import uuid4

try:
    import boto3  # type: ignore[import-untyped]
except ImportError:
    boto3 = None  # type: ignore[assignment]

from django.conf import settings

BROKER_SETTINGS = settings.ACTION_TRIGGERS["brokers"]["aws_sns"]  # type: ignore[index]  # noqa E501
CONN_DETAILS = BROKER_SETTINGS["conn_details"]  # type: ignore[index]
QUEUE_NAME = settings.ACTION_TRIGGERS["brokers"]["aws_sqs"]["params"][  # type: ignore[index]  # noqa E501
    "queue_name"
]
TOPIC_NAME = "test_topic_1"

TOPIC_ARN = BROKER_SETTINGS["params"]["topic_arn"]  # type: ignore[index]
LAMBDA_SETTINGS = settings.ACTION_TRIGGERS["actions"]["aws_lambda"]  # type: ignore[index]  # noqa E501
LAMBDA_FUNCTION_NAME = LAMBDA_SETTINGS["params"]["FunctionName"]  # type: ignore[index]  # noqa E501


class PolicyEnum(Enum):
    """An enumeration of the AWS policies."""

    SNS_FULL_ACCESS = "arn:aws:iam::aws:policy/AmazonSNSFullAccess"
    SQS_FULL_ACCESS = "arn:aws:iam::aws:policy/AmazonSQSFullAccess"


@lru_cache
def can_connect_to_sns() -> bool:
    """Check if the application can connect to the AWS SNS service.

    :return: True if the application can connect to the AWS SNS service,
        False otherwise.
    """

    if boto3 is None:
        return False
    if not CONN_DETAILS.get("endpoint_url"):
        return False

    try:
        boto3.client("sns", **CONN_DETAILS).list_topics()
        return True
    except Exception:
        return False


class User:
    """A class to manage an AWS SNS user."""

    def __init__(self, username: str) -> None:
        """Initialize the SNSUser object.

        :param username: The name of the user to create.
        """

        self.username = username
        self.client = boto3.client("iam", **CONN_DETAILS)

    def __call__(self) -> None:
        """Create a user with permissions to access AWS SNS.

        :return: The user's access and secret key.
        """
        # The `create_user` method is typically replaced by the factory
        # function which creates the user with the appropriate policy.
        self.create_user()  # type: ignore[call-arg]

    def delete_user_if_exists(self) -> None:
        """Delete the user if it exists.

        :param client: The boto3 client to use.
        :param username: The username to delete.
        """
        try:
            attached_policies = self.client.list_attached_user_policies(
                UserName=self.username
            )["AttachedPolicies"]
            for policy in attached_policies:
                self.client.detach_user_policy(
                    UserName=self.username, PolicyArn=policy["PolicyArn"]
                )
            self.client.delete_user(UserName=self.username)
        except self.client.exceptions.NoSuchEntityException:
            pass

    def create_user(self, policy: PolicyEnum) -> None:
        """Create a user with permissions to access AWS SNS.

        :param policy: The policy to attach to the user.
        """
        self.delete_user_if_exists()
        self.client.create_user(UserName=self.username)
        self.client.attach_user_policy(
            UserName=self.username,
            PolicyArn=policy,
        )
        response = self.client.create_access_key(UserName=self.username)
        self.aws_access_key_id = response["AccessKey"]["AccessKeyId"]
        self.aws_secret_access_key = response["AccessKey"]["SecretAccessKey"]


def user_factory(username: str, policy: PolicyEnum) -> User:
    """Factory for creating a `User` object.

    :param service_name: The name of the service.
    :param username: The username of the user.
    :param policy: The policy to attach to the user.
    :return: The user object.
    """

    username = Template("$user-$suffix").substitute(
        user=username, suffix=uuid4().hex[:8]
    )
    klass = User(username)
    klass.create_user = partial(  # type: ignore[method-assign]
        klass.create_user,
        policy,
    )
    return klass


def sqs_user_factory() -> User:
    """Factory for creating a `User` object.

    :return: The user object.
    """
    return user_factory(  # type: ignore[call-arg]
        "sqs",
        PolicyEnum.SQS_FULL_ACCESS.value,  # type: ignore[arg-type]
    )


def sns_user_factory() -> User:
    """Factory for creating a `User` object.

    :return: The user object.
    """
    return user_factory(  # type: ignore[call-arg]
        "sns",
        PolicyEnum.SNS_FULL_ACCESS.value,  # type: ignore[arg-type]
    )


class SQSQueue:
    """A class to manage an AWS SQS queue."""

    def __init__(self, queue_name: str = QUEUE_NAME) -> None:
        """Initialize the class.

        :param queue_name: The name of the queue.
        """
        self.queue_name = queue_name
        self.client = boto3.client("sqs", **CONN_DETAILS)

    def __call__(self) -> str:
        """Create a queue.

        :return: The queue URL.
        """
        return self.create_queue()

    def delete_queue_if_exists(self) -> None:
        """Delete the queue if it exists."""
        try:
            self.client.delete_queue(QueueUrl=self.queue_url)
        except AttributeError:
            pass

    def create_queue(self) -> str:
        """Create a queue.

        :return: The queue URL.
        """
        self.delete_queue_if_exists()
        response = self.client.create_queue(QueueName=self.queue_name)
        self.queue_url = response["QueueUrl"]
        return self.queue_url


class SNSTopic:
    """A class to manage an AWS SNS topic."""

    def __init__(self, topic: str = TOPIC_NAME) -> None:
        """Initialize the class.

        :param topic: The name of the topic.
        """
        self.topic = topic
        self.client = boto3.client("sns", **CONN_DETAILS)

    def __call__(self) -> str:
        """Create a topic.

        :return: The topic ARN.
        """
        return self.create_topic()

    def delete_topic_if_exists(self) -> None:
        """Delete the topic if it exists."""
        try:
            self.client.delete_topic(TopicArn=self.topic_arn)
        except AttributeError:
            pass

    def create_topic(self) -> str:
        """Create a topic.

        :return: The topic ARN.
        """
        self.delete_topic_if_exists()
        response = self.client.create_topic(Name=self.topic)
        self.topic_arn = response["TopicArn"]
        return self.topic_arn


@lru_cache
def can_connect_to_localstack() -> bool:
    """Check if the service can connect to Localstack (AWS emulator).

    :return: True if the service can connect to Localstack, False otherwise.
    """
    if not can_connect_to_sns():
        return False

    try:
        boto3.client("sns", **CONN_DETAILS).list_topics()
        return True
    except Exception:
        return False
