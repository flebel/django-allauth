from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

import app_settings
from allauth.invitations.models import InvitationKey


def accept(request, invitation_key, extra_context=None):
    # accept invitations regardless of whether required or not
    if invitation_key and InvitationKey.objects.is_key_valid(invitation_key):
        # store the invitation key in the session
        request.session['invitation_key'] = invitation_key
        return HttpResponseRedirect(reverse('account_signup'))
    return HttpResponseRedirect(reverse('account_login'))

