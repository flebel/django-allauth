from django.conf import settings

INVITATION_REQUIRED = getattr(settings, 'ACCOUNT_INVITATION_REQUIRED', False)
NO_INVITATION_REDIRECT = getattr(settings, 'ACCOUNT_NO_INVITATION_REDIRECT', False)
INVITATION_DAYS = getattr(settings, 'ACCOUNT_INVITATION_DAYS', 7)
INVITATIONS_PER_USER = getattr(settings, 'ACCOUNT_INVITATIONS_PER_USER', 5)

DEFAULT_FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL')
