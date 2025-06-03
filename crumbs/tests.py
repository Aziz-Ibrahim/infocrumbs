import datetime

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone


from accounts.models import CustomUser, Profile
from preferences.models import Topic, UserPreference
from subscriptions.models import SubscriptionPlan, UserSubscription
from feedback.models import SavedCrumb
from .models import Crumb


class CrumbModelTest(TestCase):
    """
    Tests for the Crumb model.
    """

    def setUp(self):
        """
        Set up common data for Crumb model tests.
        """
        self.unique_topic_name = 'TestTopicForCrumbModel'
        self.topic = Topic.objects.create(name=self.unique_topic_name)
    
    def test_crumb_creation(self):
        """
        Ensure a Crumb can be created and its fields are set correctly.
        """
        crumb = Crumb.objects.create(
            title='Test Crumb Title',
            summary='This is a summary for the test crumb.',
            url='http://example.com/test',
            source='Test Source',
            topic=self.topic,
            published_at=timezone.now() - datetime.timedelta(days=1)
        )
        self.assertEqual(crumb.title, 'Test Crumb Title')
        self.assertEqual(crumb.topic, self.topic)
        self.assertIsNotNone(crumb.added_on)
        self.assertLess(crumb.published_at, crumb.added_on)

    def test_crumb_str_representation(self):
        """
        Test the __str__ method of the Crumb model.
        """
        crumb = Crumb.objects.create(
            title='Science Breakthrough',
            summary='Summary.',
            url='http://example.com/science',
            source='Science Daily',
            topic=self.topic,
            published_at=timezone.now()
        )
        self.assertEqual(str(crumb), 'Science Breakthrough')


class CrumbListViewTest(TestCase):
    """
    Tests for the crumb_list view.
    """

    def setUp(self):
        """
        Set up common data for crumb_list view tests.
        """
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com',
            password='password123'
        )
        Profile.objects.get_or_create(user=self.user)

        self.topic1 = Topic.objects.create(name='TechTopic')
        self.topic2 = Topic.objects.create(name='FinanceTopic')
        self.topic3 = Topic.objects.create(name='HealthTopic')

        self.crumb1_tech = Crumb.objects.create(
            title='Tech Crumb 1', summary='S1', url='http://t1.com',
            source='Tech Source', topic=self.topic1, published_at=timezone.now()
        )
        self.crumb2_finance = Crumb.objects.create(
            title='Finance Crumb 1', summary='S2', url='http://f1.com',
            source='Finance Source', topic=self.topic2,
            published_at=timezone.now() - datetime.timedelta(hours=1)
        )
        self.crumb3_tech = Crumb.objects.create(
            title='Tech Crumb 2', summary='S3', url='http://t2.com',
            source='Tech Source', topic=self.topic1,
            published_at=timezone.now() - datetime.timedelta(hours=2)
        )
        self.crumb4_health = Crumb.objects.create(
            title='Health Crumb 1', summary='S4', url='http://h1.com',
            source='Health Source', topic=self.topic3,
            published_at=timezone.now() - datetime.timedelta(hours=3)
        )

        self.future_end_date = timezone.now() + datetime.timedelta(days=30)

        self.basic_plan = SubscriptionPlan.objects.create(
            name='Basic Plan Type',
            price=10.00,
            topic_limit=2
        )
        self.premium_plan = SubscriptionPlan.objects.create(
            name='Premium Plan Type',
            price=20.00,
            topic_limit=12
        )

    def test_crumb_list_redirects_unauthenticated_user(self):
        """
        Ensure unauthenticated users are redirected to the login page.
        """
        response = self.client.get(reverse('crumb_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account_login'))

    def test_crumb_list_redirects_user_without_subscription(self):
        """
        Ensure authenticated users without an active subscription are redirected
        to the choose_plan page.
        """
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('crumb_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('choose_plan'))

    def test_crumb_list_basic_subscription_no_preferences(self):
        """
        Ensure basic subscription user with no preferences sees no crumbs.
        """
        UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            active=True,
            end_date=self.future_end_date
        )

        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('crumb_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crumbs/crumbs_list.html')
        self.assertQuerySetEqual(response.context['page_obj'], [])

    def test_crumb_list_basic_subscription_with_preferences(self):
        """
        Ensure basic subscription user sees crumbs from preferred topics
        (limited to 2 topics).
        """
        UserSubscription.objects.create(
            user=self.user,
            plan=self.basic_plan,
            active=True,
            end_date=self.future_end_date
        )
        user_pref = UserPreference.objects.create(user=self.user)
        user_pref.topics.add(self.topic1, self.topic2)

        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('crumb_list'))
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.crumb1_tech, response.context['page_obj'])
        self.assertIn(self.crumb3_tech, response.context['page_obj'])
        self.assertIn(self.crumb2_finance, response.context['page_obj'])
        self.assertNotIn(self.crumb4_health, response.context['page_obj'])

    def test_crumb_list_premium_subscription_with_preferences(self):
        """
        Ensure premium subscription user sees crumbs from all preferred topics.
        """
        UserSubscription.objects.create(
            user=self.user,
            plan=self.premium_plan,
            active=True,
            end_date=self.future_end_date
        )
        user_pref = UserPreference.objects.create(user=self.user)
        user_pref.topics.add(self.topic1, self.topic2, self.topic3)

        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('crumb_list'))
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.crumb1_tech, response.context['page_obj'])
        self.assertIn(self.crumb3_tech, response.context['page_obj'])
        self.assertIn(self.crumb2_finance, response.context['page_obj'])
        self.assertIn(self.crumb4_health, response.context['page_obj'])

    def test_crumb_list_with_selected_topic_filter(self):
        """
        Ensure crumbs are filtered by the 'topic' GET parameter.
        """
        UserSubscription.objects.create(
            user=self.user,
            plan=self.premium_plan,
            active=True,
            end_date=self.future_end_date
        )
        user_pref = UserPreference.objects.create(user=self.user)
        user_pref.topics.add(self.topic1, self.topic2, self.topic3)

        self.client.login(username='testuser', password='password123')
        response = self.client.get(
            reverse('crumb_list') + f'?topic={self.topic1.id}'
        )
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.crumb1_tech, response.context['page_obj'])
        self.assertIn(self.crumb3_tech, response.context['page_obj'])
        self.assertNotIn(self.crumb2_finance, response.context['page_obj'])
        self.assertNotIn(self.crumb4_health, response.context['page_obj'])
        self.assertEqual(response.context['selected_topic'], self.topic1.id)

    def test_crumb_list_displays_saved_crumbs(self):
        """
        Ensure the list of saved_crumbs IDs is passed to the context.
        """
        UserSubscription.objects.create(
            user=self.user,
            plan=self.premium_plan,
            active=True,
            end_date=self.future_end_date
        )
        user_pref = UserPreference.objects.create(user=self.user)
        user_pref.topics.add(self.topic1)

        SavedCrumb.objects.create(user=self.user, crumb=self.crumb1_tech)

        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('crumb_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.crumb1_tech.id, response.context['saved_crumbs'])
        self.assertNotIn(self.crumb2_finance.id, response.context['saved_crumbs'])

    def test_crumb_list_pagination(self):
        """
        Ensure the view handles pagination correctly.
        """
        UserSubscription.objects.create(
            user=self.user,
            plan=self.premium_plan,
            active=True,
            end_date=self.future_end_date
        )
        user_pref = UserPreference.objects.create(user=self.user)
        user_pref.topics.clear()
        user_pref.topics.add(self.topic1)

        for i in range(10):
            Crumb.objects.create(
                title=f'Pagination Crumb {i}', summary='S',
                url=f'http://p{i}.com', source='P Source', topic=self.topic1,
                published_at=timezone.now() - datetime.timedelta(minutes=i)
            )

        self.client.login(username='testuser', password='password123')
        response_page1 = self.client.get(reverse('crumb_list'))
        self.assertEqual(len(response_page1.context['page_obj']), 10)
        self.assertTrue(response_page1.context['page_obj'].has_next())

        response_page2 = self.client.get(reverse('crumb_list') + '?page=2')
        self.assertEqual(len(response_page2.context['page_obj']), 2)
        self.assertFalse(response_page2.context['page_obj'].has_next())


class CrumbDetailViewTest(TestCase):
    """
    Tests for the crumb_detail view.
    """

    def setUp(self):
        """
        Set up common data for crumb_detail view tests.
        """
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com',
            password='password123'
        )
        Profile.objects.get_or_create(user=self.user)
        self.topic = Topic.objects.create(name='GeneralCrumbDetailTopic')
        self.crumb = Crumb.objects.create(
            title='Detail Crumb', summary='Detailed summary.',
            url='http://detail.com', source='Detail Source',
            topic=self.topic, published_at=timezone.now()
        )

    def test_crumb_detail_view_success(self):
        """
        Ensure crumb_detail view renders successfully for an existing crumb.
        """
        response = self.client.get(reverse('crumb_detail', args=[self.crumb.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crumbs/crumb_detail.html')
        self.assertEqual(response.context['crumb'], self.crumb)
        self.assertFalse(response.context['is_saved'])

    def test_crumb_detail_view_404_for_non_existent_crumb(self):
        """
        Ensure crumb_detail view returns 404 for a non-existent crumb.
        """
        non_existent_pk = self.crumb.pk + 999
        response = self.client.get(
            reverse('crumb_detail', args=[non_existent_pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_crumb_detail_view_authenticated_user_saved_crumb(self):
        """
        Ensure crumb_detail view correctly identifies a saved crumb for an
        authenticated user.
        """
        SavedCrumb.objects.create(user=self.user, crumb=self.crumb)
        self.client.login(username='testuser', password='password123')

        response = self.client.get(reverse('crumb_detail', args=[self.crumb.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_saved'])

    def test_crumb_detail_view_authenticated_user_unsaved_crumb(self):
        """
        Ensure crumb_detail view correctly identifies an unsaved crumb for an
        authenticated user.
        """
        self.client.login(username='testuser', password='password123')

        response = self.client.get(reverse('crumb_detail', args=[self.crumb.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_saved'])