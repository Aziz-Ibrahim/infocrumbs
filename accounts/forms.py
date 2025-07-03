from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth import get_user_model
from datetime import date

from .models import Profile, CustomUser


class CustomSignupForm(SignupForm):
    """
    Custom signup form to include additional fields like first name,
    last name, and date of birth, with validation for DOB.
    """
    first_name = forms.CharField(
        max_length=30,
        label="First Name",
        widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
        required=True
    )
    last_name = forms.CharField(
        max_length=30,
        label="Last Name",
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),
        required=True
    )
    date_of_birth = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={"type": "date"}),
        required=True,
        help_text="You must be at least 12 years old."
    )

    def clean_date_of_birth(self):
        """
        Custom clean method for 'date_of_birth' to validate age and
        prevent future dates.
        """
        dob = self.cleaned_data['date_of_birth']
        today = date.today()

        if dob > today:
            raise forms.ValidationError(
                "Date of birth cannot be in the future."
            )

        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )

        if age < 12:
            raise forms.ValidationError(
                "You must be at least 12 years old to sign up."
            )

        return dob

    def save(self, request):
        """
        Overrides the default save method to include first_name, last_name,
        and date_of_birth, and to create the associated Profile.
        """
        user = super().save(request)

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.date_of_birth = self.cleaned_data["date_of_birth"]

        user.save()

        Profile.objects.update_or_create(
            user=user,
            defaults={}
        )

        return user


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating a CustomUser's profile information, including
    first name, last name, email, and date of birth.

    Includes server-side validation for the date of birth to ensure
    it's not in the future and meets the minimum age requirement (12 years).
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        )
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'date_of_birth')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_date_of_birth(self):
        """
        Custom clean method for 'date_of_birth' to validate age and
        prevent future dates during profile updates.
        """
        dob = self.cleaned_data.get('date_of_birth')

        if dob: # Only validate if a date is provided
            today = date.today()

            # 1. Prevent future dates
            if dob > today:
                raise forms.ValidationError(
                    "Date of birth cannot be in the future."
                )

            # 2. Enforce minimum age (12 years)
            age = today.year - dob.year - (
                (today.month, today.day) < (dob.month, dob.day)
            )

            if age < 12:
                raise forms.ValidationError(
                    "You must be at least 12 years old."
                )
        return dob
