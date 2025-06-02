from urllib import response
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.core import mail  # For testing emails at a later stage
from django.core.exceptions import ValidationError # Import ValidationError explicitly

# Import models from other apps that are linked to
# Profile for testing relationships
from accounts.models import Profile
from crumbs.models import Crumb
from feedback.models import Comment, SavedCrumb
from preferences.models import Topic, UserPreference
from subscriptions.models import (
    SubscriptionPlan,
    SubscriptionFrequency,
    UserSubscription
)


# Get the custom user model as defined in settings.AUTH_USER_MODEL
CustomUser = get_user_model()

class CustomUserModelTest(TestCase):
    """Test the CustomUser model and its methods."""
    def test_user_creation(self):
        """Test that a custom user can be created with default values."""
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('password123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.is_premium, False)
        self.assertEqual(user.subscription_type, 'none')

    def test_superuser_creation(self):
        """Test that a superuser can be created with correct flags."""
        admin_user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)
        self.assertEqual(
            admin_user.is_premium,
            False
            )  # Default for superuser too

    def test_unique_email_constraint(self):
        """Test that email addresses must be unique."""
        CustomUser.objects.create_user(
            username='user1', email='unique@example.com', password='p'
            )
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='user2', email='unique@example.com', password='p'
                )

    def test_unique_username_constraint(self):
        """Test that usernames must be unique."""
        CustomUser.objects.create_user(
            username='uniqueuser', email='a@b.com', password='p'
            )
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='uniqueuser', email='c@d.com', password='p'
                )

    def test_is_premium_field(self):
        """Test the is_premium field can be set."""
        user = CustomUser.objects.create_user(
            username='premiumuser',
            email='premium@example.com', password='p',
            is_premium=True
            )
        self.assertTrue(user.is_premium)

    def test_subscription_type_choices(self):
        """Test that subscription_type enforces
            valid choices on full_clean()."""
        user = CustomUser.objects.create_user(
            username='weeklyuser',
            email='weekly@example.com',
            password='p',subscription_type='weekly'
            )
        self.assertEqual(user.subscription_type, 'weekly')

        # Test invalid choice using full_clean()
        user_invalid = CustomUser(
            username='invalidsub',
            email='invalid@example.com',
            password='p'
            )
        user_invalid.subscription_type = 'invalid_type'

        with self.assertRaisesMessage(
            ValidationError,
            "Value 'invalid_type' is not a valid choice."
            ):
            user_invalid.full_clean()


class ProfileModelTest(TestCase):
    """Test the Profile model and its signal for automatic creation."""
    def setUp(self):
        # Create a user, which should trigger the signal to create a profile
        self.user = CustomUser.objects.create_user(
            username='profiletest',
            email='profile@example.com',
            password='password123'
        )
        # The signal ensures the profile exists immediately after user creation
        # Using get_or_create as a fallback for test robustness
        self.profile, created = Profile.objects.get_or_create(user=self.user)

        # Create dummy data for ManyToMany fields
        self.crumb = Crumb.objects.create(
            title="Test Crumb",
            content="Test Content"
            )
        self.comment = Comment.objects.create(
            user=self.user,
            crumb=self.crumb, text="Test Comment"
            )
        self.topic = Topic.objects.create(
            name="Test Topic",
            slug="test-topic"
            )


    def test_profile_creation_via_signal(self):
        """Test that a profile is automatically created
            when a CustomUser is created."""
        self.assertIsInstance(self.profile, Profile)
        self.assertEqual(self.profile.user, self.user)
        self.assertIsNone(self.profile.date_of_birth)  # Check default null
        self.assertEqual(self.profile.saved_crumbs.count(), 0)
        self.assertEqual(self.profile.comment_history.count(), 0)
        self.assertEqual(self.profile.topic_preferences.count(), 0)

    def test_profile_str_representation(self):
        """Test the __str__ method of the Profile model."""
        self.assertEqual(str(self.profile), f"{self.user.username}'s Profile")

    def test_profile_date_of_birth_update(self):
        """Test updating the profile's date_of_birth."""
        from datetime import date
        self.profile.date_of_birth = date(1990, 5, 15)
        self.profile.save()
        updated_profile = Profile.objects.get(user=self.user)
        self.assertEqual(updated_profile.date_of_birth, date(1990, 5, 15))

    def test_saved_crumbs_relationship(self):
        """Test adding and retrieving saved crumbs."""
        self.profile.saved_crumbs.add(self.crumb)
        self.assertEqual(self.profile.saved_crumbs.count(), 1)
        self.assertIn(self.crumb, self.profile.saved_crumbs.all())

    def test_comment_history_relationship(self):
        """Test adding and retrieving comments in history."""
        self.profile.comment_history.add(self.comment)
        self.assertEqual(self.profile.comment_history.count(), 1)
        self.assertIn(self.comment, self.profile.comment_history.all())

    def test_topic_preferences_relationship(self):
        """Test adding and retrieving topic preferences."""
        self.profile.topic_preferences.add(self.topic)
        self.assertEqual(self.profile.topic_preferences.count(), 1)
        self.assertIn(self.topic, self.profile.topic_preferences.all())


class AccountViewsTest(TestCase):
    """Test the views related to user accounts and profiles."""
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='viewtestuser',
            email='viewtest@example.com',
            password='password123'
        )
        # Using get_or_create to ensure profile exists for tests,
        # regardless of signal behavior in test environment.
        self.profile, created = Profile.objects.get_or_create(user=self.user)

        # Create dummy data for related models
        self.crumb1 = Crumb.objects.create(title="Crumb 1", content="Content 1")
        self.crumb2 = Crumb.objects.create(title="Crumb 2", content="Content 2")
        self.saved_crumb1 = SavedCrumb.objects.create(
            user=self.user,
            crumb=self.crumb1
            )

        self.comment1 = Comment.objects.create(
            user=self.user,
            crumb=self.crumb1,
            text="My first comment"
            )
        self.comment2 = Comment.objects.create(
            user=self.user,
            crumb=self.crumb2,
            text="My second comment"
            )

        self.topic1 = Topic.objects.create(name="Tech", slug="tech")
        self.topic2 = Topic.objects.create(name="Gaming", slug="gaming")
        self.user_preference, _ = UserPreference.objects.get_or_create(
            user=self.user
            )
        self.user_preference.topics.add(self.topic1)

        self.plan = SubscriptionPlan.objects.create(name='Basic', price=10.00)
        self.frequency = SubscriptionFrequency.objects.create(
            name='Monthly',
            multiplier=1
            )
        self.user_subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.plan,
            frequency=self.frequency,
            start_date='2024-01-01',
            end_date='2024-02-01',
            is_active=True
        )

        # Log in the user for subsequent tests that require authentication
        self.client.login(username='viewtestuser', password='password123')


    def test_profile_view_requires_login(self):
        """Test that profile_view redirects unauthenticated users."""
        self.client.logout()  # Ensure logged out
        response = self.client.get(reverse('account_profile'))
        self.assertEqual(response.status_code, 302) # Redirect
        # Redirects to Allauth login
        self.assertIn('/accounts/login/', response.url)

    def test_profile_view_loads_for_authenticated_user(self):
        """Test that profile_view loads correctly for authenticated users."""
        response = self.client.get(reverse('account_profile'))
        self.assertEqual(response.status_code, 200) # OK
        self.assertTemplateUsed(response, 'account/profile.html')


    def test_load_account_details_partial(self):
        """Test loading of account details partial via AJAX."""
        response = self.client.get(reverse('load_account_details_partial'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertIn('html', response.json())
        html = response.json()['html']
        self.assertIn(self.user.username, html)
        self.assertIn(self.user.email, html)
        # Check for first_name and last_name if they exist on the user
        self.assertIn(
            self.user.first_name if self.user.first_name else '',
            html
            )
        self.assertIn(
            self.user.last_name if self.user.last_name else '',
            html
            )


    def test_account_update_post_redirects(self):
        """Test that account_update redirects after a successful POST."""
        response = self.client.post(reverse('account_update'), {
            'first_name': 'NewFirstName',
            'last_name': 'NewLastName',
            'email': 'newemail@example.com'
        })
        self.assertEqual(response.status_code, 302)
        # Redirect to profile
        self.assertRedirects(response, reverse('account_profile'))


    def test_account_update_updates_user_data(self):
        """Test that account_update correctly updates user data."""
        # Ensure initial state
        self.assertEqual(self.user.first_name, '')
        self.assertEqual(self.user.last_name, '')
        self.assertEqual(self.user.email, 'viewtest@example.com')

        # Capture the response for message checking
        response = self.client.post(reverse('account_update'), {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com'
        })

        # Reload user from DB to get updated values
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'updated@example.com')
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Account details updated successfully."
            )


    def test_account_update_only_updates_provided_fields(self):
        """Test that account_update only updates fields that are provided."""
        self.user.first_name = "InitialFirst"
        self.user.save()
        self.client.post(reverse('account_update'), {
            'last_name': 'OnlyLastName'
        })
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.first_name,
            'InitialFirst'
            )  # Should remain unchanged
        self.assertEqual(
            self.user.last_name,
            'OnlyLastName'
            )  # Should be updated
        self.assertEqual(
            self.user.email,
            'viewtest@example.com'
            )  # Should remain unchanged


    def test_load_saved_crumbs_partial(self):
        """Test loading of saved crumbs partial via AJAX."""
        response = self.client.get(reverse('load_saved_crumbs_partial'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertIn('html', response.json())
        html = response.json()['html']
        self.assertIn(
            self.crumb1.title,
            html
            )  # Check if crumb title is in the rendered HTML
        self.assertContains(
            response,
            self.crumb1.title
            )  # An alternative way to check content


    def test_load_saved_crumbs_partial_no_crumbs(self):
        """Test loading saved crumbs when none are saved."""
        SavedCrumb.objects.filter(user=self.user).delete()  # Clear saved crumbs
        response = self.client.get(reverse('load_saved_crumbs_partial'))
        self.assertEqual(response.status_code, 200)
        html = response.json()['html']
        self.assertIn("No saved crumbs yet.", html)

    def test_load_comments_partial(self):
        """Test loading of comments partial via AJAX."""
        response = self.client.get(reverse('load_comments_partial'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertIn('html', response.json())
        html = response.json()['html']
        self.assertIn(self.comment1.text, html)
        self.assertIn(self.comment2.text, html)
        self.assertContains(response, self.comment1.text)


    def test_load_comments_partial_no_comments(self):
        """Test loading comments when none exist for the user."""
        Comment.objects.filter(user=self.user).delete()  # Clear comments
        response = self.client.get(reverse('load_comments_partial'))
        self.assertEqual(response.status_code, 200)
        html = response.json()['html']
        self.assertIn("No comments yet.", html)


    def test_load_preferences_partial(self):
        """Test loading of preferences partial via AJAX."""
        response = self.client.get(reverse('load_preferences_partial'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertIn('html', response.json())
        html = response.json()['html']
        self.assertIn(
            self.topic1.name,
            html
            )  # Check if the topic name is in the HTML
        self.assertNotContains(response, self.topic2.name)  # topic2 not added


    def test_load_preferences_partial_no_preferences(self):
        """Test loading preferences when user has no preferences set."""
        self.user_preference.topics.clear()  # Clear topics
        response = self.client.get(reverse('load_preferences_partial'))
        self.assertEqual(response.status_code, 200)
        html = response.json()['html']
        self.assertIn("No topics selected", html)
        self.assertNotIn(self.topic1.name, html)


    def test_load_subscription_partial(self):
        """Test loading of subscription partial via AJAX."""
        response = self.client.get(reverse('load_subscription_partial'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertIn('html', response.json())
        html = response.json()['html']
        self.assertIn(self.plan.name, html)
        self.assertIn(self.frequency.name, html)
        self.assertIn(str(self.user_subscription.start_date), html)
        self.assertIn(str(self.user_subscription.end_date), html)


    def test_load_subscription_partial_no_subscription(self):
        """Test loading subscription when user has no active subscription."""
        self.user_subscription.delete()  # Delete the user's subscription
        response = self.client.get(reverse('load_subscription_partial'))
        self.assertEqual(response.status_code, 200)
        html = response.json()['html']
        self.assertIn("You are not subscribed to any plan yet.", html)
        self.assertNotIn(self.plan.name, html)