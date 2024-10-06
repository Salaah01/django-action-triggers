=========================================
AWS SNS (AWS Simple Notification Service)
=========================================

**Django Action Triggers** supports sending messages to an AWS SNS (Simple
Notification Service) message broker. This section guides you through
configuring AWS SNS and creating triggers that send messages to an AWS SNS
broker.

Configuration
=============

Before messages can be sent to an AWS SNS message broker, the broker needs to
be configured in the Django settings.

.. include:: ../partials/note_ref_message_brokers_configuration_guide.rst

AWS SNS Configuration
---------------------

The following configuration options must be set in the Django settings to
configure the AWS SNS message broker:

- `conn_details.endpoint_url`: The endpoint URL of the AWS SNS service. If you
  are using AWS' SNS service, you can set this to `None`. Otherwise, you can
  set this to the endpoint URL of the AWS SNS service/emulator you are using.

- `params.topic_arn`: The Amazon Resource Name (ARN) of the topic where
  messages will be sent when a trigger is activated.

Example Configuration in `settings.py` using `topic_arn`
--------------------------------------------------------

Here is an example configuration for AWS SNS:

.. code-block:: python

  ACTION_BROKERS = {
    "aws_sns_1": {
      "broker_type": "aws_sns",
      "conn_details": {
        "endpoint_url": None
      },
      "params": {
        "topic_arn": "arn:aws:sns:us-east-1:123456789012:my_topic"
      }
    }
  }

Example Configuration in `settings.py` using `endpoint_url`
-----------------------------------------------------------

Here is an example configuration for AWS SNS using the endpoint URL. This can
be useful when using a local instance of the AWS SNS service:

.. code-block:: python

  ACTION_BROKERS = {
    "aws_sns_3": {
      "broker_type": "aws_sns",
      "conn_details": {
        "endpoint_url": "http://localhost:4566"
      },
      "params": {
        "topic_arn": "arn:aws:sns:us-east-1:123456789012:my_topic"
      }
    }
  }

Creating an AWS SNS Action
==========================

Once AWS SNS is configured, you can create a trigger that sends messages to the
AWS SNS broker whenever the trigger is activated.

Scenario
--------

Suppose you have the following Django models:

.. include:: ../partials/django_models_for_scenarios.rst

Let's say you want to send a message to AWS SNS when a new sale is created. You
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

Step 2: Create a `MessageBrokerQueue` Model Instance (AWS SNS Action)
---------------------------------------------------------------------

.. warning::
  Hardcoding sensitive information such as connection details is not
  recommended. In the next section, we will explore how to dynamically set
  these values using callables or variables at runtime.

.. code-block:: python

    from action_triggers.models import MessageBrokerQueue

    aws_sns_action = MessageBrokerQueue.objects.create(
        config=config,
        name="aws_sns_1",  # This needs to correspond to the key in the `ACTION_BROKERS.message_brokers` dictionary
        conn_details={
          "endpoint_url": None,
          "aws_access_key_id": "my_access_key_id",
          "aws_secret_access_key": "my_secret_access_key",
          "region_name": "us-east-1"
        },
        parameters={
          "topic_arn": "arn:aws:sns:us-east-1:123456789012:my_topic"
        }
    )

In this example, the `conn_details` dictionary contains the connection details
required to connect to the AWS SNS service. The `parameters` dictionary
contains the topic ARN where messages will be sent.

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

Now, whenever a new sale is created, the AQS SNS action will be triggered.

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

- `myproject.settings.AWS_ACCESS_KEY_ID`: Stores the AWS access key ID.
- `myproject.settings.AWS_SECRET_ACCESS_KEY`: Stores the AWS secret access key.
- `myproject.settings.AWS_REGION_NAME`: Stores the AWS region name.
- `myproject.settings.AWS_SNS_TOPIC_ARN`: Stores the AWS SNS topic ARN.

You can use these in the `conn_details` field as follows:

.. code-block:: python

    from action_triggers.models import MessageBrokerQueue

    aws_sns_action = MessageBrokerQueue.objects.create(
        config=config,
        name="aws_sns_1",
        conn_details={
          "endpoint_url": None,
          "aws_access_key_id": "{{ myproject.settings.AWS_ACCESS_KEY_ID }}",
          "aws_secret_access_key": "{{ myproject.settings.AWS_SECRET_ACCESS_KEY }}",
          "region_name": "{{ myproject.settings.AWS_REGION_NAME }}"
        },
        parameters={
          "topic_arn": "{{ myproject.settings.AWS_SNS_TOPIC_ARN }}"
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
            'myproject.settings.AWS_ACCESS_KEY_ID',
            'myproject.settings.AWS_SECRET_ACCESS_KEY',
            'myproject.settings.AWS_REGION_NAME',
            'myproject.settings.AWS_SNS_TOPIC_ARN',
        ),
    }

This configuration ensures that the specified paths can be evaluated at
runtime.

---

By following these steps, you can securely and effectively set up AWS SNS as a
message broker in **Django Action Triggers**. For more advanced configurations,
refer to the related documentation sections.
