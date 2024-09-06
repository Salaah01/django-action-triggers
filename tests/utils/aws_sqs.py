from functools import lru_cache

try:
    import boto3  # type: ignore[import-untyped]
except ImportError:
    boto3 = None  # type: ignore[assignment]

from django.conf import settings

ENDPOINT = settings.AWS_ENDPOINT
QUEUE_NAME = settings.ACTION_TRIGGERS["brokers"]["aws_sqs"]["params"][  # type: ignore[index]  # noqa E501
    "queue_name"
]
POLICY_ARN = "arn:aws:iam::aws:policy/AmazonSQSFullAccess"


@lru_cache
def can_connect_to_sqs() -> bool:
    """Check if the service can connect to AWS SQS.

    :return: True if the service can connect to AWS SQS, False otherwise.
    """
    if not boto3:
        return False
    if not ENDPOINT:
        return False

    try:
        boto3.client("sqs", endpoint_url=ENDPOINT).list_queues()
        return True
    except Exception:
        return False


class SQSUser:
    """A class to manage an AWS SQS user."""

    def __init__(self, username: str = "sqs-test-user") -> None:
        """Initialize the class.

        :param username: The username of the user.
        """
        self.username = username
        self.client = boto3.client("iam", endpoint_url=ENDPOINT)
        self.aws_access_key_id = ""
        self.aws_secret_access_key = ""

    def __call__(self) -> None:
        """Create a user with permissions to access AWS SQS.

        :return: The user's access and secret key.
        """
        self.create_user()

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

    def create_user(self) -> None:
        """Create a user with permissions to access AWS SQS.

        :return: The user's access and secret key.
        """
        self.delete_user_if_exists()
        self.client.create_user(UserName=self.username)
        self.client.attach_user_policy(
            UserName=self.username, PolicyArn=POLICY_ARN
        )
        access_key = self.client.create_access_key(UserName=self.username)
        self.aws_access_key_id = access_key["AccessKey"]["AccessKeyId"]
        self.aws_secret_access_key = access_key["AccessKey"]["SecretAccessKey"]


class SQSQueue:
    """A class to manage an AWS SQS queue."""

    def __init__(
        self,
        user: SQSUser,
        queue_name: str = QUEUE_NAME,
    ) -> None:
        """Initialize the class.

        :param user: The user to use for creating the queue.
        :param queue_name: The name of the queue.
        """
        self.user = user
        self.queue_name = queue_name
        print(f"\033[92mENDPOINT============={ENDPOINT}\033[0m")
        self.client = boto3.client(
            "sqs",
            endpoint_url=ENDPOINT,
            aws_access_key_id=user.aws_access_key_id,
            aws_secret_access_key=user.aws_secret_access_key,
        )

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
