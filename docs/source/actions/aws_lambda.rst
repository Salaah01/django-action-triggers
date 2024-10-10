==========
AWS Lambda
==========

**Django Action Triggers** supports invoking AWS Lambda functions. This section
guides you through configuring AWS Lambda into the project and creating
triggers that invoke AWS Lambda functions.

Installation
============

To the AWS Lambda integration, you will need to install an additional
package. This can be done by running the following command:

.. code-block:: bash

  pip install django-action-triggers[aws]

Configuration
=============

Before AWS Lambda functions can be invoked, the AWS Lambda action needs to be
configured in the Django settings.

.. include:: ../partials/note_ref_actions_configuration_guide.rst

AWS Lambda Configuration
------------------------

The following configuration options must be set in the Django settings to
configure the AWS Lambda action:

- `conn_details.endpoint_url`: The endpoint URL of the AWS Lambda service. If
  you are using AWS' Lambda service, you can set this to `None`. Otherwise, you
  can set this to the endpoint URL of the AWS Lambda service/emulator you are
  using.

- `params.FunctionName`: The name of the Lambda function to invoke.


Example Configuration in `settings.py`
--------------------------------------

Here is an example configuration for AWS Lambda:

.. code-block:: python

  ACTION_TRIGGERS = {
    "actions": {
      "my_lambda_action": {
        "action_type": "aws_lambda",
        "conn_details": {
          "endpoint_url": None
        },
        "params": {
          "FunctionName": "my_lambda_function"
        }
      }
    }
  }

Example Configuration in `settings.py` using `endpoint_url`
-----------------------------------------------------------

Here is an example configuration for AWS Lambda using the endpoint URL. This
can be useful when using a local instance of the AWS Lambda service:

.. code-block:: python

  ACTION_TRIGGERS = {
    "actions": {
      "my_lambda_action": {
        "action_type": "aws_lambda",
        "conn_details": {
          "endpoint_url": "localhost:4566",
          "region_name": "us-east-1",
        },
        "params": {
          "FunctionName": "my_lambda_function"
        }
      }
    }
  }


Creating an AWS Lambda Action
=============================

Once AWS Lambda is configured, you can create a trigger that invokes the AWS
Lambda function whenever the trigger is activated.

Scenario
--------

Suppose you have the following Django models:

.. include:: ../partials/django_models_for_scenarios.rst

Suppose you have an AWS Lambda function that sends an email to a user when a
trigger is activated. We'll call this function `send_email_to_user`.

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

Step 2: Create an `Action` Model Instance (AWS Lambda Action)
-------------------------------------------------------------

.. warning::
  Hardcoding sensitive information such as connection details is not
  recommended. In the next section, we will explore how to dynamically set
  these values using callables or variables at runtime.

.. code-block:: python
  
    from action_triggers.models import Action
  
    aws_lambda_action = Action.objects.create(
        config=config,
        name="my_lambda_action",  # This needs to correspond to a key in the `ACTION_TRIGGERS.actions` dictionary
        action_type="aws_lambda",
        conn_details={
          "endpoint_url": None,
          "aws_access_key_id": "my_access_key_id",
          "aws_secret_access_key": "my_secret_access_key",
          "region_name": "us-east-1"
        },
        params={
            "FunctionName": "send_email_to_user"
        }
    )

In this example, the `conn_details` dictionary contains the connection details
required to connect to the AWS Lambda service. The `params` dictionary contains
the name of the Lambda function to invoke.

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

Now, whenever a new sale is created, the AWS Lambda function will be invoked.

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
- `myproject.settings.AWS_FUNCTION_NAME`: Stores the AWS Lambda function name.

You can use these in the `conn_details` field as follows:

.. code-block:: python

    from action_triggers.models import Action

    aws_lambda_action = Action.objects.create(
        config=config,
        name="my_lambda_action",
        action_type="aws_lambda",
        conn_details={
          "endpoint_url": None,
          "aws_access_key_id": "{{ myproject.settings.AWS_ACCESS_KEY_ID }}",
          "aws_secret_access_key": "{{ myproject.settings.AWS_SECRET_ACCESS_KEY }}",
          "region_name": "{{ myproject.settings.AWS_REGION_NAME }}"
        },
        params={
            "FunctionName": "{{ myproject.settings.AWS_FUNCTION_NAME }}"
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
            'myproject.settings.AWS_FUNCTION_NAME',
        ),

This configuration ensures that the specified paths can be evaluated at
runtime.

---

By following these steps, you can securely and effectively set up AWS Lambda as
an action in **Django Action Triggers**. For more advanced configurations,
refer to the related documentation sections.
