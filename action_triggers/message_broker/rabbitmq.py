from action_triggers.message_broker.base import BrokerBase, ConnectionBase
from action_triggers.message_broker.enums import BrokerType

import pika  # type: ignore[import-untyped]


class RabbitMQConnection(ConnectionBase):
    def connect(self):
        self.conn = pika.BlockingConnection(
            pika.ConnectionParameters(**self.conn_params)
        )
        return


class RabbitMQBroker(BrokerBase):
    broker_type = BrokerType.RABBITMQ
    conn_class = RabbitMQConnection

    def __init__(self, conn_params: dict, **kwargs):
        super().__init__(conn_params, **kwargs)
        self.queue = kwargs.get("queue")
        self.exchange = kwargs.get("exchange", "")

    def validate(self) -> None:
        if not self.queue:
            raise ValueError("Queue name must be provided.")

    def _send_message_impl(self, message: str) -> None:
        with self.conn_class(self.conn_params) as conn:
            channel = conn.conn.channel()
            channel.queue_declare(queue=self.queue)
            channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.queue,
                body=message,
            )
