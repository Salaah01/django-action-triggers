from django import forms

from action_triggers.conf import get_content_type_choices
from action_triggers.models import Config


class ConfigAdminForm(forms.ModelForm):
    class Meta:
        model = Config
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content_types"].queryset = get_content_type_choices()
