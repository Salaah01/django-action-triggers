=====
Redis
=====

**Django Action Triggers** supports sending messages to a Redis message broker.
This section guides you through configuring Redis and creating triggers that
send messages to a Redis broker.

Installation
============

To use Redis as a message broker, you will need to install an additional
package. This can be done by running the following command:

.. code-block:: bash

  pip install django-action-triggers[redis]

Configuration
=============

Before messages can be sent to a Redis message broker, the broker needs to be
configured in the Django settings.

.. include:: ../partials/note_ref_message_brokers_configuration_guide.rst

Redis Configuration
-------------------

In the Redis configuration, you must set the `params.channel` to specify the
channel where messages will be sent when a trigger is activated.

Example Configuration in `settings.py`
--------------------------------------

Here are two possible configurations for Redis:

Example 1 (using `host` and `port`):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  ACTION_BROKERS = {
    "redis_1": {
      "broker_type": "redis",
      "conn_details": {
        "host": "localhost",
        "port": 6370
      },
      "params": {
        "channel": "my_channel"
      }
    }
  }

Example 2 (using `url`):
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  ACTION_BROKERS = {
    "redis_2": {
      "broker_type": "redis",
      "conn_details": {
        "url": "localhost:6370"
      },
      "params": {
        "channel": "my_channel"
      }
    }
  }

In both configurations:
- The Redis broker connects to `localhost` on port `6370`.
- Messages will be sent to the `my_channel` channel.

Creating a Redis Action
=======================

Once Redis is configured, you can create a trigger that sends messages to the
Redis broker whenever the trigger is activated.

Scenario
--------

Suppose you have the following Django models:

.. include:: ../partials/django_models_for_scenarios.rst

Let's say you want to send a message to Redis when a new sale is created. You
can achieve this by following these steps:

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

Step 2: Create a `MessageBrokerQueue` Model Instance (Redis Action)
-------------------------------------------------------------------

Now, create a `MessageBrokerQueue` instance to define the Redis action.

.. warning::
  Hardcoding sensitive information such as connection details is not
  recommended. In the next section, we will explore how to dynamically set
  these values using callables or variables at runtime.

.. code-block:: python

    from action_triggers.models import MessageBrokerQueue

    redis_action = MessageBrokerQueue.objects.create(
        config=config,
        name="redis_1",
        conn_details={
            "host": "localhost",
            "port": 6370,
        },
        parameters={
            "channel": "my_channel"
        }
    )

In this example:
- The Redis broker connects to `localhost` on port `6370`.
- Messages will be sent to the `my_channel` channel.

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

Now, whenever a new sale is created, the Redis action will be triggered.

Dynamically Setting `conn_details` and `parameters`
===================================================

In the previous example, hardcoding connection details and parameters is
insecure. Instead, you can dynamically set these values at runtime.

To do this, we can use the :ref:`dynamic loading<dynamic-loading>` feature.
This feature allows you to specify a path to a callable or variable that
will be evaluated at runtime to retrieve the value.

Replacing Hardcoded Values
--------------------------

Suppose you have the following variable:

- `myproject.settings.REDIS_HOST`: Stores the Redis host.

You can use this in the `conn_details` field as follows:

.. code-block:: python

    from action_triggers.models import MessageBrokerQueue

    redis_action = MessageBrokerQueue.objects.create(
        config=config,
        name="redis_1",  # This needs to correspond to the key in the `ACTION_BROKERS.message_brokers` dictionary
        conn_details={
            "host": "{{ myproject.settings.REDIS_HOST }}",
        },
        parameters={
            "channel": "my_channel"
        }
    )

Adding Dynamic Import Paths to Settings
---------------------------------------

To enable dynamic loading, ensure that the callables or variables you are 
pecifying are defined in your Django settings.

Any callable or variable that you wish to be evaluated at runtime must be
defined in `ACTION_TRIGGER_SETTINGS.ALLOWED_DYNAMIC_IMPORT_PATHS`.

In `settings.py`, add the following:

.. code-block:: python

    ACTION_TRIGGER_SETTINGS = {
        ...
        'ALLOWED_DYNAMIC_IMPORT_PATHS': (
            'myproject.settings.REDIS_HOST',
        ),
    }

This configuration ensures that the specified paths can be evaluated at
runtime.

---

By following these steps, you can securely and effectively set up Redis as a
message broker in **Django Action Triggers**. For more advanced configurations,
refer to the related documentation sections.
