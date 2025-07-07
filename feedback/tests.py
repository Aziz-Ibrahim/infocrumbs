from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date
from django.db.utils import IntegrityError

from accounts.models import CustomUser
from crumbs.models import Crumb, Topic
from .models import SavedCrumb, LikedCrumb, Comment
from .forms import CommentForm


class FeedbackModelsTest(TestCase):
    """
    Test cases for SavedCrumb, LikedCrumb, and Comment models.
    """
    def setUp(self):
        """
        Set up test data for SavedCrumb, LikedCrumb, and Comment models.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            date_of_birth=date(1990, 1, 1)
        )
        self.topic = Topic.objects.create(name='Technology')
        self.crumb = Crumb.objects.create(
            title='Test Crumb',
            summary='This is a summary for the test crumb.',
            published_at=timezone.now(),
            topic=self.topic,
            url='http://example.com/test-crumb-model-1'
        )

    def test_saved_crumb_creation(self):
        """
        Test that a SavedCrumb can be created and has the correct fields.
        """
        saved_crumb = SavedCrumb.objects.create(
            user=self.user,
            crumb=self.crumb
        )
        self.assertEqual(SavedCrumb.objects.count(), 1)
        self.assertEqual(saved_crumb.user, self.user)
        self.assertEqual(saved_crumb.crumb, self.crumb)
        self.assertIsNotNone(saved_crumb.saved_at)

    def test_saved_crumb_str_representation(self):
        """
        Test the string representation of a SavedCrumb instance.
        """
        saved_crumb = SavedCrumb.objects.create(
            user=self.user,
            crumb=self.crumb
        )
        self.assertEqual(
            str(saved_crumb),
            f"{self.user.username} saved {self.crumb.title}"
        )

    def test_saved_crumb_unique_constraint(self):
        """
        Test that a SavedCrumb cannot be created with the same user and crumb.
        """
        SavedCrumb.objects.create(user=self.user, crumb=self.crumb)
        with self.assertRaises(IntegrityError) as cm:
            SavedCrumb.objects.create(user=self.user, crumb=self.crumb)
        self.assertIn(
            'UNIQUE constraint failed: feedback_savedcrumb.user_id, '
            'feedback_savedcrumb.crumb_id',
            str(cm.exception)
        )

    def test_liked_crumb_creation(self):
        """
        Test that a LikedCrumb can be created and has the correct fields.
        """
        liked_crumb = LikedCrumb.objects.create(
            user=self.user,
            crumb=self.crumb
        )
        self.assertEqual(LikedCrumb.objects.count(), 1)
        self.assertEqual(liked_crumb.user, self.user)
        self.assertEqual(liked_crumb.crumb, self.crumb)
        self.assertIsNotNone(liked_crumb.liked_at)

    def test_liked_crumb_str_representation(self):
        """
        Test the string representation of a LikedCrumb instance.
        """
        liked_crumb = LikedCrumb.objects.create(
            user=self.user,
            crumb=self.crumb
        )
        self.assertEqual(
            str(liked_crumb),
            f"{self.user.username} liked {self.crumb.title}"
        )

    def test_liked_crumb_unique_constraint(self):
        """
        Test that a LikedCrumb cannot be created with the same user and crumb.
        """
        LikedCrumb.objects.create(user=self.user, crumb=self.crumb)
        with self.assertRaises(IntegrityError) as cm:
            LikedCrumb.objects.create(user=self.user, crumb=self.crumb)
        self.assertIn(
            'UNIQUE constraint failed: feedback_likedcrumb.user_id, '
            'feedback_likedcrumb.crumb_id',
            str(cm.exception)
        )

    def test_comment_creation(self):
        """
        Test that a Comment can be created and has the correct fields.
        """
        comment = Comment.objects.create(
            user=self.user,
            crumb=self.crumb,
            content='This is a test comment content.'
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.crumb, self.crumb)
        self.assertEqual(comment.content, 'This is a test comment content.')
        self.assertIsNotNone(comment.created_at)
        self.assertIsNotNone(comment.updated_at)

    def test_comment_str_representation(self):
        """
        Test the string representation of a Comment instance.
        """
        comment = Comment.objects.create(
            user=self.user,
            crumb=self.crumb,
            content='Another test comment.'
        )
        self.assertEqual(
            str(comment),
            f"Comment by {self.user.username} on {self.crumb.title}"
        )

    def test_comment_update(self):
        """
        Test that updating a Comment updates the content and updated_at fields.
        """
        comment = Comment.objects.create(
            user=self.user,
            crumb=self.crumb,
            content='Original comment.'
        )
        old_updated_at = comment.updated_at
        comment.content = 'Updated comment.'
        comment.save()
        self.assertEqual(comment.content, 'Updated comment.')
        self.assertGreater(comment.updated_at, old_updated_at)


class CommentFormTest(TestCase):
    """
    Test cases for CommentForm validation.
    """
    def test_comment_form_valid(self):
        """
        Test that a valid comment form passes validation.
        """
        form = CommentForm(
            data={'content': 'This is a valid comment of sufficient length.'}
        )
        self.assertTrue(form.is_valid())

    def test_comment_form_invalid_too_short(self):
        """
        Test that a comment form with content too short fails validation.
        """
        form = CommentForm(data={'content': 'Too'})
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        self.assertIn(
            'Ensure this value has at least 5 characters',
            form.errors['content'][0]
        )

    def test_comment_form_invalid_too_long(self):
        """
        Test that a comment form with content too long fails validation.
        """
        form = CommentForm(data={'content': 'a' * 501})
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        self.assertIn(
            'Ensure this value has at most 500 characters',
            form.errors['content'][0]
        )

    def test_comment_form_empty_content(self):
        """
        Test that a comment form with empty content fails validation.
        """
        form = CommentForm(data={'content': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        self.assertIn('This field is required', form.errors['content'][0])


class FeedbackViewsTest(TestCase):
    """
    Test cases for feedback-related views.
    """
    def setUp(self):
        """
        Set up test data for feedback views.
        """
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='viewtestuser',
            email='view@example.com',
            password='password123',
            date_of_birth=date(1995, 7, 1)
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123',
            date_of_birth=date(1996, 8, 2)
        )
        self.client.login(username='viewtestuser', password='password123')

        self.topic = Topic.objects.create(name='Science')
        self.crumb = Crumb.objects.create(
            title='View Test Crumb',
            summary='Summary for view test crumb.',
            published_at=timezone.now(),
            topic=self.topic,
            url='http://example.com/view-test-crumb-1'
        )
        self.comment = Comment.objects.create(
            user=self.user,
            crumb=self.crumb,
            content='This is an existing comment.'
        )

    def test_add_comment_requires_login(self):
        """
        Test that adding a comment requires the user to be logged in.
        """
        self.client.logout()
        response = self.client.post(
            reverse(
                'add_comment',
                args=[self.crumb.id]
            ),
            {'content': 'New comment'}
        )
        self.assertRedirects(
            response,
            f'{reverse("account_login")}?next={reverse(
                "add_comment", args=[self.crumb.id]
                )}'
        )

    def test_add_comment_post_valid_ajax(self):
        """
        Test adding a comment via AJAX with valid data.
        """
        initial_comment_count = Comment.objects.count()
        response = self.client.post(
            reverse('add_comment', args=[self.crumb.id]),
            {'content': 'This is a new comment via AJAX.'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), initial_comment_count + 1)
        self.assertContains(response, 'This is a new comment via AJAX.')
        self.assertTemplateUsed(
            response,
            'feedback/includes/comment_list.html'
        )

    def test_add_comment_post_valid_non_ajax_redirects(self):
        """
        Test adding a comment via non-AJAX request with valid data.
        """
        initial_comment_count = Comment.objects.count()
        response = self.client.post(
            reverse('add_comment', args=[self.crumb.id]),
            {'content': 'This is a new comment via non-AJAX.'}
        )
        self.assertEqual(Comment.objects.count(), initial_comment_count + 1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('crumb_detail', args=[self.crumb.id]),
            target_status_code=302
        )

    def test_add_comment_post_invalid_ajax(self):
        """
        Test adding a comment via AJAX with invalid data.
        """
        initial_comment_count = Comment.objects.count()
        response = self.client.post(
            reverse('add_comment', args=[self.crumb.id]),
            {'content': 'Bad'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Comment.objects.count(), initial_comment_count)
        self.assertEqual(
            response.content,
            b'Invalid comment or unauthenticated.'
        )

    def test_add_comment_get_returns_bad_request(self):
        """
        Test that a GET request to add a comment returns a 400 Bad Request.
        """
        response = self.client.get(
            reverse(
                'add_comment',
                args=[self.crumb.id]
            )
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content,
            b'Invalid comment or unauthenticated.'
        )

    def test_edit_comment_requires_login(self):
        """
        Test that editing a comment requires the user to be logged in.
        """
        self.client.logout()
        response = self.client.post(
            reverse(
                'edit_comment',
                args=[self.comment.id]
            ),
            {'content': 'Updated content'}
        )
        self.assertRedirects(
            response,
            f'{reverse("account_login")}?next={reverse(
                "edit_comment",
                args=[self.comment.id]
            )}'
        )

    def test_edit_comment_get_ajax_returns_form(self):
        """
        Test that editing a comment via AJAX returns the edit form.
        """
        response = self.client.get(
            reverse('edit_comment', args=[self.comment.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'feedback/includes/edit_comment_form.html'
        )
        self.assertContains(response, 'Write your comment here ...')

    def test_edit_comment_post_valid_ajax(self):
        """
        Test editing a comment via AJAX with valid data.
        """
        new_content = 'This comment has been updated successfully.'
        response = self.client.post(
            reverse('edit_comment', args=[self.comment.id]),
            {'content': new_content},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'success': True, 'content': new_content}
        )
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, new_content)

    def test_edit_comment_post_invalid_ajax(self):
        """
        Test editing a comment via AJAX with invalid data.
        """
        response = self.client.post(
            reverse('edit_comment', args=[self.comment.id]),
            {'content': 'Too'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                'success': False,
                'errors': {
                    'content': ['Ensure this value has at least 5 characters '
                                '(it has 3).']
                        }
                    }
                )
        self.comment.refresh_from_db()
        self.assertNotEqual(self.comment.content, 'Too')

    def test_edit_comment_post_valid_non_ajax_redirects(self):
        """
        Test editing a comment via non-AJAX request with valid data.
        """
        new_content = 'Updated content non-AJAX.'
        response = self.client.post(
            reverse('edit_comment', args=[self.comment.id]),
            {'content': new_content}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse(
                'crumb_detail',
                args=[self.crumb.id]
            ),
            target_status_code=302
        )
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, new_content)

    def test_edit_comment_other_user_comment_returns_404(self):
        """
        Test that editing a comment made by another user returns a 404.
        """
        other_comment = Comment.objects.create(
            user=self.other_user,
            crumb=self.crumb,
            content='Other user comment.'
        )
        response = self.client.post(
            reverse('edit_comment', args=[other_comment.id]),
            {'content': 'Attempted edit.'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_comment_requires_login(self):
        """
        Test that deleting a comment requires the user to be logged in.
        """
        self.client.logout()
        response = self.client.post(
            reverse(
                'delete_comment',
                args=[self.comment.id]
            )
        )
        self.assertRedirects(
            response,
            f'{reverse("account_login")}?next={reverse(
                "delete_comment", args=[self.comment.id]
            )}'
        )

    def test_delete_comment_post_ajax_success(self):
        """
        Test deleting a comment via AJAX with valid request.
        """
        initial_comment_count = Comment.objects.count()
        response = self.client.post(
            reverse('delete_comment', args=[self.comment.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})
        self.assertEqual(Comment.objects.count(), initial_comment_count - 1)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_other_user_comment_returns_404(self):
        """
        Test that deleting a comment made by another user returns a 404.
        """
        other_comment = Comment.objects.create(
            user=self.other_user,
            crumb=self.crumb,
            content='Other user comment to delete.'
        )
        initial_comment_count = Comment.objects.count()
        response = self.client.post(
            reverse('delete_comment', args=[other_comment.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Comment.objects.count(), initial_comment_count)

    def test_delete_comment_non_ajax_returns_bad_request(self):
        """
        Test that a non-AJAX request to delete a comment returns a 400
        Bad Request.
        """
        initial_comment_count = Comment.objects.count()
        response = self.client.post(
            reverse(
                'delete_comment',
                args=[self.comment.id]
            )
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Invalid request')
        self.assertEqual(Comment.objects.count(), initial_comment_count)

    def test_toggle_save_crumb_requires_login(self):
        """
        Test that toggling save crumb requires the user to be logged in.
        """
        self.client.logout()
        response = self.client.post(
            reverse(
                'toggle_save_crumb',
                args=[self.crumb.id]
            )
        )
        self.assertRedirects(
            response,
            f'{reverse("account_login")}?next={reverse(
                "toggle_save_crumb",
                args=[self.crumb.id]
            )}'
        )

    def test_toggle_save_crumb_save_new(self):
        """
        Test toggling save crumb to save a new crumb.
        """
        initial_saved_count = SavedCrumb.objects.count()
        response = self.client.post(
            reverse(
                'toggle_save_crumb',
                args=[self.crumb.id]
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'saved': True})
        self.assertEqual(SavedCrumb.objects.count(), initial_saved_count + 1)
        self.assertTrue(
            SavedCrumb.objects.filter(
                user=self.user,
                crumb=self.crumb
            ).exists()
        )

    def test_toggle_save_crumb_unsave_existing(self):
        """
        Test toggling save crumb to unsave an existing saved crumb.
        """
        SavedCrumb.objects.create(user=self.user, crumb=self.crumb)
        initial_saved_count = SavedCrumb.objects.count()
        response = self.client.post(
            reverse(
                'toggle_save_crumb',
                args=[self.crumb.id]
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'saved': False})
        self.assertEqual(SavedCrumb.objects.count(), initial_saved_count - 1)
        self.assertFalse(
            SavedCrumb.objects.filter(
                user=self.user,
                crumb=self.crumb
            ).exists())

    def test_toggle_save_crumb_other_user_saved_crumb(self):
        """
        Test toggling save crumb when another user has already saved it.
        """
        SavedCrumb.objects.create(user=self.other_user, crumb=self.crumb)
        initial_saved_count = SavedCrumb.objects.count()

        response = self.client.post(
            reverse(
                'toggle_save_crumb',
                args=[self.crumb.id]
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'saved': True})
        self.assertEqual(SavedCrumb.objects.count(), initial_saved_count + 1)
        self.assertTrue(
            SavedCrumb.objects.filter(
                user=self.user,
                crumb=self.crumb
            ).exists())
        self.assertTrue(
            SavedCrumb.objects.filter(
                user=self.other_user,
                crumb=self.crumb
            ).exists())

        response = self.client.post(
            reverse(
                'toggle_save_crumb',
                args=[self.crumb.id]
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'saved': False})
        self.assertEqual(SavedCrumb.objects.count(), initial_saved_count)
        self.assertFalse(
            SavedCrumb.objects.filter(
                user=self.user,
                crumb=self.crumb
            ).exists())
        self.assertTrue(
            SavedCrumb.objects.filter(
                user=self.other_user,
                crumb=self.crumb
            ).exists())
