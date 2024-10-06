========
RabbitMQ
========

**Django Action Triggers** supports sending messages to a RabbitMQ message
broker. This section will guide you through the process of configuring RabbitMQ
as a message broker and creating actions that send messages to it.

Configuration
=============

Before messages can be sent to a RabbitMQ message broker, you need to configure
the broker in your Django settings.


.. include:: ../partials/note_ref_message_brokers_configuration_guide.rst

The RabbitMQ configuration requires that `params.queue` be set to the name of
the queue to which messages will be sent within the context of the trigger.

RabbitMQ Configuration
----------------------

In the RabbitMQ configuration, you must set the `params.queue` to specify the
queue where messages will be sent when a trigger is activated.

Example Configuration in `settings.py`
--------------------------------------

Here is an example configuration for RabbitMQ:

.. code-block:: python

  ACTION_BROKERS = {
    "my_rabbit_mq_broker": {
      "broker_type": "rabbitmq",
      "conn_details": {
        "host": "localhost",
        "port": 5672,
      },
      "params": {
        "queue": "my_queue"
      }
    }
  }


In this configuration:
- The `my_rabbit_mq_broker` is set to connect to RabbitMQ running on `localhost` on port `5672`.
- Messages will be sent to the `my_queue` queue.

Creating a RabbitMQ Action
==========================

Once you've configured RabbitMQ, you can create a trigger that sends messages
to the RabbitMQ broker whenever the trigger is activated.

Scenario
--------

Suppose you have the following Django models:

.. include:: ../partials/django_models_for_scenarios.rst
  
Let's say you want to send a message to RabbitMQ when a new sale is created.
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

The `payload` is designed to behave like a Django template. If the resultin
value is JSON-serializable, the payload will be returned as JSON; otherwise, it
will be returned as plain text.

Step 2: Create a `MessageBrokerQueue` Model Instance (RabbitMQ Action)
----------------------------------------------------------------------

Now, create a :class:`MessageBrokerQueue` instance to define the RabbitMQ
action.

.. warning::
  Hardcoding sensitive information such as connection details is not
  recommended. In the next section, we will explore how to dynamically set
  these values using callables or variables at runtime.

.. code-block:: python

    from action_triggers.models import MessageBrokerQueue

    message_broker_queue = MessageBrokerQueue.objects.create(
        config=config,
        name="my_rabbit_mq_broker",  # This needs to correspond to the key in the `ACTION_BROKERS.message_brokers` dictionary
        conn_details={
            "host": "localhost",
            "port": 5672,
            "username": "guest",
            "password": "guest",
        },
        parameters={
            "queue": "my_queue"
        }
    )

In this example:
- The `my_rabbit_mq_broker` connects to RabbitMQ on `localhost` at port `5672`.
- Messages will be sent to the `my_queue` queue.

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

Now, whenever a new sale is created, the RabbitMQ action will be triggered.

Dynamically Setting `conn_details` and `parameters`
===================================================


In the previous example, hardcoding connection details and parameters is
insecure. Instead, you can dynamically set these values at runtime using
the :ref:`dynamic loading feature<dynamic-loading>`.

Replacing Hardcoded Values
--------------------------



Let's suppose we have the following functions and variables:

* `myproject.settings.RABBITMQ_HOST` - A variable containing the RabbitMQ host.
* `myproject.settings.RABBITMQ_PORT` - A variable containing the RabbitMQ port.
* `myproject.settings.RABBITMQ_USERNAME` - A variable containing the RabbitMQ username.
* `myproject.settings.RABBITMQ_PASSWORD` - A variable containing the RabbitMQ password.
* `myproject.app.queues.get_queue_name` - A function that retrieves the queue name.

You can use these in the `conn_details` and `parameters` fields as follows:

.. code-block:: python

    from action_triggers.models import MessageBrokerQueue

    message_broker_queue = MessageBrokerQueue.objects.create(
        config=config,
        name="my_rabbit_mq_broker",
        conn_details={
            "host": "{{ myproject.settings.RABBITMQ_HOST }}",
            "port": "{{ myproject.settings.RABBITMQ_PORT }}",
            "username": "{{ myproject.settings.RABBITMQ_USERNAME }}",
            "password": "{{ myproject.settings.RABBITMQ_PASSWORD }}"
        },
        parameters={
           "queue": "{{ myproject.app.queues.get_queue_name }}"
        }
    )

Adding Dynamic Import Paths to Settings
---------------------------------------

In order to use this feature, you must ensure that the callables or variables
that you are specifying in the fields must be defined in the settings file.

Any callable or variable that you wish to be evaluated at runtime must be
defined in `ACTION_TRIGGER_SETTINGS.ALLOWED_DYNAMIC_IMPORT_PATHS`.

Using the example above, you would need to add the following to your settings
file:

.. code-block:: python

  ACTION_TRIGGER_SETTINGS = {
      ...
      'ALLOWED_DYNAMIC_IMPORT_PATHS': (
          'myproject.settings.RABBITMQ_HOST',
          'myproject.settings.RABBITMQ_PORT',
          'myproject.settings.RABBITMQ_USERNAME',
          'myproject.settings.RABBITMQ_PASSWORD',
          'myproject.app.queues.get_queue_name',
      ),
  }

---

By following these steps, you can securely and effectively set up RabbitMQ as a
message broker in **Django Action Triggers**. For more advanced configurations,
refer to the related documentation sections.
