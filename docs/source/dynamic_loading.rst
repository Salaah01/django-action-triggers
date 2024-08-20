.. _dynamic-loading:

=====================================
Dynamically Loading Values at Runtime
=====================================

Often, you may want to fetch a value for a field dynamically. A common use case
for this is when you may want to call a function to fetch an API key that you
can then use in a request.

Django Action Triggers allows you to do this by providing a way to specify a
path to a callable or a variable that will be evaluated at runtime to fetch the
value.

This can be only achieved for the following fields:

- `webhooks.headers`
- `msg_broker_queues.connection_details`
- `msg_broker_queues.parameters`

Usage
=====

In order to be able to evaluate a value at runtime, the path to the callable or
variable must be specified in the field. The path must be a string that
represents the path to the callable or variable wrapped in curly braces.

For example, let's suppose our header for a webhook looks like this:

.. code-block:: json

    {
      "Content-Type": "application/json",
      "Authorization": "Bearer my-api-key"
    }

Let's imagine that we have a function in our Django project that fetches the
API key for us. We can specify the path to this function in the
`webhooks.headers` field like so:

.. code-block:: json

    {
      "Content-Type": "application/json",
      "Authorization": "Bearer {my_project.my_module.fetch_api_key}"
    }

Setup
=====

In order to use this feature, you must ensure that the callable or variable
that you are specifying in the field must be defined in the settings file.

Any callable or variable that you wish to be evaluated at runtime must be
defined in `ACTION_TRIGGER_SETTINGS.ALLOWED_DYNAMIC_IMPORT_PATHS`.

Using the example above, you would need to add the following to your settings
file:

.. code-block:: python

    ACTION_TRIGGER_SETTINGS = {
        ...
        'ALLOWED_DYNAMIC_IMPORT_PATHS': (
            'my_project.my_module.fetch_api_key',
        ),
        ...
    }

.. _dynamically-fetching-value-for-a-field-webhooks-headers:
