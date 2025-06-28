from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Configuration for the Accounts app.
    This class is used to set up the app's name and any initialization
    that needs to be done when the app is ready.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        """
        This method is called when the app is ready.
        It imports the signals module to ensure that the signals are registered
        when the app is loaded.
        """
        import accounts.signals