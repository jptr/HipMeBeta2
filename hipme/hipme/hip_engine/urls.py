from django.conf.urls import patterns, include, url

urlpatterns = patterns('hip_engine.views',
    
    # classic views

    url(r'^profile/(?P<username>\w+)/$','profile_activity'),
    url(r'^profile/(?P<username>\w+)/activity/$','profile_activity'),
    url(r'^profile/(?P<username>\w+)/collection/$','profile_collection'),
    url(r'^profile/(?P<username>\w+)/pending/$','profile_pending'),
    url(r'^profile/(?P<username>\w+)/followers/$','profile_followers'),
    url(r'^profile/(?P<username>\w+)/following/$','profile_following'),

    url(r'^$','landing'),
    url(r'^feed/$','feed'),
    url(r'^login/$','landing'),
    url(r'^signup/$','landing'),

    url(r'^forms/$','test_forms'),
    url(r'^people/$', 'profile'),

    # action views
    url(r'^register/$', 'register'),
    url(r'^login/process/$','login_process'),
    url(r'^search/$','search_people'),
    url(r'^search/people/$','search_people'),
    url(r'^search/mixtapes/$','search_mixtapes'),

    url(r'^create/mixtape/$', 'create_mixtape'),
)