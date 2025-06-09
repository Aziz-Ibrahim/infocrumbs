from django import forms

from subscriptions.models import UserSubscription
from .models import UserPreference, Topic


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

        self.selected_topic_ids = set()
        if self.instance and self.instance.pk:
            self.selected_topic_ids = set(self.instance.topics.values_list(
                'id', flat=True))

        self.topic_limit = None

        try:
            subscription = self.user.usersubscription
            if subscription.plan.name.lower() == 'basic':
                self.topic_limit = 2
                self.fields['topics'].help_text = (
                    f'You can select up to {self.topic_limit} topics with '
                    'your Basic plan.'
                )
            else:
                self.fields['topics'].help_text = (
                    'Select any topics you want.'
                )
        except UserSubscription.DoesNotExist:
            self.topic_limit = 2
            self.fields['topics'].help_text = (
                f'No active subscription found. You can select up to '
                f'{self.topic_limit} topics.'
            )

    def clean_topics(self):
        """
        Custom clean method for 'topics' field to enforce
        subscription-based topic limits on the server-side.
        """
        topics = self.cleaned_data['topics']

        current_limit = None
        try:
            subscription = self.user.usersubscription
            if subscription.plan.name.lower() == 'basic':
                current_limit = 2
        except UserSubscription.DoesNotExist:
            current_limit = 2

        if current_limit is not None and topics.count() > current_limit:
            raise forms.ValidationError(
                f"You can select only {current_limit} topics with your "
                "current plan."
            )
        return topics