from django.conf.urls import patterns, include, url

urlpatterns = patterns('hip_engine.views',
    
    # classic views

    url(r'^profile/(?P<username>\w+)/$','profile_activity'),
    url(r'^profile/(?P<username>\w+)/activity/$','profile_activity'),
    url(r'^profile/(?P<username>\w+)/collection/$','profile_collection'),
    url(r'^profile/(?P<username>\w+)/pending/$','profile_pending'),
    url(r'^profile/(?P<username>\w+)/followers/$','profile_followers'),
    url(r'^profile/(?P<username>\w+)/following/$','profile_following'),
    url(r'^profile/(?P<username>\w+)/edit/$','profile_edit'),
    url(r'^profile/(?P<username>\w+)/rankings/$','profile_rankings'),
    url(r'^profile/(?P<username>\w+)/follow/$','profile_follow'),

    url(r'^$','landing'),
    url(r'^betatesters/$','landing_private'),
    url(r'^feed/$','feed'),
    url(r'^login/$','landing'),
    url(r'^signup/$','landing'),
    url(r'^forms/$','test_forms'),
    url(r'^chosen/$','test_chosen'),

    # action views
    url(r'^register/$', 'register'),
    url(r'^login/process/$','login_process'),
    url(r'^logout/process/$','logout_process'),

    url(r'^search/$','search_profiles'),
    url(r'^search/profiles/','search_profiles'),
    url(r'^search/mixtapes/','search_mixtapes'),

    url(r'^create/mixtape/$', 'create_mixtape'),
    url(r'^mixtape/(?P<tracklist_id>\d+)/add/track/$', 'add_track'),
    url(r'^mixtape/(?P<tracklist_id>\d+)/bundle/(?P<bundle_id>\d+)/track/(?P<track_id>\d+)/keep/$', 'keep_track'),
    url(r'^mixtape/(?P<tracklist_id>\d+)/like/$', 'like_mixtape'),
    url(r'^mixtape/(?P<tracklist_id>\d+)/close/$', 'close_tracklist'),

    url(r'^feedback/$', 'give_feedback'),

    #admin action views
    url(r'^populate/db/$', 'populate_db'),
)