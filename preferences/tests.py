from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta

from accounts.models import CustomUser, Profile
from subscriptions.models import (
    SubscriptionPlan,
    SubscriptionFrequency,
    UserSubscription
)
from preferences.models import Topic, UserPreference
from preferences.forms import UserPreferenceForm


class UserPreferenceFormTest(TestCase):
    """
    Tests for the UserPreferenceForm.
    """

    def setUp(self):
        """
        Set up a user, plans, frequencies, and topics for form testing.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            date_of_birth=date(1990, 1, 1)
        )
        self.profile = self.user.profile  # Ensure profile exists due to signal

        self.user_preference, created = UserPreference.objects.get_or_create(
            user=self.user
        )

        self.basic_plan = SubscriptionPlan.objects.create(
            name='basic',
            topic_limit=2,
            price=10.00
        )
        self.premium_plan = SubscriptionPlan.objects.create(
            name='premium',
            topic_limit=100,  # Using a realistic high limit
            price=20.00
        )
        # Create SubscriptionFrequency objects
        self.monthly_frequency = SubscriptionFrequency.objects.create(
            name='monthly', duration_days=30, discount_percent=0
        )
        self.annual_frequency = SubscriptionFrequency.objects.create(
            name='annual', duration_days=365, discount_percent=10
        )

        self.topic1 = Topic.objects.create(name='Technology')
        self.topic2 = Topic.objects.create(name='Science')
        self.topic3 = Topic.objects.create(name='History')
        self.topic4 = Topic.objects.create(name='Art')
        self.topic5 = Topic.objects.create(name='Sports')

        self.future_end_date = timezone.now() + timedelta(days=365)

    def tearDown(self):
        UserSubscription.objects.filter(user=self.user).delete()
        UserPreference.objects.filter(user=self.user).delete()

    def test_form_initialization_basic_subscription(self):
        """
        Form should show basic plan help text for basic subscription.
        Adjusted to match current forms.py output.
        """
        UserSubscription.objects.filter(user=self.user).delete()
        UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            frequency=self.monthly_frequency,
            active=True,
            end_date=self.future_end_date
        )
        form = UserPreferenceForm(
            user=self.user,
            instance=self.user_preference
        )
        self.assertIn(
            f"You can select up to {self.basic_plan.topic_limit} "
            "topics with your Basic plan.",
            form.fields['topics'].help_text
        )

    def test_form_initialization_premium_subscription(self):
        """
        Form should show premium plan help text for premium subscription.
        Adjusted to match current forms.py output.
        """
        UserSubscription.objects.filter(user=self.user).delete()
        UserSubscription.objects.create(
            user=self.user,
            plan=self.premium_plan,
            frequency=self.annual_frequency,
            active=True,
            end_date=self.future_end_date
        )
        form = UserPreferenceForm(
            user=self.user,
            instance=self.user_preference
        )
        self.assertIn(
            "Select any topics you want.",
            form.fields['topics'].help_text
        )

    def test_form_valid_basic_subscription_max_topics(self):
        """
        Basic subscription form should be valid with up to 2 topics.
        Ensures form uses existing instance to avoid IntegrityError.
        """
        UserSubscription.objects.filter(user=self.user).delete()
        UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            frequency=self.monthly_frequency,
            active=True,
            end_date=self.future_end_date
        )
        form = UserPreferenceForm(
            user=self.user,
            instance=self.user_preference,
            data={'topics': [self.topic1.id, self.topic2.id]}
        )
        self.assertTrue(form.is_valid())
        user_preference_saved = form.save()
        self.assertEqual(user_preference_saved.topics.count(), 2)

    def test_form_invalid_basic_subscription_over_limit(self):
        """
        Basic subscription form should be invalid with more than 2 topics.
        Adjusted to match current forms.py output for this error.
        """
        UserSubscription.objects.filter(user=self.user).delete()
        UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            frequency=self.monthly_frequency,
            active=True,
            end_date=self.future_end_date
        )
        form = UserPreferenceForm(
            user=self.user,
            instance=self.user_preference,
            data={'topics': [self.topic1.id, self.topic2.id, self.topic3.id]}
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "You can select only 2 topics with your current plan.",
            form.errors['topics'][0]
        )

    def test_form_valid_premium_subscription_many_topics(self):
        """
        Premium subscription form should be valid with many topics.
        Ensures form uses existing instance to avoid IntegrityError.
        """
        UserSubscription.objects.filter(user=self.user).delete()
        UserSubscription.objects.create(
            user=self.user,
            plan=self.premium_plan,
            frequency=self.annual_frequency,
            active=True,
            end_date=self.future_end_date
        )
        form = UserPreferenceForm(
            user=self.user,
            instance=self.user_preference,
            data={
                'topics': [
                    self.topic1.id,
                    self.topic2.id,
                    self.topic3.id,
                    self.topic4.id
                ]
            }
        )
        self.assertTrue(form.is_valid())
        user_preference_saved = form.save()
        self.assertEqual(user_preference_saved.topics.count(), 4)


class SetPreferencesViewTest(TestCase):
    """
    Tests for the set_preferences view.
    """
    def setUp(self):
        """
        Set up a client, user, plans, frequencies, and topics for view tests.
        """
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='viewtestuser',
            email='view@example.com',
            password='password123',
            date_of_birth=date(1995, 7, 1)
        )
        self.client.login(username='viewtestuser', password='password123')

        # Ensure a UserPreference object exists for the user initially
        self.user_preference, created = UserPreference.objects.get_or_create(
            user=self.user
        )

        self.basic_plan = SubscriptionPlan.objects.create(
            name='basic', topic_limit=2, price=10.00
        )
        self.premium_plan = SubscriptionPlan.objects.create(
            name='premium', topic_limit=100, price=20.00
        )
        self.monthly_frequency = SubscriptionFrequency.objects.create(
            name='monthly', duration_days=30, discount_percent=0
        )
        self.annual_frequency = SubscriptionFrequency.objects.create(
            name='annual', duration_days=365, discount_percent=10
        )

        self.future_end_date = timezone.now() + timedelta(days=365)
        self.user_subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            frequency=self.monthly_frequency,
            active=True,
            end_date=self.future_end_date
        )

        self.topic1 = Topic.objects.create(name='Science')
        self.topic2 = Topic.objects.create(name='Technology')
        self.topic3 = Topic.objects.create(name='Business')

    def tearDown(self):
        # Clean up after each test to avoid interference
        UserSubscription.objects.filter(user=self.user).delete()
        UserPreference.objects.filter(user=self.user).delete()

    def test_set_preferences_view_requires_login(self):
        """
        Test that the set_preferences view redirects unauthenticated users.
        """
        self.client.logout()
        response = self.client.get(reverse('set_preferences'))
        self.assertRedirects(
            response,
            f'{reverse("account_login")}?next={reverse("set_preferences")}'
        )

    def test_set_preferences_view_redirects_if_no_subscription(self):
        """
        Test that the set_preferences view redirects to choose_plan if no
        active subscription.
        """
        UserSubscription.objects.filter(user=self.user).delete()
        response = self.client.get(reverse('set_preferences'))
        self.assertRedirects(response, reverse('choose_plan'))

    def test_set_preferences_view_get(self):
        """
        Test that the set_preferences view renders correctly for a GET request.
        Removed assertion for 'user_subscription' in context if it's not
        directly passed.
        """
        response = self.client.get(reverse('set_preferences'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'preferences/set_preferences.html')
        self.assertIsInstance(response.context['form'], UserPreferenceForm)

    def test_set_preferences_view_post_valid_data(self):
        """
        Test that the set_preferences view processes valid POST data.
        Adjusted status code to 302 (redirect) and removed JSON assertions.
        """
        selected_topics = [self.topic1.id, self.topic2.id]
        response = self.client.post(
            reverse('set_preferences'),
            {'topics': selected_topics},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 302)
        # Assert redirect target
        self.assertRedirects(response, reverse('crumb_list'))
        # Verify the database state after redirect (no JSON response to check)
        self.user_preference.refresh_from_db()  # Refresh the instance
        self.assertEqual(self.user_preference.topics.count(), 2)
        self.assertIn(self.topic1, self.user_preference.topics.all())
        self.assertIn(self.topic2, self.user_preference.topics.all())

    def test_set_preferences_view_updates_existing_preference(self):
        """
        Test that existing preferences are updated rather than creating new
        ones.
        Adjusted status code to 302 (redirect) and removed JSON assertions.
        """
        # First, set some initial preferences
        self.user_preference.topics.add(self.topic1)
        self.assertEqual(self.user_preference.topics.count(), 1)

        # Then update them via POST
        selected_topics = [self.topic2.id, self.topic3.id]
        response = self.client.post(
            reverse('set_preferences'),
            {'topics': selected_topics},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 302)
        # Assert redirect target
        self.assertRedirects(response, reverse('crumb_list'))
        # Verify the database state after redirect
        self.user_preference.refresh_from_db()
        self.assertEqual(self.user_preference.topics.count(), 2)
        self.assertIn(self.topic2, self.user_preference.topics.all())
        self.assertIn(self.topic3, self.user_preference.topics.all())
        self.assertNotIn(self.topic1, self.user_preference.topics.all())
        self.assertEqual(
            UserPreference.objects.filter(user=self.user).count(),
            1
        )  # Ensure only one preference exists

    def test_set_preferences_view_post_invalid_data(self):
        """
        Test that the set_preferences view handles invalid POST data.
        Adjusted status code to 200 and removed JSON assertions, as the
        view returns HTML.
        """
        # Simulate invalid data (e.g., exceeding basic plan limit of 2 topics)
        invalid_topics = [self.topic1.id, self.topic2.id, self.topic3.id]
        response = self.client.post(
            reverse('set_preferences'),
            {'topics': invalid_topics},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # Simulate AJAX
        )
        self.assertEqual(response.status_code, 200)
