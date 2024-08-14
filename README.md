# Django Action Triggers (In Development)

## Description

Django Action Triggers is a Django application that allows the user to trigger actions based on changes in the database.
These actions may be hitting a webhook, adding a message to a queue.

These triggers can be triggered either in the code, or by the UI in the Django admin interface.

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

If you intent on using the API, add the following to your `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('api/action-triggers/', include('action_triggers.urls')),
    ...
]
```


### Usage

The application will allow users to create triggers and actions in the Django admin or via the API.

#### API Specifications

The API specifications are below illustrate how to interact with the API and how `webhook` and `queue` actions are defined.


```ts
{
  "trigger": {
    "signals": string[]
    "models": {
      "app_label": string,
      "model_name": string,
    }[],
  }
  "webhooks"?: {
    "url": string,
    "method": "GET" | "POST" | "PUT" | "DELETE",
    "headers"?: {
      [key: string]: string
    },
  }[],
  "msg_broker_queues"?: {
    "broker_config_name": string,
    "connection_details"?: {
      [key: string]: string
    },
    "parameters"?: {
      [key: string]: string
    }
  }[],
  "active": boolean,
  "payload"?: {
    [key: string]: string
  }
}
```

##### API constraints

| Field             | Constraint                                                           |
| ----------------- | -------------------------------------------------------------------- |
| `trigger.signals` | Allowed values: `pre_save`, `post_save`, `pre_delete`, `post_delete` |


##### Field Descriptions

| Field                                  | Type                  | Description                                                                                                                                                                |
| -------------------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `trigger.signal`                       | `string[]`            | The list of signals that will trigger the action.                                                                                                                          |
| `trigger.models`                       | `object[]`            | The list of models that will trigger the action.                                                                                                                           |
| `trigger.models.app_label`             | `string`              | The app label of the model that will trigger the action.                                                                                                                   |
| `trigger.models.model_name`            | `string`              | The model name that will trigger the action.                                                                                                                               |
| `webhooks`                             | `object[]` (optional) | The list of webhooks that will be triggered.                                                                                                                               |
| `webhooks.url`                         | `string`              | The URL of the webhook.                                                                                                                                                    |
| `webhooks.method`                      | `string`              | The HTTP method of the webhook.                                                                                                                                            |
| `webhooks.headers`                     | `object[]` (optional) | A key-value pair of headers that will be sent with the webhook. The value can receive the path to a callable that will be evaluated at runtime.                            |
| `msg_broker_queues`                    | `object[]` (optional) | The list of queues that will be receive the message.                                                                                                                       |
| `msg_broker_queues.broker_config_name` | `string`              | The name of the queue as defined in `settings.py.ACTION_TRIGGERS.brokers`                                                                                                  |
| `msg_broker_queues.parameters`         | `object[]` (optional) | A key-value pair of parameters that will be sent with the message. The value can receive the path to a callable that will be evaluated at runtime.                         |
| `active`                               | `boolean`             | Whether the trigger is enabled or not.                                                                                                                                     |
| `payload`                              | `object[]` (optional) | A Django template like value. If the resulting value after any parsing is JSON-serializable, then the returning payload will be JSON, otherwise, it'll be just plain text. |


##### Using a callable in the `headers` and `parameters` fields

The `headers` and `parameters` fields can receive a callable that will be evaluated at runtime. This callable must be a string that represents the path to the callable. In order for the application to recognise the value as a callable, the value must be wrapped in double curly braces.

For example, if you want to use the function `get_token` which resides in `myapp.utils`, you would use the following syntax:

```json
{
  "headers": {
    "Authorization": "Bearer {{ myapp.utils.get_token }}"
  }
}
```

The application will evaluate the string `myapp.utils.get_token` and call the function `get_token` from the `myapp.utils` module.

**Limitations**

* Must be a callable that returns a JSON serializable object.
* The callable must be a string that represents the path to the callable.
* Cannot point to a variable (must be a callable).
* Cannot pass arguments to the callable.

##### Traversing the model relation in the `payload` field

`django-action-triggers` allows you to start off with the model instance (`instance`) that triggered the action and traverse the model relation to get the data you want to send to the webhook or queue. 

Let's imagine we have the following models:

```python

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()


class Sale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
```

We can then create the following trigger:

```json
{
  "action": "new_sale",
  "customer_name": "{{ instance.customer.name }}",
  "product_name": "{{ instance.product.name }}",
}
```

The application will evaluate the string `instance.customer.name` and `instance.product.name` and get the name of the customer and product respectively. An example of the payload that will be sent to the webhook or queue is:

```json
{
  "action": "new_sale",
  "customer_name": "John Doe",
  "product_name": "Product 1",
}
```

### Examples

#### Example 1: Create a trigger that will hit a webhook when a `User` object is created, updated or deleted

```json

{
  "trigger": {
    "signals": ["post_save", "post_delete"],
    "models": [
      {
        "app_label": "auth",
        "model_name": "User"
      }
    ]
  },
  "webhooks": [
    {
      "url": "https://my-webhook.com",
      "method": "POST",
      "headers": {
        "Authorization": "Bearer {{ myapp.utils.get_token }}"
      }
    }
  ],
  "active": true
}
```

#### Example 2: Create a trigger that will hit some webhooks and add a message to some queues when the `Product` or `Sale` object is created/updated.

```json
{
  "trigger": {
    "signals": ["post_save"],
    "models": [
      {
        "app_label": "myapp",
        "model_name": "Product"
      },
      {
        "app_label": "myapp",
        "model_name": "Sale"
      }
    ]
  },
  "webhooks": [
    {
      "url": "https://my-webhook.com",
      "method": "POST",
      "headers": {
        "Authorization": "Bearer {{ myapp.utils.get_token }}"
      }
    },
    {
      "url": "https://my-other-webhook.com",
      "method": "POST",
      "headers": {
        "Authorization": "Bearer {{ myapp.utils.get_token }}"
      }
    }
  ],
  "msg_broker_queues": [
    {
      "broker_config_name": "my-queue",
      "parameters": {
        "product_id": "{{ myapp.utils.get_product_id }}"
      }
    },
    {
      "broker_config_name": "my-other-queue",
      "parameters": {
        "sale_id": "{{ myapp.utils.get_sale_id }}"
      }
    }
  ],
  "active": true
}
```

#### Example 3: Create a trigger that will hit a webhook when a `Sale` object is created/updated and send the customer and product name.

```json
{
  "trigger": {
    "signals": ["post_save"],
    "models": [
      {
        "app_label": "myapp",
        "model_name": "Sale"
      }
    ]
  },
  "webhooks": [
    {
      "url": "https://my-webhook.com",
      "method": "POST",
      "headers": {
        "Authorization": "Bearer {{ myapp.utils.get_token }}"
      }
    }
  ],
  "active": true,
  "payload": {
    "action": "new_sale",
    "customer_name": "{{ instance.customer.name }}",
    "product_name": "{{ instance.product.name }}"
  }
}
```