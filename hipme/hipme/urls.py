from django.conf.urls import patterns, include, url

from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('hip_engine.urls')),
)

#if settings.DEBUG:
    # static files (images, css, javascript, etc.)
# urlpatterns += patterns('',
#     (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
#     'document_root': settings.STATIC_ROOT}))

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )

