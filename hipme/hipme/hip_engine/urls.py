from django.conf.urls import patterns, include, url

urlpatterns = patterns('hip_engine.views',
    
    # classic views

    url(r'^$','profile_activity'),
    url(r'^profile/$','profile_activity'),
    url(r'^profile/activity/$','profile_activity'),
    url(r'^profile/pendingmixtapes/$','profile_my_pending'),
    url(r'^profile/pendingcontributions/$','profile_pending_contributions'),

    url(r'^listen/$','my_music_all'),
    url(r'^listen/mymusic/$','my_music_all'),
    url(r'^listen/mymixtapes/$','my_music_my'),
    url(r'^listen/newest/$','network_newest'),
    url(r'^listen/popular/$','network_popular'),

    url(r'^forms/$','test_forms'),
    url(r'^login/$','login_form'),
    url(r'^people/$', 'profile'),

    # action views
    url(r'^register/$', 'register'),
)