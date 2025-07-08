from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from unittest.mock import patch


class CoreViewsTest(TestCase):
    """
    Test the basic views and URL redirections in the core app.
    """

    def setUp(self):
        """
        Set up the test client for making requests.
        """
        self.client = Client()

    def test_home_view_status_code(self):
        """
        Test that the home page view returns a 200 OK status code.
        """
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_template_used(self):
        """
        Test that the home page view uses the correct template.
        """
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'core/home.html')

    def test_home_view_content(self):
        """
        Test that the home page contains some expected content.
        """
        response = self.client.get(reverse('home'))
        self.assertContains(
            response,
            '<h1 class="display-5 mb-3"><strong class="infocrumbs-title">'
            'infocrombs</strong><br>Bite-sized Knowledge. Big Impact.</h1>'
        )
        self.assertContains(
            response,
            'InfoCrumbs delivers smart, summarised, and auto-tagged content '
            'from trusted sources'
        )
        self.assertContains(response, 'Start with Basic')
        self.assertContains(response, 'Go Premium')
        self.assertContains(response, 'Join InfoCrumbs')
        self.assertNotContains(
            response, 'This text should not be on the home page'
        )

    @patch('django.conf.settings.DEBUG', True)
    def test_error_404_view_debug_true(self):
        """
        Test that the custom 404 handler is used when DEBUG is True.
        When DEBUG is True, Django usually shows a detailed traceback
        page for 404s, not the custom 404.html template. So, we only
        assert the status code.
        """
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)

    @patch('django.conf.settings.DEBUG', False)
    def test_error_404_view_debug_false(self):
        """
        Test that the custom 404 handler is used when DEBUG is False.
        Now that a custom handler is defined, we can assert the template
        and its specific content.
        """
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
        self.assertContains(response, "404", status_code=404)
        self.assertContains(response, "Page Not Found", status_code=404)
        self.assertContains(
            response,
            "Oops! It looks like the crumb you were looking for has vanished.",
            status_code=404
        )
        self.assertContains(
            response,
            "The page you are looking for might have been removed, "
            "had its name changed, or is temporarily unavailable.",
            status_code=404
        )
        self.assertContains(response, "Go to Home Page", status_code=404)


    def test_about_view_status_code(self):
        """
        Test that the about page view returns a 200 OK status code.
        """
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_about_view_template_used(self):
        """
        Test that the about page view uses the correct template.
        """
        response = self.client.get(reverse('about'))
        self.assertTemplateUsed(response, 'core/about.html')

    def test_about_view_content(self):
        """
        Test that the about page contains some expected content.
        """
        response = self.client.get(reverse('about'))
        self.assertContains(response, 'About InfoCrumbs')
        self.assertContains(
            response,
            '<strong>InfoCrumbs</strong> is a knowledge aggregation platform'
        )
        self.assertNotContains(
            response, 'This text should not be on the about page'
        )

    def test_faq_view_status_code(self):
        """
        Test that the FAQ page loads successfully.
        """
        response = self.client.get(reverse('faq'))
        self.assertEqual(response.status_code, 200)

    def test_faq_view_template_used(self):
        """
        Test that the FAQ page uses the correct template.
        """
        response = self.client.get(reverse('faq'))
        self.assertTemplateUsed(response, 'core/faq.html')

    def test_faq_view_content(self):
        """
        Test that the FAQ page contains some expected content.
        """
        response = self.client.get(reverse('faq'))
        self.assertContains(response, "Frequently Asked Questions")
        self.assertContains(response, "What is InfoCrumbs?")
        self.assertContains(
            response, "InfoCrumbs is a platform designed to deliver"
        )

    def test_contact_view_status_code(self):
        """
        Test that the contact page loads successfully.
        """
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

    def test_contact_view_template_used(self):
        """
        Test that the contact page uses the correct template.
        """
        response = self.client.get(reverse('contact'))
        self.assertTemplateUsed(response, 'core/contact.html')

    def test_contact_view_content(self):
        """
        Test that the contact page contains some expected content.
        """
        response = self.client.get(reverse('contact'))
        self.assertContains(response, "Contact Our Support Team")
        self.assertContains(
            response,
            "Have questions or feedback? We'd love to hear from you!"
        )

    def test_signup_redirect(self):
        """
        Test that the /signup/ URL redirects to the allauth signup page.
        """
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account_signup'))

    def test_login_redirect(self):
        """
        Test that the /login/ URL redirects to the allauth login page.
        """
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account_login'))

    def test_logout_redirect(self):
        """
        Test that the /logout/ URL redirects through allauth logout
        to the expected final page (e.g., home page).
        """
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('account_logout'),
            status_code=302,
            target_status_code=302
        )

        response = self.client.get(reverse('logout'))

        self.assertEqual(response.status_code, 302)

        redirect_to_allauth_logout_url = response.url

        self.assertEqual(
            redirect_to_allauth_logout_url,
            reverse('account_logout')
        )

        response_from_allauth_logout = self.client.get(
            redirect_to_allauth_logout_url
        )

        self.assertEqual(response_from_allauth_logout.status_code, 302)

        final_redirect_url = response_from_allauth_logout.url

        self.assertEqual(final_redirect_url, reverse('home'))

        final_page_response = self.client.get(final_redirect_url)
        self.assertEqual(final_page_response.status_code, 200)
