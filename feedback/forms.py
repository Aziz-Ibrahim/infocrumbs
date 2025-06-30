from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    """
    Form for adding a comment to a Crumb.
    This form includes a single field for the comment content with
    min/max length validation.
    """
    # Define the comment_body field directly with min/max length
    comment_body = forms.CharField(
        label="",
        min_length=5,
        max_length=500,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Write your comment here ...',
            'class': 'form-control'
        }),
        help_text="Your comment should be between 5 and 500 characters."
    )

    class Meta:
        """
        Meta class to define the model and fields for the form.
        We use an empty fields list to indicate that we are overriding the
        default fields with our custom field.
        """
        model = Comment
        fields = []

    def save(self, commit=True):
        comment = super().save(commit=False)
        comment.content = self.cleaned_data['comment_body']
        if commit:
            comment.save()
        return comment
