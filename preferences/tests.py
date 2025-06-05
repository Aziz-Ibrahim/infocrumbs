# preferences/tests.py

import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile # New import for dummy image

from accounts.models import CustomUser
from subscriptions.models import SubscriptionPlan, UserSubscription
from .models import UserPreference, Topic
from .forms import UserPreferenceForm

# Define a minimal dummy image content for tests
DUMMY_IMAGE_CONTENT = b'GIF89a\x01\x00\x01\x00\x00\xff\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'


class UserPreferenceFormTest(TestCase):
    """
    Tests for the UserPreferenceForm.
    """

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='formuser', email='form@example.com',
            password='password123'
        )
        # Create Topics with dummy images
        self.topic1 = Topic.objects.create(name='Topic A', image=SimpleUploadedFile("topic_a.gif", DUMMY_IMAGE_CONTENT, content_type="image/gif"))
        self.topic2 = Topic.objects.create(name='Topic B', image=SimpleUploadedFile("topic_b.gif", DUMMY_IMAGE_CONTENT, content_type="image/gif"))
        self.topic3 = Topic.objects.create(name='Topic C', image=SimpleUploadedFile("topic_c.gif", DUMMY_IMAGE_CONTENT, content_type="image/gif"))
        self.topic4 = Topic.objects.create(name='Topic D', image=SimpleUploadedFile("topic_d.gif", DUMMY_IMAGE_CONTENT, content_type="image/gif"))

        self.basic_plan = SubscriptionPlan.objects.create(
            name='basic',
            price=10.00, topic_limit=2
        )
        self.premium_plan = SubscriptionPlan.objects.create(
            name='premium',
            price=20.00, topic_limit=12
        )
        self.future_end_date = timezone.now() + datetime.timedelta(days=30)

    def test_form_initialization_basic_subscription(self):
        """
        Form should show basic plan help text for basic subscription.
        """
        UserSubscription.objects.create(
            user=self.user, plan=self.basic_plan, active=True,
            end_date=self.future_end_date
        )
        form = UserPreferenceForm(user=self.user)
        self.assertIn(f'You can select up to {self.basic_plan.topic_limit} topics.',
                      form.fields['topics'].help_text)

    def test_form_initialization_premium_subscription(self):
        """
        Form should show premium plan help text for premium subscription.
        """
        UserSubscription.objects.create(
            user=self.user, plan=self.premium_plan, active=True,
            end_date=self.future_end_date
        )
        form = UserPreferenceForm(user=self.user)
        self.assertIn(f'You can select up to {self.premium_plan.topic_limit} topics.',
                      form.fields['topics'].help_text)

    def test_form_valid_basic_subscription_max_topics(self):
        """
        Basic subscription form should be valid with up to 2 topics.
        """
        UserSubscription.objects.create(
            user=self.user, plan=self.basic_plan, active=True,
            end_date=self.future_end_date
        )
        data = {'topics': [self.topic1.id, self.topic2.id]}
        form = UserPreferenceForm(data=data, user=self.user)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['topics'].count(), 2)

    def test_form_valid_premium_subscription_many_topics(self):
        """
        Premium subscription form should be valid with many topics (up to limit).
        """
        UserSubscription.objects.create(
            user=self.user, plan=self.premium_plan, active=True,
            end_date=self.future_end_date
        )
        # Create topics dynamically to reach just under the limit
        premium_topics_data = []
        for i in range(self.premium_plan.topic_limit):
            # Ensure new topics also have dummy images
            premium_topics_data.append(Topic.objects.create(name=f'Premium Topic {i}', image=SimpleUploadedFile(f"prem_topic_{i}.gif", DUMMY_IMAGE_CONTENT, content_type="image/gif")).id)

        data = {'topics': premium_topics_data}
        form = UserPreferenceForm(data=data, user=self.user)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['topics'].count(),
                         self.premium_plan.topic_limit)


    def test_form_invalid_basic_subscription_over_limit(self):
        """
        Basic subscription form should be invalid with more than 2 topics.
        """
        UserSubscription.objects.create(
            user=self.user, plan=self.basic_plan, active=True,
            end_date=self.future_end_date
        )
        data = {'topics': [self.topic1.id, self.topic2.id, self.topic3.id]}
        form = UserPreferenceForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn(f'{self.basic_plan.get_name_display()} plan allows only '
                      f'{self.basic_plan.topic_limit} topics.',
                      form.errors['topics'][0])

    def test_form_invalid_premium_subscription_over_limit(self):
        """
        Premium subscription form should be invalid if topics exceed its limit.
        """
        UserSubscription.objects.create(
            user=self.user, plan=self.premium_plan, active=True,
            end_date=self.future_end_date
        )
        # Create topics to exceed the premium limit (e.g., 13 topics for limit 12)
        extra_topics = []
        for i in range(self.premium_plan.topic_limit + 1):
            # Ensure new topics also have dummy images
            extra_topics.append(Topic.objects.create(name=f'Extra Topic {i}', image=SimpleUploadedFile(f"extra_topic_{i}.gif", DUMMY_IMAGE_CONTENT, content_type="image/gif")))

        data = {'topics': [t.id for t in extra_topics]}
        form = UserPreferenceForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn(f'{self.premium_plan.get_name_display()} plan allows only '
                      f'{self.premium_plan.topic_limit} topics.',
                      form.errors['topics'][0])


class SetPreferencesViewTest(TestCase):
    """
    Tests for the set_preferences view.
    """

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='viewuser', email='view@example.com',
            password='password123'
        )
        # Create Topics with dummy images
        self.topic1 = Topic.objects.create(name='Coding', image=SimpleUploadedFile("topic_coding.gif", DUMMY_IMAGE_CONTENT, content_type="image/gif"))
        self.topic2 = Topic.objects.create(name='Design', image=SimpleUploadedFile("topic_design.gif", DUMMY_IMAGE_CONTENT, content_type="image/gif"))
        self.topic3 = Topic.objects.create(name='Marketing', image=SimpleUploadedFile("topic_marketing.gif", DUMMY_IMAGE_CONTENT, content_type="image/gif"))

        self.basic_plan = SubscriptionPlan.objects.create(
            name='basic',
            price=10.00, topic_limit=2
        )
        self.future_end_date = timezone.now() + datetime.timedelta(days=30)
        self.set_preferences_url = reverse('set_preferences')
        self.client.login(username='viewuser', password='password123')

        # Store the created UserPreference instance directly
        self.user_preference = UserPreference.objects.create(user=self.user)
        # Create an active UserSubscription for the test user by default
        self.user_subscription = UserSubscription.objects.create(
            user=self.user, plan=self.basic_plan, active=True,
            end_date=self.future_end_date
        )

    def test_set_preferences_view_get(self):
        """
        Test that the set_preferences view renders correctly for a GET request.
        """
        response = self.client.get(self.set_preferences_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'preferences/set_preferences.html')
        self.assertIsInstance(response.context['form'], UserPreferenceForm)
        self.assertIn('form', response.context)

    def test_set_preferences_view_post_valid_data(self):
        """
        Test that the set_preferences view processes valid POST data.
        """
        # UserSubscription is already created in setUp for this user
        data = {'topics': [self.topic1.id, self.topic2.id]}
        response = self.client.post(self.set_preferences_url, data)
        # Check if topics are updated
        self.user_preference.refresh_from_db()
        self.assertEqual(self.user_preference.topics.count(), 2)
        # Check redirection
        self.assertRedirects(response, reverse('home'))

    def test_set_preferences_view_post_invalid_data(self):
        """
        Test that the set_preferences view handles invalid POST data.
        """
        # UserSubscription is already created in setUp for this user
        # Provide too many topics for a basic plan
        data = {'topics': [self.topic1.id, self.topic2.id, self.topic3.id]}
        response = self.client.post(self.set_preferences_url, data)
        # Should render the form again with errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'preferences/set_preferences.html')
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('topics', response.context['form'].errors)

    def test_set_preferences_view_requires_login(self):
        """
        Test that the set_preferences view redirects unauthenticated users.
        """
        self.client.logout()  # Log out the user
        response = self.client.get(self.set_preferences_url)
        self.assertRedirects(response, reverse('account_login') + '?next=' + self.set_preferences_url)

    def test_set_preferences_view_redirects_if_no_subscription(self):
        """
        Test that the set_preferences view redirects to choose_plan if no active subscription.
        """
        # Delete the subscription created in setUp for this specific test
        self.user_subscription.delete() # Using the stored instance for deletion

        response = self.client.get(self.set_preferences_url)
        self.assertRedirects(response, reverse('choose_plan'))

    def test_set_preferences_view_updates_existing_preference(self):
        """
        Test that existing preferences are updated rather than new ones created.
        """
        # UserSubscription is already created in setUp for this user
        # Set an initial preference using the stored self.user_preference
        self.user_preference.topics.add(self.topic1)
        self.assertEqual(self.user_preference.topics.count(), 1)

        # Update the preference with new topics
        data = {'topics': [self.topic2.id, self.topic3.id]}
        response = self.client.post(self.set_preferences_url, data)

        self.user_preference.refresh_from_db()
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(self.user_preference.topics.count(), 2)
        self.assertIn(self.topic2, self.user_preference.topics.all())
        self.assertIn(self.topic3, self.user_preference.topics.all())
        self.assertNotIn(self.topic1, self.user_preference.topics.all())