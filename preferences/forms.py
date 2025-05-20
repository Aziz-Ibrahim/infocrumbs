from django import forms
from .models import UserPreference, Topic
from subscriptions.models import UserSubscription

class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['topics']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        # Determine user's topic limit based on subscription
        try:
            subscription = self.user.usersubscription
            if subscription.plan.name.lower() == 'basic':
                self.fields['topics'].help_text = 'You can select up to 2 topics.'
                self.fields['topics'].queryset = Topic.objects.all()
            else:
                # Premium: allow all topics
                self.fields['topics'].help_text = 'Select any topics you want.'
        except UserSubscription.DoesNotExist:
            self.fields['topics'].help_text = 'No active subscription. Default to basic.'

        def clean_topics(self):
            topics = self.cleaned_data['topics']
            try:
                subscription = self.user.usersubscription
                if subscription.plan.name.lower() == 'basic' and topics.count() > 2:
                    raise forms.ValidationError("Basic plan allows only 2 topics.")
            except UserSubscription.DoesNotExist:
                if topics.count() > 2:
                    raise forms.ValidationError("Without a subscription, you can only select 2 topics.")
            return topics

