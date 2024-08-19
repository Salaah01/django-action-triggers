========
RabbitMQ
========

Django Action Triggers supports sending messages to a RabbitMQ message broker.

Configuration
=============

Before messages can be sent to a RabbitMQ message broker, the broker needs to
be configured in the Django settings.

.. include:: ../partials/note_ref_message_brokers_configuration_guide.rst

The RabbitMQ configuration requires that `params.queue` be set to the name of
the queue to which messages will be sent within the context of the trigger.

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
      },
      "params": {
        "queue": "my_queue"
      }
    }
  }


In this example, the `my_rabbit_mq_broker` broker is configured to connect to
a RabbitMQ broker running on `localhost` on port `5672`. The broker will send
messages to the `my_queue` queue.

Creating a RabbitMQ Action
==========================

Now that the RabbitMQ broker is configured, you can create a trigger that will
execute the action to send messages to the RabbitMQ broker when the trigger is
activated.

Let's start with a scenario. Suppose we have the following Django models:

.. include:: ../partials/django_models_for_scenarios.rst
  
Suppose we want to send a message to the RabbitMQ broker when certain triggers
are activated. We can set this up by following these steps:

1. Create a :class:`Config` model instance (base action):

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

This forms the basis of any action. The `payload` is designed to behave like a
Django template. If the resulting value after any parsing is JSON-serializable,
then the returning payload will be JSON, otherwise, it'll be just plain text.

2. Create a :class:`MessageBrokerQueue` model instance (RabbitMQ action):

.. warning::
  In this example, we hardcode the connection details which contains sensitive
  information. This is not recommended. Instead, we will explore how instead we
  can point to a callable or variable that will be evaluated at runtime in the
  next section.

.. code-block:: python

  from action_triggers.models import MessageBrokerQueue

  message_broker_queue = MessageBrokerQueue.objects.create(
    config=config,
    name="my_rabbit_mq_broker",
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

In this example, the `my_rabbit_mq_broker` broker is configured to connect to
a RabbitMQ broker running on `localhost` on port `5672`. The broker will send
messages to the `my_queue` queue.


3. Create a :class:`ConfigSignal` model instance (trigger):

.. code-block:: python

  from action_triggers.models import ConfigSignal
  from action_triggers.enums import SignalChoices

  config_signal = ConfigSignal.objects.create(
    config=config,
    signal=SignalChoices.POST_SAVE,
  )

Now we have a message broker action that will be triggered when a new sale is
created.

Dynamically Setting `conn_details` and `parameters`
===================================================

In the example above, we hardcoded the connection details and parameters. This
is not recommended as it exposes sensitive information. Instead, we can point
to a callable or variable that will be evaluated at runtime.

To do this, we can use the :ref:`dynamic loading<dynamic-loading>` feature.
This feature allows you to specify a path to a callable or variable that will
be evaluated at runtime to fetch the value.

Replacing Hardcoding
---------------------

Let's suppose we have the following functions and variables:

* `myproject.settings.RABBITMQ_HOST` - A variable that stores the RabbitMQ
  host.
* `myproject.settings.RABBITMQ_PORT` - A variable that stores the RabbitMQ
  port.
* `myproject.settings.RABBITMQ_USERNAME` - A variable that stores the RabbitMQ
  username.
* `myproject.settings.RABBITMQ_PASSWORD` - A variable that stores the RabbitMQ
  password.
* `myproject.app.queues.get_queue_name` - A function that fetches the queue
  name.

We can specify the path to these variables in the `conn_details` and
`parameters`:

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


