from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

SOCIALACCOUNT_ENABLED = 'allauth.socialaccount' in settings.INSTALLED_APPS

if SOCIALACCOUNT_ENABLED:
    if 'allauth.socialaccount.context_processors.socialaccount' \
            not in settings.TEMPLATE_CONTEXT_PROCESSORS:
        raise ImproperlyConfigured("socialaccount context processor "
                    "not found in settings.TEMPLATE_CONTEXT_PROCESSORS."
                    "See settings.py instructions here: "
                    "https://github.com/pennersr/django-allauth#installation")

LOGIN_REDIRECT_URL = getattr(settings, 'LOGIN_REDIRECT_URL', '/')

USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

INVITATIONS_ENABLED = getattr(settings, 'ACCOUNT_INVITATIONS_ENABLED', False)
INVITATION_REQUIRED = getattr(settings, 'ACCOUNT_INVITATION_REQUIRED', False)
NO_INVITATION_REDIRECT = getattr(settings, 'ACCOUNT_NO_INVITATION_REDIRECT', False)
