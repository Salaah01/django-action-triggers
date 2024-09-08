=====
Kafka
=====

**Django Action Triggers** supports sending messages to a Kafka message broker.
This section guides you through configuring Kafka and creating triggers that
send messages to a Kafka broker.

Configuration
=============

Before messages can be sent to a Kafka message broker, the broker needs to
be configured in the Django settings.

.. include:: ../partials/note_ref_message_brokers_configuration_guide.rst

Kafka Configuration
-------------------

The following configuration options must be set in the Django settings to
configure the Kafka message broker:

- `conn_details.bootstrap_servers`: The list of Kafka brokers to connect to.
- `params.topic`: The topic where messages will be sent when a trigger is
  activated.

Example Configuration in `settings.py`
--------------------------------------

Here is an example configuration for Kafka:

.. code-block:: python

  ACTION_BROKERS = {
    "my_kafka_broker": {
      "broker_type": "kafka",
      "conn_details": {
        "bootstrap_servers": "localhost:9092",
      },
      "params": {
        "topic": "my_topic"
      }
    }
  }

In this configuration:
- The `my_kafka_broker` is set to connect to Kafka running on `localhost` on
  port `9092`.
- Messages will be sent to the `my_topic` topic.

Creating a Kafka Action
=======================

Once you’ve configured Kafka, you can create a trigger that sends messages to
the Kafka broker whenever the trigger is activated.

Scenario
--------

Suppose you have the following Django models:

.. include:: ../partials/django_models_for_scenarios.rst

Let's say you want to send a message to Kafka when a new sale is created.
You can achieve this by following these steps:

Step 1: Create a `Config` Model Instance (Base Action)
------------------------------------------------------

The `Config` model defines the base action, including the payload that will be
sent when the trigger is activated.

.. code-block:: python

  from django.contrib.contenttypes.models import ContentType
  from action_triggers.models import Config

  config = Config.objects.create(
    payload={
      "customer_name": "{{ customer.name }}",
      "product_name": "{{ product.name }}",
      "quantity": "{{ quantity }}"
    },
    active=True,
    content_types=[
      ContentType.objects.get_for_model(Sale)
    ]
  )

The `payload` is designed to behave like a Django template. If the resulting
value is JSON-serializable, the payload will be returned as JSON; otherwise,
it will be returned as plain text.

Step 2: Create a `MessageBrokerQueue` Model Instance (Kafka Action)
--------------------------------------------------------------------

Now, create a `MessageBrokerQueue` instance to define the Kafka action.

.. warning::
  Hardcoding sensitive information such as connection details is not
  recommended. In the next section, we will explore how to dynamically set
  these values using callables or variables at runtime.

.. code-block:: python
  
    from action_triggers.models import MessageBrokerQueue
  
    kafka_action = MessageBrokerQueue.objects.create(
        config=config,
        name="my_kafka_broker",
        conn_details={
            "bootstrap_servers": "localhost:9092",
        },
        parameters={
            "topic": "my_topic"
        }
    )

In this example:
- The `my_kafka_broker` connects to Kafka on `localhost` at port `9092`.
- Messages will be sent to the `my_topic` topic.

Step 3: Create a `ConfigSignal` Model Instance (Trigger)
---------------------------------------------------------

Finally, link the action to a trigger event, such as saving a model instance.

.. code-block:: python

  from action_triggers.models import ConfigSignal
  from action_triggers.enums import SignalChoices

  config_signal = ConfigSignal.objects.create(
    config=config,
    signal=SignalChoices.POST_SAVE,
  )

Now, whenever a new sale is created, the Kafka action will be triggered.

Dynamically Setting `conn_details` and `parameters`
===================================================

In the previous example, hardcoding connection details and parameters is
insecure. Instead, you can dynamically set these values at runtime.

To do this, we can use the :ref:`dynamic loading<dynamic-loading>` feature.
This feature allows you to specify a path to a callable or variable that will
be evaluated at runtime to retrieve the value.

Replacing Hardcoded Values
--------------------------

Suppose you have the following variable:

- `myproject.settings.KAFKA_BOOTSTRAP_SERVERS`: Stores the Kafka bootstrap servers.

You can use this in the `conn_details` field as follows:

.. code-block:: python

    from action_triggers.models import MessageBrokerQueue

    kafka_action = MessageBrokerQueue.objects.create(
        config=config,
        name="my_kafka_broker",
        conn_details={
            "bootstrap_servers": "{{ myproject.settings.KAFKA_BOOTSTRAP_SERVERS }}",
        },
        parameters={
            "topic": "my_topic"
        }
    )

Adding Dynamic Import Paths to Settings
---------------------------------------

To enable dynamic loading, ensure that the callables or variables you are
specifying are defined in your Django settings.

Any callable or variable that you wish to be evaluated at runtime must be
defined in `ACTION_TRIGGER_SETTINGS.ALLOWED_DYNAMIC_IMPORT_PATHS`.

In `settings.py`, add the following:

.. code-block:: python

    ACTION_TRIGGER_SETTINGS = {
        ...
        'ALLOWED_DYNAMIC_IMPORT_PATHS': (
            'myproject.settings.KAFKA_BOOTSTRAP_SERVERS',
        ),
    }

This configuration ensures that the specified paths can be evaluated at
runtime.

---

By following these steps, you can securely and effectively set up Kafka as a
message broker in **Django Action Triggers**. For more advanced
configurations, refer to the related documentation sections.
