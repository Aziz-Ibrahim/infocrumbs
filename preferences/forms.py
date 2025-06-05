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

        subscription = self.user.usersubscription

        if subscription.plan.topic_limit is not None and \
           subscription.plan.topic_limit > 0:
            self.fields['topics'].help_text = (
                f'You can select up to {subscription.plan.topic_limit} topics.'
            )
            self.fields['topics'].queryset = Topic.objects.all()
        else:
            self.fields['topics'].help_text = (
                'Select any topics you want.'
            )


    def clean_topics(self):
        """
        Custom clean method for 'topics' field to enforce
        subscription-based topic limits.
        """
        topics = self.cleaned_data['topics']
        subscription = self.user.usersubscription

        if subscription.plan.topic_limit is not None and \
           topics.count() > subscription.plan.topic_limit:
            raise forms.ValidationError(
                f"{subscription.plan.get_name_display()} plan allows only "
                f"{subscription.plan.topic_limit} topics."
            )

        return topics