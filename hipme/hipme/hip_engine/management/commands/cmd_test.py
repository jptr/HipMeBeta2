from django.core.management.base import NoArgsCommand, CommandError
from django.core.mail import send_mail
from datetime import timedelta

from hip_engine.models import User, UserProfile, Track, Bundle, Tracklist, Tag, Event, Relationship, Suggestion, SavedEmail
from hip_engine.mailer import generate_header_new_mixtape, generate_body_new_mixtape

# your custom command must reference the base management classes like this:
class Command(NoArgsCommand):

    # send e-mail when time's up : owner needs to pick kept songs and close the mixtape.
    def handle_noargs(self, **options):
        send_mail('Subject', 'Body', 'test@ex.com', ['sim.frr@gmail.com'], fail_silently = False)
        self.stdout.write('mail envoyé')