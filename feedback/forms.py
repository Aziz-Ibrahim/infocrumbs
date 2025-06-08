from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    """
    Form for adding a comment to a Crumb.
    This form includes a single field for the comment content.
    It uses a Textarea widget for better user experience.
    """

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write your comment here...',
                'class': 'form-control'
            }),
        }
