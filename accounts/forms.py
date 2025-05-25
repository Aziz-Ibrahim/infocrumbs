from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth import get_user_model
from .models import Profile


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=30,
        label="First Name",
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        label="Last Name",
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    date_of_birth = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()

        Profile.objects.update_or_create(
            user=user,
            defaults={
                'date_of_birth': self.cleaned_data["date_of_birth"]
            }
        )

        return user
