from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

import app_settings
from allauth.invitations.models import InvitationKey


def accept(request, invitation_key, extra_context=None):
    if app_settings.INVITATION_REQUIRED:
        if invitation_key and InvitationKey.objects.is_key_valid(invitation_key):
            # store the invitation key in the session
            request.session['invitation_key'] = invitation_key
            return HttpResponseRedirect(reverse('account_signup'))
    return HttpResponseRedirect(reverse('account_login'))


# remaining_invitations_for_user = InvitationKey.objects.remaining_invitations_for_user

# def register(request, backend, success_url=None,
#             form_class=RegistrationForm,
#             disallowed_url='registration_disallowed',
#             post_registration_redirect=None,
#             template_name='registration/registration_form.html',
#             wrong_template_name='invitation/wrong_invitation_key.html',
#             extra_context=None):
#     extra_context = extra_context is not None and extra_context.copy() or {}
#     if getattr(settings, 'INVITE_MODE', False):
#         invitation_key = request.REQUEST.get('invitation_key', False)
#         if invitation_key:
#             extra_context.update({'invitation_key': invitation_key})
#             if is_key_valid(invitation_key):
#                 return registration_register(request, backend, success_url,
#                                             form_class, disallowed_url,
#                                             template_name, extra_context)
#             else:
#                 extra_context.update({'invalid_key': True})
#         else:
#             extra_context.update({'no_key': True})
#         return direct_to_template(request, wrong_template_name, extra_context)
#     else:
#         return registration_register(request, backend, success_url, form_class,
#                                      disallowed_url, template_name, extra_context)

# def invite(request, success_url=None,
#             form_class=InvitationKeyForm,
#             template_name='invitation/invitation_form.html',
#             extra_context=None):
#     extra_context = extra_context is not None and extra_context.copy() or {}
#     remaining_invitations = remaining_invitations_for_user(request.user)
#     if request.method == 'POST':
#         form = form_class(data=request.POST, files=request.FILES)
#         if remaining_invitations > 0 and form.is_valid():
#             invitation = InvitationKey.objects.create_invitation(request.user)
#             invitation.send_to(form.cleaned_data["email"])
#             # success_url needs to be dynamically generated here; setting a
#             # a default value using reverse() will cause circular-import
#             # problems with the default URLConf for this application, which
#             # imports this file.
#             return HttpResponseRedirect(success_url or reverse('invitation_complete'))
#     else:
#         form = form_class()
#     extra_context.update({
#             'form': form,
#             'remaining_invitations': remaining_invitations,
#         })
#     return direct_to_template(request, template_name, extra_context)
# invite = login_required(invite)
