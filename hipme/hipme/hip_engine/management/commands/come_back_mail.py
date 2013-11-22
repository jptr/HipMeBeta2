from django.core.management.base import NoArgsCommand, CommandError
from django.core.mail import send_mail
from datetime import timedelta

from hip_engine.models import User, UserProfile, Track, Bundle, Tracklist, Tag, Event, Relationship, Suggestion, SavedEmail
from hip_engine.mailer import generate_header_come_back, generate_body_come_back

class Command(NoArgsCommand):
    help = 'Sends e-mail when user hasnt logged in the past 10, 20, 30... days'

    def handle_noargs(self, **options):

        for u in User.objects.all():
            delta_last_login = timezone.now() - u.last_login
            print delta_last_login