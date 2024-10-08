.. _message_brokers:

===============
Message Brokers
===============

Message broker actions in **Django Action Triggers** allow you to send messages
to a message broker when a trigger is activated. This is useful for integrating
with distributed systems, event-driven architectures, and asynchronous
processing.

Navigate to the :ref:`message_brokers_configuration_guides` section to learn
how to configure specific message brokers in your Django settings.

Support for other message brokers are planned for future releases. If you would
like to see support for a specific message broker, please open an issue on the
`GitHub repository <https://github.com/Salaah01/django-action-triggers>`_.

.. _message_brokers_configuration:

Configuration
=============

Before you can send messages to a message broker, you must configure the broker
in your Django settings. This involves specifying the broker type, connection
details and any necessary parameters for the broker.

For more information, refer to the :ref:`action_trigger_settings` guide.

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

- **Security**: Avoid hardcoding sensitive information, such as passwords in
  your `settings.py` file. Use environment variables or a secure vault to
  manage these credentials.
- **Testing**: Before deploying to production, thoroughly test your broker
  configuration in a development environment to ensure that messages are being
  sent and received correctly.
- **Set Timeout Limits**: Define a maximum timeout for message broker actions
  to prevent long-running requests from blocking your application. This can be
  done by setting `ACTION_TRIGGER_SETTINGS.MAX_BROKER_TIMEOUT` in your
  settings.

.. _message_brokers_configuration_guides:

Broker Configuration Guides
===========================

The following guides will help you configure specific message brokers within
your Django project using **Django Action Triggers**:

.. toctree::
   :maxdepth: 1
   :caption: Message Brokers
   
   message_brokers/kafka
   message_brokers/rabbitmq
   message_brokers/redis
   message_brokers/aws_sqs
   message_brokers/aws_sns
   message_brokers/gcp_pubsub