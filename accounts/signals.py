from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.hashers import check_password

from .emails import send_security_alert_email
from .models import CustomUser, Profile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Creates a Profile instance for the user when a CustomUser is created.
    This signal is triggered after a CustomUser instance is saved.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    Saves the Profile instance when a CustomUser is saved.
    This signal is triggered after a CustomUser instance is saved.
    """
    instance.profile.save()


User = get_user_model()


# --- Signal for User Changes (Password & Profile Details) ---
@receiver(pre_save, sender=User)
def track_user_changes_pre_save(sender, instance, **kwargs):
    """
    Stores the original field values of a User instance
    (including password hash)
    before it's saved. This allows comparison in post_save.
    """
    if instance.pk:
        try:
            original_user = sender.objects.get(pk=instance.pk)
            # Store original values for post_save comparison
            instance.__original_email = original_user.email
            instance.__original_first_name = original_user.first_name
            instance.__original_last_name = original_user.last_name
            instance.__original_password_hash = original_user.password
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def user_changes_security_alert(sender, instance, created, **kwargs):
    """
    Sends a security alert email if sensitive user details (including password)
    are updated. Triggered after a User instance is saved.
    """
    if created:
        return

    changed_fields = []
    password_changed = False

    request = kwargs.get('request', None)
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('X-Forwarded-For')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

    # Compare current instance values with original values stored in pre_save
    if hasattr(
        instance,
        '__original_email'
    ) and instance.__original_email != instance.email:
        changed_fields.append("email address")
    if hasattr(
        instance,
        '__original_first_name'
    ) and instance.__original_first_name != instance.first_name:
        changed_fields.append("first name")
    if hasattr(
        instance,
        '__original_last_name'
    ) and instance.__original_last_name != instance.last_name:
        changed_fields.append("last name")

    if hasattr(
        instance,
        '__original_password_hash'
    ) and instance.__original_password_hash != instance.password:
        password_changed = True
        changed_fields.append("password")

    if password_changed or changed_fields:
        change_description = ""
        if password_changed and changed_fields:
            other_fields_changed = [
                field for field in changed_fields if field != 'password'
            ]
            if other_fields_changed:
                change_description = (
                    f"password and profile details "
                    f"({', '.join(other_fields_changed)}) updated"
                )
                change_description = "password changed"
        elif password_changed:
            change_description = "password changed"
        elif changed_fields:
            change_description = (
                f"profile details ({', '.join(changed_fields)}) updated"
            )

        try:
            send_security_alert_email(instance, change_description, ip_address)
            print(
                f"DEBUG: Security alert email sent for {change_description} "
                f"to {instance.email}."
            )
        except Exception as e:
            print(
                f"ERROR: Failed to send security alert email "
                f"for {change_description} to {instance.email}: {e}"
            )
