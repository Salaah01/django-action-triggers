from django.conf import settings

DB_TABLE_PREFIX = getattr(settings, "DB_TABLE_PREFIX", "action_triggers_")
