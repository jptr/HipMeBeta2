from django.core.management.base import NoArgsCommand, CommandError
from django.core.mail import send_mail
from datetime import timedelta

from hip_engine.models import User, UserProfile, Track, Bundle, Tracklist, Tag, Event, Relationship, Suggestion, SavedEmail
from hip_engine.mailer import generate_header_mixtape_to_close, generate_body_mixtape_to_close

# your custom command must reference the base management classes like this:
class Command(NoArgsCommand):
    help = 'Sends e-mail to owner when time is up (must keep and close)'

    # send e-mail when time's up : owner needs to pick kept songs and close the mixtape.
    def handle_noargs(self, **options):

        # define a time delta, from the moment when the time is up to one hour later.
        # the cron job will check every hour if some mixtapes are in this time delta.
        delta0 = timedelta(hours=0)
        delta1 = timedelta(hours=-1)

        for tl in Tracklist.objects.all():
            user_mail_to = tl.owner

            # if in the delta and if not already closed and if user wants emails
            if tl.time_left < delta0 and tl.time_left > delta1 and not tl.is_finished and user_to_mail.is_email_notified:
                send_mail(generate_header_mixtape_to_close(tl), generate_body_mixtape_to_close(user_to_mail, tl), 'HipMe', [user_to_mail.user.email])

