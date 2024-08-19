====================  ========  ==================================================================================================================================================================
Field                 Type      Description
====================  ========  ==================================================================================================================================================================
`broker_config_name`  `string`  A unique name for the broker configuration.
`broker_type`         `string`  The type of the broker. Can be either `rabbitmq` or `kafka`.
`conn_details`        `dict`    A key-value pair of connection details that will be used to connect to the broker. The value can receive the path to a callable that will be evaluated at runtime.
`params`              `dict`    A key-value pair of parameters that will be used to configure the broker. The value can receive the path to a callable that will be evaluated at runtime.
====================  ========  ==================================================================================================================================================================