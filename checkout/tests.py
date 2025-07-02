from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from unittest.mock import patch, MagicMock

from accounts.models import CustomUser
from subscriptions.models import (
    SubscriptionPlan,
    SubscriptionFrequency,
    UserSubscription
)


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


@patch('checkout.views.stripe', mock_stripe_module)
class CheckoutRedirectionTest(TestCase):
    """
    Automated tests focusing purely on view redirections and HTTP status codes
    for the checkout application.
    """

    def setUp(self):
        """
        Set up test client and basic data for all tests.
        """
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client.login(username='testuser', password='password123')

        self.basic_plan = SubscriptionPlan.objects.create(
            name='basic', topic_limit=2, price=10.00
        )
        self.monthly_freq = SubscriptionFrequency.objects.create(
            name='monthly', duration_days=30, discount_percent=0
        )

        self.mock_calculate_price_patch = patch(
            'checkout.views.calculate_subscription_price',
            return_value=10.00
        )
        self.mock_calculate_price = self.mock_calculate_price_patch.start()
        self.addCleanup(self.mock_calculate_price_patch.stop)

        mock_stripe_module.reset_mock()

    def test_checkout_subscription_get_valid_url(self):
        """
        Test GET request to checkout_subscription with valid IDs.
        Should return 200 OK.
        """
        response = self.client.get(
            reverse('checkout', args=[self.basic_plan.id,
                                     self.monthly_freq.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_checkout_subscription_get_invalid_plan_redirects(self):
        """
        Test GET request with an invalid plan ID.
        Should redirect to choose_plan.
        """
        response = self.client.get(
            reverse('checkout', args=[999, self.monthly_freq.id])
        )
        self.assertRedirects(response, reverse('choose_plan'))

    def test_checkout_subscription_get_invalid_frequency_redirects(self):
        """
        Test GET request with an invalid frequency ID.
        Should redirect to choose_plan.
        """
        response = self.client.get(
            reverse('checkout', args=[self.basic_plan.id, 999])
        )
        self.assertRedirects(response, reverse('choose_plan'))

    def test_checkout_subscription_price_calc_fail_redirects(self):
        """
        Test GET request when calculate_subscription_price returns None.
        Should redirect to choose_plan.
        """
        self.mock_calculate_price.return_value = None
        response = self.client.get(
            reverse('checkout', args=[self.basic_plan.id,
                                     self.monthly_freq.id])
        )
        self.assertRedirects(response, reverse('choose_plan'))

    def test_checkout_subscription_post_redirects(self):
        """
        Test POST request to checkout_subscription.
        Should redirect to choose_plan.
        """
        response = self.client.post(
            reverse('checkout', args=[self.basic_plan.id,
                                     self.monthly_freq.id])
        )
        self.assertRedirects(response, reverse('choose_plan'))

    def test_cache_checkout_data_post_success(self):
        """
        Test POST request to cache_checkout_data with valid data.
        Should return 200 OK.
        """
        response = self.client.post(
            reverse('cache_checkout_data'),
            {
                'client_secret': 'pi_mock_secret_123_secret',
                'plan_id': self.basic_plan.id,
                'frequency_id': self.monthly_freq.id,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

    def test_cache_checkout_data_post_empty_client_secret_returns_400(self):
        """
        Test POST request to cache_checkout_data with an empty client_secret.
        Should return 400 Bad Request.
        """
        response = self.client.post(
            reverse('cache_checkout_data'),
            {
                'client_secret': '',
                'plan_id': self.basic_plan.id,
                'frequency_id': self.monthly_freq.id,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)

    def test_checkout_success_view_unauthenticated_redirects_to_login(self):
        """
        Test that checkout_success view redirects unauthenticated users
        to login.
        """
        self.client.logout()
        response = self.client.get(
            reverse('checkout_success', args=['pi_any_id'])
        )
        self.assertRedirects(
            response,
            f'{reverse("account_login")}?next=/checkout/success/pi_any_id/'
        )

    def test_checkout_success_invalid_pi_redirects_to_profile(self):
        """
        Test that checkout_success view redirects to profile for non-existent
        Payment Intent after retries.
        """
        with patch('checkout.views.UserSubscription.objects.get') as \
                mock_get_sub:
            mock_get_sub.side_effect = UserSubscription.DoesNotExist

            response = self.client.get(
                reverse('checkout_success', args=['pi_non_existent_123'])
            )
            self.assertRedirects(response, reverse('account_profile'))
