from django.conf.urls import patterns, include, url

from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('hip_engine.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )

urlpatterns += patterns('',
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
	'document_root': settings.MEDIA_ROOT}))

    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)