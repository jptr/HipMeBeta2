from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
import PIL

# Create your models here.

def upload_to(instance, filename):
    return 'profile_pics/%s/%s' % (instance.user.id, filename)

class UserProfile(models.Model):
    # avatar = models.ImageField("Profile Pic", upload_to=upload_to, blank=True, null=True)
    user = models.OneToOneField(User)
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
    title = models.CharField(max_length=200, blank=True)
    def __unicode__(self):
        if self.artist and not self.name:
            return u"song %s - %s - unknown title" % (self.id, self.artist)
        elif  not self.artist and self.name:
            return u"song %s - unknown artist -%s" % (self.id, self.title)
        else:
            return u"song %s - %s - %s - %s" % (self.id, self.artist, self.title, self.url)
    def get_site_from(self):
        return get_streaming_site_from(self.url)
    get_site_from.short_description = 'Streaming source'
    site_from = property(get_site_from)