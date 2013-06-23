from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime
from django.utils import timezone
from hip_engine.validation_tools import get_streaming_site_from

# import PIL

# Create your models here.

def upload_to(instance, filename):
    return 'profile_pics/%s/%s' % (instance.user.id, filename)

class UserProfile(models.Model):
    # avatar = models.ImageField("Profile Pic", upload_to=upload_to, blank=True, null=True)
    user = models.OneToOneField(User)
    follows = models.ManyToManyField('UserProfile', related_name='followed_by', blank=True)
    tracklist_kept = models.ManyToManyField('Tracklist', related_name='followed_by', blank=True)
    reputation = models.IntegerField(default=0)
    url = models.URLField(blank=True)
    is_email_notified = models.BooleanField('get email notifications?', default=True)
    def __unicode__(self):
        return self.user.username
    def get_email_address(self):
        return self.user.email
    get_email_address.short_description = 'Email'
    def get_username(self):
        return self.user.username
    get_username.admin_order_field = 'user__username'

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)

class Track(models.Model):
    url = models.URLField(help_text='from soundcloud, youtube, hypemachine, grooveshark, deezer')
    artist = models.CharField(max_length=200, blank=True, help_text='optionnal')
    name = models.CharField(max_length=200, blank=True, help_text='optionnal')
    bundle = models.ManyToManyField('Bundle', related_name='followed_by', null=True, blank=True)
    date_added = models.DateTimeField('date of creation', default=timezone.now())
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
    def get_track_web_id(self):
        return get_web_id(self.url, site_from)
    get_site_from.short_description = 'Web ID'
    web_id = property(get_site_from)      

class Bundle(models.Model):
    owner = models.ForeignKey(UserProfile, related_name='bundles_created')
    tracks = models.ManyToManyField('Track', related_name='bundle_from', blank=True)
    date_created = models.DateTimeField('date of creation', default=timezone.now())
    nb_tracks_kept = models.IntegerField(default=0)

    def __unicode__(self):
        return u"bundle %s created by %s" % (self.id, self.owner)

class Event(models.Model):
    main_profile = models.ForeignKey(UserProfile, related_name='main_events')
    secondary_profile = models.ForeignKey(UserProfile, related_name='secondary_events', null=True)
    date = models.DateTimeField('date', default=timezone.now())
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

    date_created = models.DateTimeField('date of creation', default=timezone.now())
    date_latest_edit = models.DateTimeField('date of latest edit', default=timezone.now())
    latest_event = models.ForeignKey(Event)

    tracks_initial = models.ManyToManyField('Track', related_name='tracklist_from', blank=True)
    tracks_kept = models.ManyToManyField('Track', related_name='tracklist_kept_from', blank=True)
    bundlebacks = models.ManyToManyField('Bundle', related_name='tracklist_from', null=True, blank=True)
    is_finished = models.BooleanField('finished?', default=False)

    tags = models.ManyToManyField('Tag', null=True, blank=True)
    likes = models.IntegerField(default=0)

    def get_time_left(self):
        timeDiff = datetime.timedelta(days=3) + self.date_created - timezone.now()
        return timeDiff

    def get_time_out(self):
        timeDiff = datetime.timedelta(days=3) + self.date_created - timezone.now()
        seconds = timeDiff.seconds
        if seconds > 0:
            return False
        else:
            return True

    is_time_out = property(get_time_out)
    time_left = property(get_time_left)

    def get_time_delta(self):   
        timeDiff = timezone.now() - self.date_created
        return timeDiff

    time_delta = property(get_time_delta)

    def __unicode__(self):
        return u"tracklist %s created by %s - %s" % (self.id, self.owner, self.title)

class Tag(models.Model):
    name = models.CharField(max_length=40, help_text='optionnal')
    def __unicode__(self):
        return self.name