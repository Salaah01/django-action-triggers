.. _message_brokers:

===============
Message Brokers
===============

Message broker actions allow you to send messages to a message broker when a
trigger is activated.

The supported message brokers are Kafka and RabbitMQ.

.. _message_brokers_configuration:

Configuration
=============

Before messages can be sent to a message broker, the broker needs to be
configured in the Django settings.

Message brokers are configured in `ACTION_TRIGGERS.brokers` in the Django
settings. A configuration for a given broker should look like this:

**settings.py**

.. code-block:: python

  ACTION_BROKERS = {
    "<broker_config_name>": {
      "broker_type": "<broker_type>",
      "conn_details", {"<key>": "<value>"},  # Key-value pair of connection details
      "params": {"<key>": "<value>"},  # Key-value pair of parameters
    }
  }


Config Options
==============

.. include:: message_brokers/config_options.rst

Example Configuration
=====================

An example configuration for RabbitMQ would look like this:
  
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
        "queue": "my_queue"
      }
    }
  }



.. toctree::
   :maxdepth: 2
   :caption: Message Brokers:

   message_brokers/kafka
   message_brokers/rabbitmq
