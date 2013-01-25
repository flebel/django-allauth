from django.contrib import admin
from models import InvitationKey, InvitationUser


class InvitationKeyAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'key', 'from_user', 'date_invited', 'registrant', 'key_expired', 'reusable', 'use_count',)


class InvitationUserAdmin(admin.ModelAdmin):
    list_display = ('inviter', 'invitations_remaining')

admin.site.register(InvitationKey, InvitationKeyAdmin)
admin.site.register(InvitationUser, InvitationUserAdmin)
