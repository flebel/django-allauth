import logging
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from allauth.invitations.models import InvitationKey


class Command(BaseCommand):
    help = "Send a new invitation to an email address from admin"
    args = "<email>"

    def handle(self, *args, **options):
        logger = self._get_logger()
        if len(args) != 1:
            raise CommandError("Please provide an email address")
        user = self.get_admin()
        invite = InvitationKey.objects.create_invitation(user)
        logger.info('Sending invite to: %s' % args[0])
        invite.send_to(args[0])

    def get_admin(self):
        try:
            return User.objects.filter(is_staff=True)[0]
        except KeyError:
            raise CommandError("No admin found")

    def _get_logger(self):
        logger = logging.getLogger(__name__)
        stream = logging.StreamHandler(self.stdout)
        logger.addHandler(stream)
        logger.setLevel(logging.DEBUG)
        return logger
