from action_triggers.base.config import ActionTriggerActionBase
from action_triggers.enums import ActionTriggerType


class BrokerBase(ActionTriggerActionBase):
    """Base class for a message broker. This class should be subclassed
    to implement the specific message broker.
    """

    action_trigger_type = ActionTriggerType.BROKERS
