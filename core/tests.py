from django.test import TestCase, Client
from django.urls import reverse


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
            'Welcome to <span class="highlight glow-text">InfoCrumbs</span>'
            )
        self.assertNotContains(
            response, 'This text should not be on the home page'
        )

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
        self.assertNotContains(
            response, 'This text should not be on the about page'
        )

    def test_signup_redirect(self):
        """
        Test that the /signup/ URL redirects to the allauth signup page.
        """
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 302)  # Expect a redirect
        self.assertRedirects(response, reverse('account_signup'))

    def test_login_redirect(self):
        """
        Test that the /login/ URL redirects to the allauth login page.
        """
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)  # Expect a redirect
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