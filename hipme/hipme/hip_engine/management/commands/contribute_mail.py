from django.core.management.base import NoArgsCommand, CommandError
from django.core.mail import send_mail
from datetime import timedelta

from hip_engine.models import User, UserProfile, Track, Bundle, Tracklist, Tag, Event, Relationship, Suggestion, SavedEmail
from hip_engine.mailer import generate_header_contribute, generate_body_contribute

class Command(NoArgsCommand):
    help = 'Sends e-mail when was called but has not contributed yet'

    def handle_noargs(self, **options):

        delta0 = timedelta(hours=48)
        delta1 = timedelta(hours=47)

        for tl in Tracklist.objects.all():
            # if 2 days left and tracklist not closed yet
            if tl.time_left < delta0 and tl.time_left > delta1 and not tl.is_finished:
                for user_to_mail in tl.userto.all():
                    # if contributor has not contributed yet and wants emails
                    if not tl.bundlebacks.filter(owner=user_to_mail) and user_to_mail.is_email_notified:
                        print "caca"
                        send_mail(generate_header_contribute(user_to_mail), generate_body_contribute(user_to_mail, tl), 'HipMe', [user_to_mail.user.email])

