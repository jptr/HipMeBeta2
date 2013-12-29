from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime
from datetime import timedelta
# the line above seems to solve total_seconds() issue when present
from django.utils import timezone
from hip_engine.validation_tools import get_streaming_site_from, get_stream_id

from PIL import Image

# Create your models here.
RELATIONSHIP_FOLLOWING = 1
RELATIONSHIP_BLOCKED = 2
RELATIONSHIP_STATUSES = (
    (RELATIONSHIP_FOLLOWING, 'Following'),
    (RELATIONSHIP_BLOCKED, 'Blocked'),
)

def upload_to(instance, filename):
    return 'profile_pics/%s/%s' % (instance.user.id, filename)

class UserProfile(models.Model):
    avatar = models.ImageField("Profile Pic", upload_to=upload_to, blank=True, null=True)
    user = models.OneToOneField(User)
    relationships = models.ManyToManyField('self', through='Relationship', 
                                           symmetrical=False, 
                                           related_name='related_to', blank=True)
    tracklist_kept = models.ManyToManyField('Tracklist', related_name='kept_by', blank=True)
    reputation = models.IntegerField(default=0)
    url = models.URLField(blank=True)
    is_email_notified = models.BooleanField('Get email notifications?', default=True)
    nb_connects = models.IntegerField(default=0, verbose_name=u'nb of connections')
    def __unicode__(self):
        return self.user.username
    def get_email_address(self):
        return self.user.email
    get_email_address.short_description = 'Email'
    def get_username(self):
        return self.user.username
    get_username.admin_order_field = 'user__username'

    def add_relationship(self, profile, status):
        relationship, created = Relationship.objects.get_or_create(
            from_profile=self,
            to_profile=profile,
            status=status)
        return relationship

    def add_following(self, profile):
        return self.add_relationship(profile, RELATIONSHIP_FOLLOWING)

    def remove_relationship(self, profile, status):
        Relationship.objects.filter(
            from_profile=self, 
            to_profile=profile,
            status=status).delete()
        return

    def remove_following(self, profile):
        return self.remove_relationship(profile, RELATIONSHIP_FOLLOWING)

    def get_relationships(self, status):
        return self.relationships.filter(
            to_profile__status=status, 
            to_profile__from_profile=self)

    def get_related_to(self, status):
        return self.related_to.filter(
            from_profile__status=status, 
            from_profile__to_profile=self)

    def get_following(self):
        return self.get_relationships(RELATIONSHIP_FOLLOWING)

    def get_followers(self):
        return self.get_related_to(RELATIONSHIP_FOLLOWING)

    def get_friends(self):
        return self.relationships.filter(
            to_profile__status=RELATIONSHIP_FOLLOWING, 
            to_profile__from_profile=self,
            from_profile__status=RELATIONSHIP_FOLLOWING, 
            from_profile__to_profile=self)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)

class Relationship(models.Model):
    from_profile = models.ForeignKey(UserProfile, related_name='from_profile')
    to_profile = models.ForeignKey(UserProfile, related_name='to_profile')
    status = models.IntegerField(choices=RELATIONSHIP_STATUSES)
    def __unicode__(self):
        if self.status == 1:
            return u"%s following %s" % (self.from_profile, self.to_profile)
        return u"%s blocking %s" % (self.from_profile, self.to_profile)

class Track(models.Model):
    url = models.URLField(help_text='from soundcloud, youtube, hypemachine, grooveshark, deezer')
    artist = models.CharField(max_length=200, blank=True, help_text='optional')
    name = models.CharField(max_length=200, blank=True, help_text='optional')
    bundle = models.ManyToManyField('Bundle', related_name='followed_by', null=True, blank=True)
    date_added = models.DateTimeField('date of creation', default=timezone.now)
    def __unicode__(self):
        if self.artist and not self.name:
            return u"song %s - %s - unknown name" % (self.id, self.artist)
        elif  not self.artist and self.name:
            return u"song %s - unknown artist -%s" % (self.id, self.name)
        elif  not self.artist and not self.name:
            return u"song %s - unknown artist - unknown name" % (self.id)
        else:
            return u"song %s - %s - %s" % (self.id, self.artist, self.name)
    def get_site_from(self):
        return get_streaming_site_from(self.url)
    get_site_from.short_description = 'Streaming source'
    site_from = property(get_site_from)
    def get_stream_id(self):
        return get_stream_id(self.url, self.site_from)
    get_site_from.short_description = 'Streaming ID'
    stream_id = property(get_stream_id)

class Bundle(models.Model):
    owner = models.ForeignKey(UserProfile, related_name='bundles_created')
    tracks = models.ManyToManyField('Track', related_name='bundle_from', blank=True)
    tracks_kept = models.ManyToManyField('Track', related_name='bundle_kept_from', blank=True)
    date_created = models.DateTimeField('date of creation', default=timezone.now)
    nb_tracks_kept = models.IntegerField(default=0)

    def __unicode__(self):
        return u"bundle %s created by %s" % (self.id, self.owner)

class Event(models.Model):
    main_profile = models.ForeignKey(UserProfile, related_name='main_events')
    secondary_profile = models.ForeignKey(UserProfile, related_name='secondary_events', null=True)
    date = models.DateTimeField('date', default=timezone.now)
    event_type = models.CharField(max_length=20)
    def __unicode__(self):
        return u"event %s - %s by %s" % (self.id, self.event_type, self.main_profile)
    def get_time_delta(self):   
        timeDiff = timezone.now() - self.date
        return timeDiff

    time_delta = property(get_time_delta)

class Tracklist(models.Model):
    owner = models.ForeignKey(UserProfile, related_name='tracklists_created')
    userto = models.ManyToManyField('UserProfile', verbose_name=u'to', related_name='tracklists_contributed', help_text='type any username')
    title = models.CharField(max_length=50, blank=True, help_text='max 50 characters')
    description = models.CharField(max_length=200, blank=True, help_text='max 200 characters')

    date_created = models.DateTimeField('date of creation', default=timezone.now)
    date_latest_edit = models.DateTimeField('date of latest edit', default=timezone.now)
    latest_event = models.ForeignKey(Event, blank=True)

    tracks_initial = models.ManyToManyField('Track', related_name='tracklist_from', blank=True)
    tracks_kept = models.ManyToManyField('Track', related_name='tracklist_kept_from', blank=True)
    bundlebacks = models.ManyToManyField('Bundle', related_name='tracklist_from', null=True, blank=True)
    is_finished = models.BooleanField('finished?', default=False)

    tags = models.ManyToManyField('Tag', blank=True)
    likes = models.IntegerField(default=0)

    def get_time_left(self):
        timeDiff = datetime.timedelta(days=7) + self.date_created - timezone.now()
        return timeDiff

    def get_time_out(self):
        timeDiff = datetime.timedelta(days=7) + self.date_created - timezone.now()
        # secondsLeft = timeDiff.total_seconds()
        secondsLeft = timeDiff.seconds + (timeDiff.days * 24 * 36000)
        # solves total_seconds issue if present
        if secondsLeft > 0:
            return False
        else:
            return True

    is_time_out = property(get_time_out)
    time_left = property(get_time_left)

    def get_time_delta(self):   
        timeDiff = timezone.now() - self.date_latest_edit
        return timeDiff

    time_delta = property(get_time_delta)

    def __unicode__(self):
        return u"tracklist %s created by %s - %s" % (self.id, self.owner, self.title)

class Tag(models.Model):
    name = models.CharField(max_length=40, help_text='optional')
    def __unicode__(self):
        return self.name

class Suggestion(models.Model):
    userfrom = models.ForeignKey(UserProfile)
    body = models.TextField(max_length=1000)
    kind = models.TextField(max_length=16, default="")
    submit_date = models.DateTimeField('submit date', default=timezone.now)

    def get_summary(self):
        if len(self.body)>140:
            return self.body[:137]+"..."
        else:
            return self.body
    get_summary.short_description = 'extract'

class SavedEmail(models.Model):
    email = models.CharField(max_length=200)
    submit_date = models.DateTimeField('submit date', default=timezone.now)
    def __unicode__(self):
        return self.email