
# Django Action Triggers (In Development)

## Table of Contents
- [Django Action Triggers (In Development)](#django-action-triggers-in-development)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Key Features](#key-features)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Example Scenarios](#example-scenarios)
    - [Example 1: Webhook Trigger on User Creation/Update/Deletion](#example-1-webhook-trigger-on-user-creationupdatedeletion)
    - [Example 2: Webhooks and Message Queues on Product and Sale Creation/Update](#example-2-webhooks-and-message-queues-on-product-and-sale-creationupdate)
  - [Documentation](#documentation)
  - [License](#license)


## Description

**Django Action Triggers** is a Django application that allows you to trigger actions based on changes in your database. These actions can include sending a request to a webhook or adding a message to a message broker such as Kafka or RabbitMQ.

This application is highly flexible and can be configured via code or through the Django admin interface.

## Key Features

- **Database-Driven Triggers**: Automatically trigger actions based on model events (e.g., save, delete).
- **Webhook Integration**: Send HTTP requests to external services when triggers are activated.
- **Message Broker Integration**: Send messages to messaging brokers like Kafka and RabbitMQ.
- **Extensible**: Easily extend to support custom triggers and actions.
- **Secure Dynamic Configuration**: Dynamically set values at runtime for secure and flexible configuration.

## Installation

To install the package, run the following command:

```bash
pip install django-action-triggers
```

Then, add the following to your `INSTALLED_APPS` in your Django settings:

```python
INSTALLED_APPS = [
    ...
    'action_triggers',
    ...
]
```

If you plan on using the API, add the following to your `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('api/action-triggers/', include('action_triggers.urls')),
    ...
]
```

## Usage

Once installed, you can create triggers and actions using the Django admin interface or programmatically through the API.

For detailed usage instructions, configuration options, and examples, please refer to the [official documentation](https://salaah01.github.io/django-action-triggers/).

## Example Scenarios

### Example 1: Webhook Trigger on User Creation/Update/Deletion

Trigger a webhook whenever a `User` model is created, updated, or deleted:

```json
{
  "config_signals": [
    {"signal": "post_save"},
    {"signal": "post_delete"}
  ],
  "content_types": [
    {
      "app_label": "auth",
      "model_name": "User"
    }
  ],
  "webhooks": [
    {
      "url": "https://my-webhook.com",
      "http_method": "POST",
      "headers": {
        "Authorization": "Bearer {{ myapp.utils.get_token }}"
      }
    }
  ],
  "active": true
}

```

### Example 2: Webhooks and Message Queues on Product and Sale Creation/Update

Trigger multiple webhooks and add messages to queues when `Product` or `Sale` models are created or updated:

```json
{
  "config_signals": [
    {"signal": "post_save"}
  ],
  "content_types": [
    {
      "app_label": "myapp",
      "model_name": "Product"
    },
    {
      "app_label": "myapp",
      "model_name": "Sale"
    }
  ],
  "webhooks": [
    {
      "url": "https://my-webhook.com",
      "http_method": "POST",
      "headers": {
        "Authorization": "Bearer {{ myapp.utils.get_token }}"
      }
    },
    {
      "url": "https://my-other-webhook.com",
      "http_method": "POST",
      "headers": {
        "Authorization": "Bearer {{ myapp.utils.get_token }}"
      }
    }
  ],
  "msg_broker_queues": [
    {
      "name": "my-msg-broker-config",
      "parameters": {
        "product_id": "{{ myapp.utils.get_product_id }}"
      }
    },
    {
      "name": "my-other-msg-broker-config",
      "parameters": {
        "sale_id": "{{ myapp.utils.get_sale_id }}"
      }
    }
  ],
  "active": true
}
```

## Documentation

For detailed documentation, including setup, configuration options, API specifications, and more examples, please refer to the [official documentation](https://salaah01.github.io/django-action-triggers/).


## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
