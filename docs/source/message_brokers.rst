.. _message_brokers:

===============
Message Brokers
===============

Message broker actions in **Django Action Triggers** allow you to send messages
to a message broker when a trigger is activated. This is useful for integrating
with distributed systems, event-driven architectures, and asynchronous
processing.

Currently, the supported message brokers are **Kafka** and **RabbitMQ**.

Support for other message brokers are planned for future releases. If you would
like to see support for a specific message broker, please open an issue on the
`GitHub repository <https://github.com/Salaah01/django-action-triggers>`_.

.. _message_brokers_configuration:

Configuration
=============

Before you can send messages to a message broker, you must configure the broker
in your Django settings. This involves specifying the connection details and
any necessary parameters for the broker.

Configuring Message Brokers
---------------------------

Message brokers are configured in the `ACTION_TRIGGERS.brokers` dictionary in
your `settings.py` file. Each broker configuration includes the broker type,
connection details, and any additional parameters required.

**Example Configuration in `settings.py`**

Here is the structure of a basic message broker configuration:

.. code-block:: python

    ACTION_TRIGGERS = {
        "brokers": {
            "<broker_config_name>": {
                "broker_type": "<broker_type>",  # e.g., "rabbitmq" or "kafka"
                "conn_details": {
                    "<key>": "<value>"  # Key-value pairs of connection details (e.g., host, port)
                },
                "params": {
                    "<key>": "<value>"  # Key-value pairs of broker-specific parameters (e.g., queue, topic)
                }
            }
        }
    }


**Configuration Options**

.. include:: message_brokers/config_options.rst

Example Configuration
=====================

Below is an example configuration for setting up a RabbitMQ broker:
  
.. code-block:: python

  ACTION_BROKERS = {
    "my_rabbit_mq_broker": {
      "broker_type": "rabbitmq",
      "conn_details": {
        "host": "localhost",
        "port": 5672,
        "username": "guest",
        "password": "guest",
        "virtual_host": "/"
      },
      "params": {
        "queue": "my_queue"  # The name of the queue to which messages will be sent
      }
    }
  }

Best Practices for Configuration
================================

- **Security**: Avoid hardcoding sensitive information, such as passwords, in your `settings.py` file. Use environment variables or a secure vault to manage these credentials.
- **Testing**: Before deploying to production, thoroughly test your broker configuration in a development environment to ensure that messages are being sent and received correctly.

Broker Configuration Guides
===========================

This guide should help you configure message brokers within **Django Action Triggers**. For more advanced configurations, refer to the specific guides for Kafka and RabbitMQ.

.. toctree::
   :maxdepth: 2
   :caption: Message Brokers:

   message_brokers/kafka
   message_brokers/rabbitmq
