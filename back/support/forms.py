from django import forms
from .models import CopyrightRequest, CopyrightResponse, SupportRequest


class CopyrightRequestForm(forms.ModelForm):
    class Meta:
        model = CopyrightRequest
        fields = [
            "full_name", "email", "company", "message",
            "links_to_remove", "proof_document_url",
            "takedown_explanation_text", "attachment"
        ]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
            "links_to_remove": forms.Textarea(attrs={"rows": 4}),
            "takedown_explanation_text": forms.Textarea(attrs={"rows": 4}),
        }


class CopyrightResponseForm(forms.ModelForm):
    class Meta:
        model = CopyrightResponse
        fields = ["response_text", "is_sent"]
        widgets = {
            "response_text": forms.Textarea(attrs={"rows": 4}),
        }


class SupportRequestForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ["full_name", "email", "subject", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
        }
