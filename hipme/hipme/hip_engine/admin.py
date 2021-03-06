from hip_engine.models import User, UserProfile, Track, Bundle, Tracklist, Tag, Event, Relationship, Suggestion, SavedEmail
from django.contrib import admin

class TracklistCreatedInline(admin.TabularInline):
    model = Tracklist
    fk_name = 'owner'
    extra=1
    verbose_name="tracklist created"

class BundleCreatedInline(admin.TabularInline):
    model = Bundle
    fk_name = 'owner'
    extra=1
    verbose_name="bundle created"

class FollowingInline(admin.TabularInline):
    model = Relationship
    fk_name = 'from_profile'
    extra=0
    verbose_name="following"

class FollowerInline(admin.TabularInline):
    model = Relationship
    fk_name = 'to_profile'
    extra=0
    verbose_name="follower"

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline, )

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username','reputation','is_email_notified','get_email_address', 'nb_connects')
    inlines = [FollowingInline, FollowerInline, TracklistCreatedInline, BundleCreatedInline, ]
    list_filter = ('is_email_notified',)

class TracklistAdmin(admin.ModelAdmin):
    list_display = ('title','owner','__unicode__','is_finished', 'is_time_out', 'date_created','date_latest_edit')

class TrackAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','get_site_from','artist','name', 'date_added')

class BundleAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','date_created')

class TagAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)

class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type','main_profile','secondary_profile','date','__unicode__',)

class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)

class SuggestionAdmin(admin.ModelAdmin):
    list_display=('kind','userfrom', 'get_summary','submit_date',)

class SavedEmailAdmin(admin.ModelAdmin):
    list_display=('__unicode__','submit_date')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Tracklist, TracklistAdmin)
admin.site.register(Bundle, BundleAdmin)
admin.site.register(Track, TrackAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Relationship, RelationshipAdmin)
admin.site.register(Suggestion, SuggestionAdmin)
admin.site.register(SavedEmail, SavedEmailAdmin)