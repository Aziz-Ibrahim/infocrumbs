from django import forms

from .models import UserPreference, Topic
from subscriptions.models import UserSubscription


class UserPreferenceForm(forms.ModelForm):
    """
    Form for users to set their topic preferences,
    with limits based on their subscription plan.
    """
    class Meta:
        model = UserPreference
        fields = ['topics']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        # Determine user's topic limit based on subscription
        try:
            subscription = self.user.usersubscription
            # Check for specific 'Basic Plan Type' name
            if subscription.plan.name.lower() == 'basic plan type':
                self.fields['topics'].help_text = (
                    'You can select up to 2 topics.'
                )
                self.fields['topics'].queryset = Topic.objects.all()
            else:  # Covers premium or any other plan
                self.fields['topics'].help_text = (
                    'Select any topics you want.'
                )
        except UserSubscription.DoesNotExist:
            self.fields['topics'].help_text = (
                'No active subscription. Default to basic.'
            )

    def clean_topics(self):
        """
        Custom clean method for 'topics' field to enforce
        subscription-based topic limits.
        """
        topics = self.cleaned_data['topics']
        try:
            subscription = self.user.usersubscription
            # Explicitly check for 'Basic Plan Type' and its limit of 2
            if subscription.plan.name.lower() == 'basic plan type':
                if topics.count() > 2:
                    raise forms.ValidationError(
                        "Basic plan allows only 2 topics."
                    )
            # No specific over-limit validation for premium yet

        except UserSubscription.DoesNotExist:
            # For users without a subscription, limit to 2 topics
            if topics.count() > 2:
                raise forms.ValidationError(
                    "Without a subscription, you can only select 2 topics."
                )
        return topics