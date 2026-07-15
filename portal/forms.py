from django import forms

from core.models import PublicPage


class PublicPageForm(forms.ModelForm):
    class Meta:
        model = PublicPage
        fields = ["employer_name", "position_title", "notes", "is_published"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
