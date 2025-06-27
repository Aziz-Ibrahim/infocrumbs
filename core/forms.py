from django import forms


class ContactForm(forms.Form):
    """
    Form for users to send messages to the site administrator.
    Includes fields for name, email, subject, and message.
    """
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={'placeholder': 'Your Name', 'class': 'form-control'}
        ),
        help_text="Please enter your full name."
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'placeholder': 'Your Email Address', 'class': 'form-control'}
        ),
        help_text="We'll use this to reply to you."
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Subject of your message', 'class': 'form-control'
            }
        ),
        help_text="A brief summary of your inquiry."
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 5, 'placeholder': 'Your message here...',
                'class': 'form-control'
            }),
        help_text="Please provide detailed information so we can "
        "assist you better.",
        min_length=10  # Minimum characters for a message
    )

