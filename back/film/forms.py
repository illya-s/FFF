from django import forms
from .models import *


class MediaCommentForm(forms.ModelForm):
    class Meta:
        model = MediaComment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, value in self.fields.items():
            value.widget.attrs['placeholder'] = value.label