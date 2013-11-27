from django.core.management.base import NoArgsCommand, CommandError
from django.core.mail import send_mail
from django.utils import timezone

from hip_engine.models import User, UserProfile, Track, Bundle, Tracklist, Tag, Event, Relationship, Suggestion, SavedEmail
from hip_engine.mailer import generate_header_come_back, generate_body_come_back

class Command(NoArgsCommand):
    help = 'Sends e-mail when user hasnt logged in the past 10, 20, 30... days'

    def handle_noargs(self, **options):

        for user_to_mail in UserProfile.objects.all():
            delta_last_login = timezone.now() - user_to_mail.user.last_login
            delta_last_login_days = delta_last_login.days
            # if it's been 10, 20, 30... (and not 0) days the user did not show up, e-mail
            if delta_last_login_days % 10 == 0 and delta_last_login_days != 0:
                send_mail(generate_header_come_back(), generate_body_come_back(user_to_mail), 'HipMe', [user_to_mail.user.email], fail_silently=True)
