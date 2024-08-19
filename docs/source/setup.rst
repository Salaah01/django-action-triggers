Setup
=====

The following will describe how to setup the application so that you can use it
in your Django project once it has been installed.

.. note::

    This guide assumes that you have already installed the application. If you
    have not, please refer to the :ref:`installation` guide.


Configuration
-------------

To use the application, you will need to add it to your Django project's
``INSTALLED_APPS`` setting. This can be done by adding the following line to
your project's ``settings.py`` file:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'django_action_triggers',
        ...
    ]
