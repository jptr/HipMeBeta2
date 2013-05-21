from hip_engine.models import User, UserProfile, Track, Bundle, Tracklist
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

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline, )

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username','reputation','is_email_notified','get_email_address')
    inlines = [TracklistCreatedInline, BundleCreatedInline, ]
    list_filter = ('is_email_notified',)

class TracklistAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','is_finished', 'date_created','date_last_edit')

class TrackAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','get_site_from','artist','name', 'date_added')

class BundleAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','is_bundlego','date_created')
    list_filter = ('is_bundlego',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Tracklist, TracklistAdmin)
admin.site.register(Bundle, BundleAdmin)
admin.site.register(Track, TrackAdmin)