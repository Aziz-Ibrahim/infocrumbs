from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta, date
from unittest.mock import patch
from decimal import Decimal
from django.core import mail


from accounts.models import CustomUser
from .models import SubscriptionPlan, SubscriptionFrequency, UserSubscription
from .utils import calculate_subscription_price
from .email import send_subscription_confirmation_email
from .email import send_subscription_expiry_reminders


class SubscriptionModelsTest(TestCase):
    """
    Tests for the models in the subscriptions app.
    """

    def setUp(self):
        """
        Set up common data for model tests.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            date_of_birth=date(1990, 1, 1)
        )
        self.basic_plan = SubscriptionPlan.objects.create(
            name='basic', topic_limit=2, price=Decimal('10.00')
        )
        self.premium_plan = SubscriptionPlan.objects.create(
            name='premium', topic_limit=100, price=Decimal('20.00')
        )
        self.monthly_freq = SubscriptionFrequency.objects.create(
            name='monthly', duration_days=30, discount_percent=0
        )
        self.annual_freq = SubscriptionFrequency.objects.create(
            name='annual', duration_days=365, discount_percent=10
        )

    def test_subscription_plan_creation(self):
        """
        Test SubscriptionPlan creation and __str__ method.
        """
        self.assertEqual(self.basic_plan.name, 'basic')
        self.assertEqual(self.basic_plan.topic_limit, 2)
        self.assertEqual(self.basic_plan.price, Decimal('10.00'))
        self.assertEqual(str(self.basic_plan), 'Basic')

    def test_subscription_frequency_creation(self):
        """
        Test SubscriptionFrequency creation and __str__ method.
        """
        self.assertEqual(self.monthly_freq.name, 'monthly')
        self.assertEqual(self.monthly_freq.duration_days, 30)
        self.assertEqual(self.monthly_freq.discount_percent, 0)
        self.assertEqual(str(self.monthly_freq), 'monthly (0% off)')

    def test_user_subscription_creation(self):
        """
        Test UserSubscription creation and automatic date calculation.
        """
        with patch('django.utils.timezone.now') as mock_now:
            mock_dt = datetime(2025, 1, 1, 10, 0, 0)
            mock_now.return_value = timezone.make_aware(mock_dt)
            subscription = UserSubscription.objects.create(
                user=self.user,
                plan=self.basic_plan,
                frequency=self.monthly_freq,
                active=True
            )
            self.assertIsNotNone(subscription.start_date)
            self.assertIsNotNone(subscription.end_date)
            self.assertEqual(subscription.start_date, mock_now.return_value)
            self.assertEqual(
                subscription.end_date,
                mock_now.return_value + timedelta(days=30)
            )
            self.assertTrue(subscription.active)
            self.assertEqual(
                str(subscription),
                f"UserSubscription object ({subscription.pk})"
            )

    def test_user_subscription_extension(self):
        """
        Test that a new subscription extends the end_date of the latest
        existing one.
        """
        with patch('django.utils.timezone.now') as mock_now:
            mock_dt_start = datetime(2025, 1, 1, 10, 0, 0)
            mock_now.return_value = timezone.make_aware(mock_dt_start)
            UserSubscription.objects.create(
                user=self.user,
                plan=self.basic_plan,
                frequency=self.monthly_freq,
                active=True
            )

            mock_dt_middle = datetime(2025, 1, 15, 10, 0, 0)
            mock_now.return_value = timezone.make_aware(mock_dt_middle)
            new_subscription = UserSubscription.objects.create(
                user=self.user,
                plan=self.basic_plan,
                frequency=self.monthly_freq,
                active=True
            )
            expected_start_date = timezone.make_aware(mock_dt_start) + \
                timedelta(days=30)
            self.assertEqual(new_subscription.start_date, expected_start_date)
            self.assertEqual(
                new_subscription.end_date, new_subscription.start_date +
                timedelta(days=30)
            )

    def test_user_subscription_is_active(self):
        """
        Test the is_active method of UserSubscription.
        """
        subscription_active = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            frequency=self.monthly_freq,
            start_date=timezone.now() - timedelta(days=15),
            end_date=timezone.now() + timedelta(days=15),
            active=True
        )
        self.assertTrue(subscription_active.is_active())

        subscription_inactive = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            frequency=self.monthly_freq,
            start_date=timezone.now() - timedelta(days=60),
            end_date=timezone.now() - timedelta(days=30),
            active=True
        )
        self.assertFalse(subscription_inactive.is_active())

        subscription_not_active_flag = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            frequency=self.monthly_freq,
            start_date=timezone.now() - timedelta(days=15),
            end_date=timezone.now() + timedelta(days=15),
            active=False
        )
        self.assertFalse(subscription_not_active_flag.is_active())


class SubscriptionUtilsTest(TestCase):
    """
    Tests for utility functions in subscriptions app.
    """

    def setUp(self):
        """
        Set up common data for utility tests.
        """
        SubscriptionPlan.objects.create(
            name='basic', topic_limit=2, price=Decimal('10.00')
        )
        SubscriptionPlan.objects.create(
            name='premium', topic_limit=100, price=Decimal('20.00')
        )
        SubscriptionFrequency.objects.create(
            name='monthly', duration_days=30, discount_percent=0
        )
        SubscriptionFrequency.objects.create(
            name='annual', duration_days=365, discount_percent=10
        )
        SubscriptionFrequency.objects.create(
            name='quarterly', duration_days=90, discount_percent=5
        )

    def test_calculate_subscription_price_basic_monthly(self):
        """
        Test price calculation for basic monthly plan.
        """
        price = calculate_subscription_price('basic', 30)
        self.assertEqual(price, Decimal('10.00'))

    def test_calculate_subscription_price_premium_annual(self):
        """
        Test price calculation for premium annual plan with discount.
        """
        price = calculate_subscription_price('premium', 365)
        self.assertEqual(price, Decimal('219.00'))

    def test_calculate_subscription_price_non_existent_plan(self):
        """
        Test price calculation for a non-existent plan.
        """
        price = calculate_subscription_price('nonexistent', 30)
        self.assertIsNone(price)

    def test_calculate_subscription_price_non_existent_frequency(self):
        """
        Test price calculation for a non-existent frequency.
        """
        price = calculate_subscription_price('basic', 999)
        self.assertEqual(price, Decimal('333.00'))

    def test_calculate_subscription_price_quarterly_basic(self):
        """
        Test price calculation for basic quarterly plan with discount.
        """
        price = calculate_subscription_price('basic', 90)
        self.assertEqual(price, Decimal('28.50'))


class SubscriptionEmailTest(TestCase):
    """
    Tests for email functions in subscriptions app.
    """

    def setUp(self):
        """
        Set up common data for email tests.
        """
        self.user = CustomUser.objects.create_user(
            username='emailtestuser',
            email='email@example.com',
            password='password123',
            date_of_birth=date(1990, 1, 1)
        )
        self.basic_plan = SubscriptionPlan.objects.create(
            name='basic', topic_limit=2, price=Decimal('10.00')
        )
        self.premium_plan = SubscriptionPlan.objects.create(
            name='premium', topic_limit=100, price=Decimal('20.00')
        )
        self.monthly_freq = SubscriptionFrequency.objects.create(
            name='monthly', duration_days=30, discount_percent=0
        )
        self.annual_freq = SubscriptionFrequency.objects.create(
            name='annual', duration_days=365, discount_percent=10
        )
        UserSubscription.objects.all().delete()
        self.subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            frequency=self.monthly_freq,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            active=True
        )
        self.patcher_site_url = patch(
            'django.conf.settings.SITE_URL', 'http://testserver'
        )
        self.patcher_from_email = patch(
            'django.conf.settings.DEFAULT_FROM_EMAIL', 'noreply@test.com'
        )
        self.mock_site_url = self.patcher_site_url.start()
        self.mock_from_email = self.patcher_from_email.start()

    def tearDown(self):
        """
        Clean up mocks and email outbox after each test.
        """
        self.patcher_site_url.stop()
        self.patcher_from_email.stop()
        mail.outbox = []

    def test_send_subscription_confirmation_email(self):
        """
        Test that subscription confirmation email is sent correctly.
        """
        mail.outbox = []
        final_price = Decimal('10.00')
        send_subscription_confirmation_email(
            self.user, self.subscription, final_price
        )

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(
            email.subject,
            'InfoCrumbs Subscription Confirmation!'
        )
        self.assertEqual(email.from_email, 'noreply@test.com')
        self.assertEqual(email.to, ['email@example.com'])
        self.assertIn(
            "Thank you for your recent subscription purchase with InfoCrumbs!",
            email.body
        )
        self.assertIn(
            "Your subscription is now active with the following details:",
            email.body
        )
        self.assertIn("Plan: basic", email.body)
        self.assertIn("Frequency: monthly", email.body)
        self.assertIn(
            "You can manage your subscription and view your details anytime "
            "in your InfoCrumbs profile:",
            email.body
        )
        self.assertIn("http://testserver/accounts/profile/", email.body)
        self.assertTrue(email.alternatives[0][1], 'text/html')

    def test_send_subscription_expiry_reminders_sends_email(self):
        """
        Test that expiry reminder email is sent for an expiring subscription.
        """
        mail.outbox = []

        mock_dt = datetime(2025, 1, 1, 10, 0, 0)
        mock_now_aware = timezone.make_aware(mock_dt)

        UserSubscription.objects.filter(user=self.user).delete()
        expiring_sub = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            frequency=self.monthly_freq,
            start_date=mock_now_aware - timedelta(days=5),
            end_date=mock_now_aware + timedelta(
                hours=24
            ) + timedelta(minutes=1),
            active=True
        )

        with patch('django.utils.timezone.now', return_value=mock_now_aware):
            send_subscription_expiry_reminders()

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(
            email.subject,
            'Your InfoCrumbs Subscription Expires Soon!'
        )
        self.assertEqual(email.to, ['email@example.com'])
        self.assertIn(
            "Just a friendly reminder that your InfoCrumbs subscription "
            "(basic plan) is scheduled to expire in approximately 24 hours",
            email.body
        )
        self.assertIn(
            "Don't miss out on your personalized insights! Renew your "
            "subscription today to continue enjoying uninterrupted access:",
            email.body
        )
        self.assertIn("http://testserver/accounts/profile/", email.body)
        self.assertIn("http://testserver/subscriptions/choose/", email.body)
        self.assertTrue(email.alternatives[0][1], 'text/html')

    def test_reminders_skip_newer_active_subscription(self):
        """
        Test that expiry reminder is skipped if a newer active subscription
        exists.
        """
        mail.outbox = []

        mock_dt = datetime(2025, 1, 1, 10, 0, 0)
        mock_now_aware = timezone.make_aware(mock_dt)

        UserSubscription.objects.filter(user=self.user).delete()
        old_expiring_sub = UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            frequency=self.monthly_freq,
            start_date=mock_now_aware - timedelta(days=5),
            end_date=mock_now_aware + timedelta(
                hours=24
            ) + timedelta(minutes=1),
            active=True
        )

        newer_sub = UserSubscription.objects.create(
            user=self.user,
            plan=self.premium_plan,
            frequency=self.annual_freq,
            start_date=mock_now_aware + timedelta(days=1),
            end_date=mock_now_aware + timedelta(days=366),
            active=True
        )

        with patch('django.utils.timezone.now', return_value=mock_now_aware):
            send_subscription_expiry_reminders()

        self.assertEqual(len(mail.outbox), 0)

    def test_reminders_skip_outside_24hr_window(self):
        """
        Test that expiry reminder is skipped if not in the 24-hour window.
        """
        mail.outbox = []

        mock_dt = datetime(2025, 1, 1, 10, 0, 0)
        mock_now_aware = timezone.make_aware(mock_dt)

        UserSubscription.objects.filter(user=self.user).delete()
        UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            frequency=self.monthly_freq,
            start_date=mock_now_aware - timedelta(days=5),
            end_date=mock_now_aware + timedelta(hours=26),
            active=True
        )

        with patch('django.utils.timezone.now', return_value=mock_now_aware):
            send_subscription_expiry_reminders()

        self.assertEqual(len(mail.outbox), 0)

    def test_send_subscription_expiry_reminders_skips_inactive_sub(self):
        """
        Test that expiry reminder is skipped for inactive subscriptions.
        """
        mail.outbox = []

        mock_dt = datetime(2025, 1, 1, 10, 0, 0)
        mock_now_aware = timezone.make_aware(mock_dt)

        UserSubscription.objects.filter(user=self.user).delete()
        UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            frequency=self.monthly_freq,
            start_date=mock_now_aware - timedelta(days=5),
            end_date=mock_now_aware + timedelta(
                hours=24
            ) + timedelta(minutes=1),
            active=False
        )

        with patch('django.utils.timezone.now', return_value=mock_now_aware):
            send_subscription_expiry_reminders()

        self.assertEqual(len(mail.outbox), 0)


class SubscriptionViewsTest(TestCase):
    """
    Tests for the views in the subscriptions app.
    """

    def setUp(self):
        """
        Set up common data for view tests.
        """
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='viewtestuser',
            email='view@example.com',
            password='password123',
            date_of_birth=date(1995, 7, 1)
        )
        self.client.login(username='viewtestuser', password='password123')

        self.basic_plan = SubscriptionPlan.objects.create(
            name='basic', topic_limit=2, price=Decimal('10.00')
        )
        self.premium_plan = SubscriptionPlan.objects.create(
            name='premium', topic_limit=100, price=Decimal('20.00')
        )
        self.monthly_freq = SubscriptionFrequency.objects.create(
            name='monthly', duration_days=30, discount_percent=0
        )
        self.annual_freq = SubscriptionFrequency.objects.create(
            name='annual', duration_days=365, discount_percent=10
        )
        self.quarterly_freq = SubscriptionFrequency.objects.create(
            name='quarterly', duration_days=90, discount_percent=5
        )

        self.patcher_stripe_key = patch(
            'django.conf.settings.STRIPE_PUBLIC_KEY', 'pk_test_mock_key'
        )
        self.mock_stripe_key = self.patcher_stripe_key.start()

    def tearDown(self):
        """
        Clean up mocks after each test.
        """
        self.patcher_stripe_key.stop()

    def test_choose_plan_requires_login(self):
        """
        Test that choose_plan redirects unauthenticated users.
        """
        self.client.logout()
        response = self.client.get(reverse('choose_plan'))
        self.assertRedirects(
            response,
            f'{reverse("account_login")}?next={reverse("choose_plan")}'
        )

    def test_choose_plan_get_renders_template_with_plans(self):
        """
        Test that choose_plan renders the correct template and passes
        plan data.
        """
        response = self.client.get(reverse('choose_plan'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'subscriptions/choose_plan.html')
        self.assertIn('plans', response.context)
        self.assertEqual(len(response.context['plans']), 2)

        basic_plan_context = next(
            p for p in response.context['plans'] if p['name'] == 'Basic'
        )
        self.assertIsNotNone(basic_plan_context)
        self.assertEqual(basic_plan_context['topic_limit'], 2)
        self.assertEqual(len(basic_plan_context['frequencies']), 3)

        monthly_option = next(
            f for f in basic_plan_context[
                'frequencies'
            ] if f['name'] == 'monthly'
        )
        self.assertEqual(monthly_option['price'], Decimal('10.00'))

        annual_option = next(
            f for f in basic_plan_context[
                'frequencies'
            ] if f['name'] == 'annual'
        )
        self.assertEqual(annual_option['price'], Decimal('109.50'))

        quarterly_option = next(
            f for f in basic_plan_context[
                'frequencies'
            ] if f['name'] == 'quarterly'
        )
        self.assertEqual(quarterly_option['price'], Decimal('28.50'))

    def test_subscribe_requires_login(self):
        """
        Test that subscribe redirects unauthenticated users.
        """
        self.client.logout()
        response = self.client.get(
            reverse('subscribe', args=[self.basic_plan.id]) +
            '?frequency=' + str(self.monthly_freq.id)
        )
        self.assertRedirects(
            response,
            f'{reverse(
                "account_login"
            )}?next={reverse(
                "subscribe",
                args=[self.basic_plan.id]
            )}'
            f'?frequency={self.monthly_freq.id}'
        )

    def test_subscribe_get_renders_checkout_template_valid_data(self):
        """
        Test that subscribe renders checkout template with correct context for
        valid data.
        """
        response = self.client.get(
            reverse('subscribe', args=[self.basic_plan.id]) +
            '?frequency=' + str(self.monthly_freq.id)
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/checkout.html')
        self.assertIn('plan', response.context)
        self.assertEqual(response.context['plan'], self.basic_plan)
        self.assertIn('frequency', response.context)
        self.assertEqual(response.context['frequency'], self.monthly_freq)
        self.assertIn('price', response.context)
        self.assertEqual(response.context['price'], Decimal('10.00'))
        self.assertIn('STRIPE_PUBLIC_KEY', response.context)
        self.assertEqual(
            response.context['STRIPE_PUBLIC_KEY'],
            'pk_test_mock_key'
        )

    def test_subscribe_get_redirects_if_no_frequency_param(self):
        """
        Test that subscribe redirects to choose_plan if no frequency parameter.
        """
        response = self.client.get(
            reverse(
                'subscribe',
                args=[self.basic_plan.id]
            )
        )
        self.assertRedirects(response, reverse('choose_plan'))

    def test_subscribe_get_redirects_if_invalid_plan_id(self):
        """
        Test that subscribe returns 404 for invalid plan ID.
        """
        response = self.client.get(
            reverse('subscribe', args=[999]) +
            '?frequency=' + str(self.monthly_freq.id)
        )
        self.assertEqual(response.status_code, 404)

    def test_subscribe_get_redirects_if_invalid_frequency_id(self):
        """
        Test that subscribe returns 404 for invalid frequency ID.
        """
        response = self.client.get(
            reverse('subscribe', args=[self.basic_plan.id]) + '?frequency=999'
        )
        self.assertEqual(response.status_code, 404)

    def test_subscribe_get_redirects_if_price_calculation_fails(self):
        """
        Test that subscribe redirects if price calculation returns None.
        """
        with patch(
            'subscriptions.views.calculate_subscription_price',
            return_value=None
        ):
            response = self.client.get(
                reverse('subscribe', args=[self.basic_plan.id]) +
                '?frequency=' + str(self.monthly_freq.id)
            )
            self.assertRedirects(response, reverse('choose_plan'))

    def test_subscription_status_requires_login(self):
        """
        Test that subscription_status redirects unauthenticated users.
        """
        self.client.logout()
        response = self.client.get(reverse('subscription_status'))
        self.assertRedirects(
            response,
            f'{reverse("account_login")}?next={reverse("subscription_status")}'
        )

    def test_subscription_status_get_renders_template_no_subscription(self):
        """
        Test that subscription_status renders correctly when user has no
        subscription.
        """
        UserSubscription.objects.filter(user=self.user).delete()
        response = self.client.get(reverse('subscription_status'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'subscriptions/subscription_status.html'
        )
        self.assertIn('subscription', response.context)
        self.assertIsNone(response.context['subscription'])
        self.assertContains(
            response,
            "You are not subscribed to any plan yet."
        )

    def test_subscription_status_get_renders_template_with_subscription(self):
        """
        Test that subscription_status renders correctly when user has an
        active subscription.
        """
        UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            frequency=self.monthly_freq,
            start_date=timezone.now() - timedelta(days=5),
            end_date=timezone.now() + timedelta(days=25),
            active=True
        )
        response = self.client.get(reverse('subscription_status'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'subscriptions/subscription_status.html'
        )
        self.assertIn('subscription', response.context)
        self.assertIsNotNone(response.context['subscription'])
        self.assertEqual(response.context['subscription'].user, self.user)
        self.assertContains(
            response,
            f'<strong class="text-neon-green">Plan:</strong> Basic'
        )
