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

# --- Signal for Password Change ---
@receiver(pre_save, sender=User)
def password_changed_security_alert(sender, user, request, **kwargs):
    """
    Sends a security alert email when a user's password is changed.
    """
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('X-Forwarded-For')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

    try:
        send_security_alert_email(user, "password changed", ip_address)
        print(
            f"DEBUG: Security alert email sent for password change to "
            f"{user.email}."
        )
    except Exception as e:
        print(
            f"ERROR: Failed to send security alert email for password "
            f"change to {user.email}: {e}")


# --- Signal for Profile Details Update ---
@receiver(pre_save, sender=User)
def track_user_changes_pre_save(sender, instance, **kwargs):
    """
    Stores the original field values of a User instance before it's saved.
    This allows us to compare changes in post_save.
    """
    if instance.pk:
        try:
            original_user = sender.objects.get(pk=instance.pk)
            instance.__original_email = original_user.email
            instance.__original_first_name = original_user.first_name
            instance.__original_last_name = original_user.last_name
        except sender.DoesNotExist:
            pass

@receiver(post_save, sender=User)
def profile_details_changed_security_alert(sender, instance, created, **kwargs):
    """
    Sends a security alert email if sensitive user details are updated.
    This signal is triggered after a User instance is saved.
    """
    if created:
        return

    changed_fields = []
    
    request = kwargs.get('request', None) 
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('X-Forwarded-For')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

    if hasattr(
        instance, '__original_email'
    ) and instance.__original_email != instance.email:
        changed_fields.append("email address")
    if hasattr(
        instance, '__original_first_name'
    ) and instance.__original_first_name != instance.first_name:
        changed_fields.append("first name")
    if hasattr(
        instance, '__original_last_name'
    ) and instance.__original_last_name != instance.last_name:
        changed_fields.append("last name")

    if changed_fields:
        change_description = (
            f"profile details ({', '.join(changed_fields)}) updated"
        )
        try:
            send_security_alert_email(instance, change_description, ip_address)
            print(
                f"DEBUG: Security alert email sent for profile update "
                f"to {instance.email}."
            )
        except Exception as e:
            print(
                f"ERROR: Failed to send security alert email for "
                f"profile update to {instance.email}: {e}"
            )
