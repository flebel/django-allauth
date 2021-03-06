import random
import datetime
import re

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

import app_settings

SHA1_RE = re.compile('^[a-f0-9]{40}$')
TEXT_RE = re.compile('^[a-z]{1,10}$')


class InvitationKeyManager(models.Manager):
    def get_key(self, invitation_key):
        """
        Return InvitationKey, or None if it doesn't (or shouldn't) exist.
        """
        # Don't bother hitting database if invitation_key doesn't match patterns.
        if not SHA1_RE.search(invitation_key) and not TEXT_RE.search(invitation_key):
            return None

        try:
            key = self.get(key=invitation_key)
        except self.model.DoesNotExist:
            return None
        return key

    def is_key_valid(self, invitation_key):
        """
        Check if an ``InvitationKey`` is valid or not, returning a boolean,
        ``True`` if the key is valid.
        """
        invitation_key = self.get_key(invitation_key)
        return invitation_key and invitation_key.is_usable()

    def create_invitation(self, user):
        """
        Create an ``InvitationKey`` and returns it.

        The key for the ``InvitationKey`` will be a SHA1 hash, generated
        from a combination of the ``User``'s username and a random salt.
        """
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        key = sha_constructor("%s%s%s" % (now(), salt, user.username)).hexdigest()
        return self.create(from_user=user, key=key)

    def remaining_invitations_for_user(self, user):
        """
        Return the number of remaining invitations for a given ``User``.
        """
        invitation_user, created = InvitationUser.objects.get_or_create(
            inviter=user,
            defaults={'invitations_remaining': app_settings.INVITATIONS_PER_USER})
        return invitation_user.invitations_remaining

    def delete_expired_keys(self):
        for key in self.all():
            if key.key_expired():
                key.delete()


class InvitationKey(models.Model):
    key = models.CharField(_('invitation key'), max_length=40)
    date_invited = models.DateTimeField(_('date invited'), default=now)
    from_user = models.ForeignKey(User, related_name='invitations_sent')
    registrant = models.ForeignKey(User, null=True, blank=True,
                                  related_name='invitations_used')
    reusable = models.BooleanField(default=False)
    use_count = models.IntegerField(default=0)

    objects = InvitationKeyManager()

    def __unicode__(self):
        return u"Invitation from %s on %s" % (self.from_user.username, self.date_invited)

    def is_usable(self):
        """
        Return whether this key is still valid for registering a new user.
        """
        if self.reusable:
            return True
        return self.registrant is None and not self.key_expired()

    def key_expired(self):
        """
        Determine whether this ``InvitationKey`` has expired, returning
        a boolean -- ``True`` if the key has expired.

        The date the key has been created is incremented by the number of days
        specified in the setting ``ACCOUNT_INVITATION_DAYS`` (which should be
        the number of days after invite during which a user is allowed to
        create their account); if the result is less than or equal to the
        current date, the key has expired and this method returns ``True``.

        """
        expiration_date = datetime.timedelta(days=app_settings.INVITATION_DAYS)
        return self.date_invited + expiration_date <= now()
    key_expired.boolean = True

    def mark_used(self, registrant):
        """
        Note that this key has been used to register a new user.
        """
        self.registrant = registrant
        self.use_count += 1
        self.save()

    def send_to(self, email, request=None, **kwargs):
        """
        Send an invitation email to ``email``.
        """
        current_site = kwargs["site"] if "site" in kwargs else Site.objects.get_current()
        invitation_url = reverse("invitations_accept", args=[self.key])
        if request:
            invitation_url = request.build_absolute_uri(invitation_url)
        else:
            invitation_url = 'http://' + current_site.domain + invitation_url
        subject = render_to_string('invitations/invitation_email_subject.txt',
                                   {'site': current_site,
                                     'invitation_key': self})
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message = render_to_string('invitations/invitation_email.txt',
                                   {'invitation': self,
                                    'invitation_url': invitation_url,
                                    'expiration_days': app_settings.INVITATION_DAYS,
                                    'site': current_site})

        send_mail(subject, message, app_settings.DEFAULT_FROM_EMAIL, [email])


class InvitationUser(models.Model):
    inviter = models.ForeignKey(User, unique=True)
    invitations_remaining = models.IntegerField()

    def __unicode__(self):
        return u"InvitationUser for %s" % self.inviter.username


def user_post_save(sender, instance, created, **kwargs):
    """Create InvitationUser for user when User is created."""
    if created:
        invitation_user = InvitationUser()
        invitation_user.inviter = instance
        invitation_user.invitations_remaining = app_settings.INVITATIONS_PER_USER
        invitation_user.save()

models.signals.post_save.connect(user_post_save, sender=User)


def invitation_key_post_save(sender, instance, created, **kwargs):
    """Decrement invitations_remaining when InvitationKey is created."""
    if created:
        invitation_user = InvitationUser.objects.get(inviter=instance.from_user)
        remaining = invitation_user.invitations_remaining
        invitation_user.invitations_remaining = remaining - 1
        invitation_user.save()

models.signals.post_save.connect(invitation_key_post_save, sender=InvitationKey)
