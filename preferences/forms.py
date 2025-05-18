from django import forms
from .models import UserPreference

class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['topics']
        widgets = {
            'topics': forms.CheckboxSelectMultiple
        }
