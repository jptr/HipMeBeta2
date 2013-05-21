from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime
from django.utils import timezone
# import PIL

# Create your models here.

def upload_to(instance, filename):
    return 'profile_pics/%s/%s' % (instance.user.id, filename)

class UserProfile(models.Model):
    # avatar = models.ImageField("Profile Pic", upload_to=upload_to, blank=True, null=True)
    user = models.OneToOneField(User)
    follows = models.ManyToManyField('UserProfile', related_name='followed_by')
    tracklist = models.ManyToManyField('Tracklist', related_name='followed_by')
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
    url = models.URLField()
    artist = models.CharField(max_length=200, blank=True)
    name = models.CharField(max_length=200, blank=True)
    bundle = models.ManyToManyField('Bundle', related_name='followed_by', null=True, blank=True)
    date_added = models.DateTimeField('date of creation', default=timezone.now())
    def __unicode__(self):
        if self.artist and not self.name:
            return u"song %s - %s - unknown name" % (self.id, self.artist)
        elif  not self.artist and self.name:
            return u"song %s - unknown artist -%s" % (self.id, self.name)
        elif  not self.artist and not self.name:
            return u"song %s - unknown artist - unknown name" % (self.id, self.name)
        else:
            return u"song %s - %s - %s" % (self.id, self.artist, self.name, self.url)
    def get_site_from(self):
        return get_streaming_site_from(self.url)
    get_site_from.short_description = 'Streaming source'
    site_from = property(get_site_from)

class Bundle(models.Model):
    owner = models.ForeignKey(UserProfile, related_name='bundles_created')
    tracks = models.ManyToManyField('Track', related_name='bundle_from')
    is_bundlego = models.BooleanField('bundlego?', default=False)
    date_created = models.DateTimeField('date of creation', default=timezone.now())

    def __unicode__(self):
        return u"bundle %s created by %s" % (self.id, self.owner)

class Tracklist(models.Model):
    owner = models.ForeignKey(UserProfile, related_name='tracklists_created')
    title = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=200, blank=True)
    date_created = models.DateTimeField('date of creation', default=timezone.now())
    date_last_edit = models.DateTimeField('date of last edit', default=timezone.now())
    bundlego = models.ForeignKey(Bundle, related_name='tracklist_created')
    bundlebacks = models.ManyToManyField('Bundle', related_name='tracklist_from', null=True, blank=True)
    is_finished = models.BooleanField('finished?', default=False)

    def __unicode__(self):
        return u"tracklist %s created by %s - %s" % (self.id, self.owner, self.title)