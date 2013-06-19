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

class Tracklist(models.Model):
    owner = models.ForeignKey(UserProfile, related_name='tracklists_created')
    userto = models.ManyToManyField('UserProfile', verbose_name=u'to', related_name='tracklists_contributed', help_text='type any username')
    title = models.CharField(max_length=50, blank=True, help_text='max 50 characters')
    description = models.CharField(max_length=200, blank=True, help_text='max 200 characters')

    date_created = models.DateTimeField('date of creation', default=timezone.now())
    date_latest_event = models.DateTimeField('date of latest event', default=timezone.now())
    date_latest_edit = models.DateTimeField('date of latest edit', default=timezone.now())
    latest_event = models.CharField(max_length=200, blank=True)

    tracks_initial = models.ManyToManyField('Track', related_name='tracklist_from', blank=True)
    tracks_kept = models.ManyToManyField('Track', related_name='tracklist_kept_from', blank=True)
    bundlebacks = models.ManyToManyField('Bundle', related_name='tracklist_from', null=True, blank=True)
    is_finished = models.BooleanField('finished?', default=False)
    tags = models.ManyToManyField('Tag', null=True, blank=True)

    def get_time_string(timeDiff):
        days = timeDiff.days
        hours = timeDiff.seconds/3600
        minutes = timeDiff.seconds%3600/60
        seconds = timeDiff.seconds%3600%60
        str = ""
        tStr = ""
        if days > 0:
            if days == 1:   tStr = "day"
            else:           tStr = "days"
            str = str + "%s %s" %(days, tStr)
            return str
        elif hours > 0:
            if hours == 1:  tStr = "hour"
            else:           tStr = "hours"
            str = str + "%s %s" %(hours, tStr)
            return str
        elif minutes > 0:
            if minutes == 1:tStr = "min"
            else:           tStr = "mins"           
            str = str + "%s %s" %(minutes, tStr)
            return str
        elif seconds > 0:
            if seconds == 1:tStr = "sec"
            else:           tStr = "secs"
            str = str + "%s %s" %(seconds, tStr)
            return str
        else:
            return "1 sec"

    def get_time_left():
        timeDiff = datetime.timedelta(days=3) + self.date_created - timezone.now()
        seconds = timeDiff.seconds%3600%60
        if timeDiff.seconds > 0:
            return self.get_time_string(timeDiff)+" left"
        else:
            return ""

    def get_time_out():
        timeDiff = datetime.timedelta(days=3) + self.date_created - timezone.now()
        seconds = timeDiff.seconds%3600%60
        if timeDiff.seconds > 0:
            return False
        else:
            return True

    is_time_out = property(get_time_out)
    time_left = property(get_time_left)

    def get_time_delta(self):   
        timeDiff = timezone.now() - self.date_created
        return self.get_time_string(timeDiff)+" ago"

    time_delta = property(get_time_delta)

    def __unicode__(self):
        return u"tracklist %s created by %s - %s" % (self.id, self.owner, self.title)

class Tag(models.Model):
    name = models.CharField(max_length=40, help_text='optionnal')
    def __unicode__(self):
        return self.name