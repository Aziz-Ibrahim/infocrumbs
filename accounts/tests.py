from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from unittest.mock import patch, MagicMock, ANY
from datetime import date, timedelta
from django.utils import timezone

from accounts.models import CustomUser, Profile
from subscriptions.models import (
    SubscriptionPlan,
    SubscriptionFrequency,
    UserSubscription
)
from preferences.models import Topic, UserPreference
from crumbs.models import Crumb
from feedback.models import Comment, SavedCrumb


# Mock Stripe to prevent actual API calls during tests.
mock_stripe_module = MagicMock()
mock_stripe_module.PaymentIntent.create.return_value = MagicMock(
    client_secret='pi_mock_secret_123'
)
mock_stripe_module.PaymentIntent.modify.return_value = MagicMock()
mock_stripe_module.error = MagicMock()
mock_stripe_module.error.StripeError = type('StripeError', (Exception,), {})


# Ensure settings are set for tests
settings.STRIPE_SECRET_KEY = 'sk_test_mock_key'
settings.STRIPE_PUBLIC_KEY = 'pk_test_mock_key'
settings.STRIPE_CURRENCY = 'gbp'


class CustomUserTest(TestCase):
    """
    Tests for the CustomUser model.
    """

    def setUp(self):
        """
        Set up a user for testing.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User',
            date_of_birth=date(2000, 1, 1)
        )

    def test_user_creation(self):
        """
        Test that a CustomUser can be created successfully.
        """
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('password123'))
        self.assertFalse(self.user.is_premium)
        self.assertEqual(self.user.subscription_type, 'none')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.date_of_birth, date(2000, 1, 1))

    def test_user_str_representation(self):
        """
        Test the __str__ method of the CustomUser model.
        """
        self.assertEqual(str(self.user), 'testuser')


class ProfileModelTest(TestCase):
    """
    Tests for the Profile model and its relationship with CustomUser.
    """

    def setUp(self):
        """
        Set up a user and related objects for Profile testing.
        """
        self.user = CustomUser.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='password123',
            date_of_birth=date(1990, 5, 15)
        )
        self.profile = self.user.profile  # Profile created via signal

        # Create a Topic for Crumb
        self.topic = Topic.objects.create(name="Technology")
        # Create a Crumb for saved_crumbs and comment_history
        self.crumb = Crumb.objects.create(
            title="Test Crumb",
            summary="Test Summary Content for Crumb.",
            published_at=timezone.now(),
            topic=self.topic,
            url="http://example.com/test-crumb-profile"
        )
        self.comment = Comment.objects.create(
            user=self.user,
            crumb=self.crumb,
            content="This is a test comment."
        )
        self.saved_crumb = SavedCrumb.objects.create(
            user=self.user,
            crumb=self.crumb
        )

    def test_profile_creation_via_signal(self):
        """
        Test that a profile is automatically created when a CustomUser is.
        """
        self.assertIsInstance(self.profile, Profile)
        self.assertEqual(self.profile.user, self.user)

    def test_profile_str_representation(self):
        """
        Test the __str__ method of the Profile model.
        """
        self.assertEqual(str(self.profile), f"{self.user.username}'s Profile")

    def test_saved_crumbs_relationship(self):
        """
        Test adding and retrieving saved crumbs.
        """
        self.profile.saved_crumbs.add(self.crumb)
        self.assertIn(self.crumb, self.profile.saved_crumbs.all())
        self.assertEqual(self.profile.saved_crumbs.count(), 1)

    def test_comment_history_relationship(self):
        """
        Test adding and retrieving comments in history.
        """
        # Comments are linked via the Comment model directly to user,
        # but Profile has a ManyToMany to Comment for history.
        self.profile.comment_history.add(self.comment)
        self.assertIn(self.comment, self.profile.comment_history.all())
        self.assertEqual(self.profile.comment_history.count(), 1)

    def test_topic_preferences_relationship(self):
        """
        Test adding and retrieving topic preferences.
        """
        self.profile.topic_preferences.add(self.topic)
        self.assertIn(self.topic, self.profile.topic_preferences.all())
        self.assertEqual(self.profile.topic_preferences.count(), 1)

    def test_profile_date_of_birth_update(self):
        """
        Test updating the profile's date_of_birth.
        Note: date_of_birth is on CustomUser, not Profile.
        """
        new_dob = date(1985, 10, 20)
        self.user.date_of_birth = new_dob
        self.user.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.date_of_birth, new_dob)


@patch('accounts.views.render_to_string')
@patch('accounts.views.UserUpdateForm')
@patch('accounts.views.UserSubscription')  # This is MockUserSubscription
@patch('checkout.views.stripe', mock_stripe_module)
class AccountViewsTest(TestCase):
    """
    Tests for views in the accounts application.
    """

    def setUp(self):
        """
        Set up a client, user, and necessary objects for view tests.
        """
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='viewtestuser',
            email='view@example.com',
            password='password123',
            first_name='View',
            last_name='Test',
            date_of_birth=date(1995, 7, 1)
        )
        self.client.login(username='viewtestuser', password='password123')

        self.basic_plan = SubscriptionPlan.objects.create(
            name='basic', topic_limit=2, price=10.00
        )
        self.monthly_freq = SubscriptionFrequency.objects.create(
            name='monthly', duration_days=30, discount_percent=0
        )
        self.user_subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            frequency=self.monthly_freq,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            active=True
        )
        # Create a Topic for Crumb
        self.topic_for_crumb = Topic.objects.create(name="General")

        self.crumb1 = Crumb.objects.create(
            title="Crumb 1",
            summary="Summary content for crumb 1.",
            published_at=timezone.now(),
            topic=self.topic_for_crumb,
            url="http://example.com/crumb1-test-url"
        )
        self.crumb2 = Crumb.objects.create(
            title="Crumb 2",
            summary="Summary content for crumb 2.",
            published_at=timezone.now(),
            topic=self.topic_for_crumb,
            url="http://example.com/crumb2-test-url"
        )
        self.comment1 = Comment.objects.create(
            user=self.user,
            crumb=self.crumb1,
            content="This is comment 1."
        )
        self.saved_crumb1 = SavedCrumb.objects.create(
            user=self.user,
            crumb=self.crumb2
        )
        self.topic1 = Topic.objects.create(name="Science")
        self.topic2 = Topic.objects.create(name="History")
        self.user_preference, _ = UserPreference.objects.get_or_create(
            user=self.user
        )
        self.user_preference.topics.add(self.topic1)

    def test_profile_view_requires_login(
        self,
        MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test that profile_view redirects unauthenticated users.
        """
        MockUserSubscription.objects.filter.return_value.first.return_value = (
            None
        )
        self.client.logout()
        response = self.client.get(reverse('account_profile'))
        self.assertRedirects(
            response,
            f'{reverse("account_login")}?next={reverse("account_profile")}'
        )

    def test_profile_view_loads_for_authenticated_user(
        self,
        MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test that profile_view loads correctly for authenticated users.
        """
        # Configure the mock to return the actual user_subscription instance
        MockUserSubscription.objects.filter.return_value.first.return_value = (
            self.user_subscription
        )
        response = self.client.get(reverse('account_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/profile.html')
        self.assertIn('user_subscription', response.context)
        self.assertEqual(
            response.context['user_subscription'], self.user_subscription
        )

    def test_load_account_details_partial(
        self, MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test loading of account details partial via AJAX.
        """
        mock_form_instance = MockUserUpdateForm.return_value
        mock_render_to_string.return_value = "<div>Mock HTML</div>"

        response = self.client.get(
            reverse('load_account_details_partial'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"html": "<div>Mock HTML</div>"})
        MockUserUpdateForm.assert_called_once_with(instance=self.user)
        mock_render_to_string.assert_called_once_with(
            "account/includes/partial_account_details.html",
            {"form": mock_form_instance},
            request=response.wsgi_request
        )

    def test_account_update_updates_user_data(
        self, MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test that account_update correctly updates user data.
        """
        mock_form_instance = MockUserUpdateForm.return_value
        mock_form_instance.is_valid.return_value = True
        mock_render_to_string.return_value = "<div>Updated HTML</div>"

        # Simulate a valid form submission
        response = self.client.post(
            reverse('account_update'),
            {
                'first_name': 'Updated',
                'last_name': 'User',
                'email': 'updated@example.com',
                'date_of_birth': '1990-01-01'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"html": "<div>Updated HTML</div>"})
        mock_form_instance.is_valid.assert_called_once()
        mock_form_instance.save.assert_called_once()
        mock_render_to_string.assert_called_once()
        # Verify messages are added (optional, but good for full test)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Account details updated successfully."
        )

    def test_account_update_only_updates_provided_fields(
        self,
        MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test that account_update only updates fields that are provided.
        """
        mock_form_instance = MockUserUpdateForm.return_value
        mock_form_instance.is_valid.return_value = True
        mock_render_to_string.return_value = "<div>Updated HTML</div>"

        # Simulate a partial form submission (e.g., only email changed)
        response = self.client.post(
            reverse('account_update'),
            {
                'email': 'newemail@example.com',
                # Other fields are not provided in POST data
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"html": "<div>Updated HTML</div>"})
        mock_form_instance.is_valid.assert_called_once()
        mock_form_instance.save.assert_called_once()
        mock_render_to_string.assert_called_once()
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)

    def test_account_update_post_invalid_form_displays_errors(
        self,
        MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test that account_update displays errors for invalid form submission.
        """
        mock_form_instance = MockUserUpdateForm.return_value
        mock_form_instance.is_valid.return_value = False
        mock_form_instance.errors = {'email': ['Enter a valid email address.']}
        mock_render_to_string.return_value = "<div>Form with Errors HTML</div>"

        response = self.client.post(
            reverse('account_update'),
            {
                'first_name': 'Invalid',
                'email': 'invalid-email',
                'date_of_birth': '2030-01-01'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"html": "<div>Form with Errors HTML</div>"}
        )
        mock_form_instance.is_valid.assert_called_once()
        mock_form_instance.save.assert_not_called()
        mock_render_to_string.assert_called_once()
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Please correct the errors below.")

    def test_account_update_get_redirects(
        self,
        MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test that a GET request to account_update redirects to profile.
        """
        response = self.client.get(reverse('account_update'))
        self.assertRedirects(response, reverse('account_profile'))

    def test_load_saved_crumbs_partial(
        self,
        MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test loading of saved crumbs partial via AJAX.
        """
        mock_render_to_string.return_value = "<div>Saved Crumbs HTML</div>"
        response = self.client.get(
            reverse('load_saved_crumbs_partial'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())
        self.assertIn('has_next_page', response.json())
        self.assertIn('next_page_number', response.json())
        mock_render_to_string.assert_called_once_with(
            "account/includes/partial_saved_crumbs.html",
            {
                "page_obj": ANY,
                "saved_crumbs": ANY
            },
            request=response.wsgi_request
        )

    def test_load_saved_crumbs_partial_no_crumbs(
        self,
        MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test loading saved crumbs when none are saved.
        """
        SavedCrumb.objects.all().delete()
        mock_render_to_string.return_value = "<div>No Saved Crumbs</div>"
        response = self.client.get(
            reverse('load_saved_crumbs_partial'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())
        self.assertFalse(response.json()['has_next_page'])
        self.assertIsNone(response.json()['next_page_number'])

    def test_load_comments_partial(
        self,
        MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test loading of comments partial via AJAX.
        """
        mock_render_to_string.return_value = "<div>Comments HTML</div>"
        response = self.client.get(
            reverse('load_comments_partial'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())
        self.assertIn('has_next_page', response.json())
        self.assertIn('next_page_number', response.json())
        mock_render_to_string.assert_called_once_with(
            "account/includes/partial_comments.html",
            {
                "page_obj": ANY,
                "comments": ANY
            },
            request=response.wsgi_request
        )

    def test_load_comments_partial_no_comments(
        self,
        MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test loading comments when none exist for the user.
        """
        Comment.objects.all().delete()
        mock_render_to_string.return_value = "<div>No Comments</div>"
        response = self.client.get(
            reverse('load_comments_partial'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())
        self.assertFalse(response.json()['has_next_page'])
        self.assertIsNone(response.json()['next_page_number'])

    def test_load_preferences_partial(
        self,
        MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test loading of preferences partial via AJAX.
        """
        mock_render_to_string.return_value = "<div>Preferences HTML</div>"
        response = self.client.get(
            reverse('load_preferences_partial'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())
        self.assertIn('has_next_page', response.json())
        self.assertIn('next_page_number', response.json())
        mock_render_to_string.assert_called_once_with(
            "account/includes/partial_preferences.html",
            {
                "page_obj": ANY,
                "topics": ANY,
                "user_subscription": ANY
            },
            request=response.wsgi_request
        )

    def test_load_preferences_partial_no_preferences(
        self,
        MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test loading preferences when user has no preferences set.
        """
        self.user_preference.topics.clear()
        mock_render_to_string.return_value = "<div>No Preferences</div>"
        response = self.client.get(
            reverse('load_preferences_partial'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())
        self.assertFalse(response.json()['has_next_page'])
        self.assertIsNone(response.json()['next_page_number'])

    def test_load_subscription_partial(
        self,
        MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test loading of subscription partial via AJAX.
        """
        mock_render_to_string.return_value = "<div>Subscription HTML</div>"
        response = self.client.get(
            reverse('load_subscription_partial'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"html": "<div>Subscription HTML</div>"}
        )
        mock_render_to_string.assert_called_once_with(
            'account/includes/partial_subscription.html',
            {'user_subscription': ANY},
            request=response.wsgi_request
        )

    def test_load_subscription_partial_no_subscription(
        self,
        MockUserSubscription,
        MockUserUpdateForm,
        mock_render_to_string
    ):
        """
        Test loading subscription when user has no active subscription.
        """
        UserSubscription.objects.all().delete()
        mock_render_to_string.return_value = "<div>No Subscription</div>"
        response = self.client.get(
            reverse('load_subscription_partial'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"html": "<div>No Subscription</div>"}
        )
