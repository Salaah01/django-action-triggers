====================  ========  ==================================================================================================================
Field                 Type      Description
====================  ========  ==================================================================================================================
`broker_config_name`  `string`  A unique name for the broker configuration.
`broker_type`         `string`  The type of the broker. Can be either `rabbitmq` or `kafka`.
`conn_details`        `dict`    Connection details required to establish a connection with the broker, such as host, port, username, and password.
`params`              `dict`    Additional parameters specific to the broker, such as the name of the queue for RabbitMQ or the topic for Kafka.
====================  ========  ==================================================================================================================