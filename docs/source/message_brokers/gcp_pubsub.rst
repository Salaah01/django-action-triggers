.. _gcp_pubsub:

==================================
GCP Pub/Sub (Google Cloud Pub/Sub)
==================================

**Django Action Triggers** sending messages to a GCP Pub/Sub message broker.
This section guides you through configuring GCP Pub/Sub and creating triggers
that send messages to a GCP Pub/Sub broker.

Installation
============

To use GCP Pub/Sub as a message broker, you will need to install an additional
package. This can be done by running the following command:

.. code-block:: bash

  pip install django-action-triggers[gcp]

Configuration
=============

Before messages can be sent to a GCP Pub/Sub message broker, the broker needs
to be configured in the Django settings.

.. include:: ../partials/note_ref_message_brokers_configuration_guide.rst

GCP Pub/Sub Configuration
-------------------------

The following configuration options must be set in the Django settings to
configure the GCP Pub/Sub message broker:

- `conn_details.project`: The GCP project name.
- `conn_details.topic`: The topic where messages will be sent when a trigger is
  activated.

Example Configuration in `settings.py`
--------------------------------------

Here is an example configuration for GCP Pub/Sub:

.. code-block:: python

  ACTION_BROKERS = {
    "my_gcp_pubsub_broker": {
      "broker_type": "gcp_pubsub",
      "conn_details": {
        "project": "my-gcp-project",
        "topic": "my_topic"
      },
      "params": {}
    }
  }

In this configuration:
- The `my_gcp_pubsub_broker` is set to connect to the GCP project `my-gcp-project` and send messages to the `my_topic` topic.

Creating a GCP Pub/Sub Action
=============================

Once you have configured GCP Pub/Sub, you can create a trigger that sends
messages to the GCP Pub/Sub broker whenever the trigger is activated.

Scenario
--------

Suppose you have the following Django models:

.. include:: ../partials/django_models_for_scenarios.rst

Let's say you want to send a message to GCP Pub/Sub when a new sale is created.
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

Step 2: Create a `MessageBrokerQueue` Model Instance (GCP Pub/Sub Action)
-------------------------------------------------------------------------

Now, create a `MessageBrokerQueue` model instance to define the GCP Pub/Sub
action.


.. code-block:: python

    from action_triggers.models import MessageBrokerQueue

    gcp_pubsub_action = MessageBrokerQueue.objects.create(
      config=config,
      name="my_gcp_pubsub_broker",
      conn_details={
        "project": "my-gcp-project",
        "topic": "my_topic",
      },
      parameters={}
    )

In this example:
- The `gcp_pubsub_action` is set to send messages to the GCP project `my-gcp-project` and the `my_topic` topic.

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

Now, whenever a new sale is created, the GCP Pub/Sub action will be triggered.

---

By following these steps, you can configure your project to send messages to
GCP Pub/Sub using **Django Action Triggers**. For more advanced
configurations, refer to the related documentation sections.
