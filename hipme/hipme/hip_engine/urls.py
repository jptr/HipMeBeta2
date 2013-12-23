from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^user/password/reset/$', 
        'django.contrib.auth.views.password_reset', 
        {'post_reset_redirect' : '/user/password/reset/done/'},
        name="password_reset"),
    (r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'),
    (r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 
        'django.contrib.auth.views.password_reset_confirm', 
        {'post_reset_redirect' : '/user/password/done/'}),
    (r'^user/password/done/$', 
        'django.contrib.auth.views.password_reset_complete'),
)

urlpatterns += patterns('hip_engine.views',
    
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

    url(r'^mixtape/(?P<tracklist_id>\d+)/$', 'mixtape_display'),
    url(r'^mixtape/(?P<tracklist_id>\d+)/edit/$', 'mixtape_edit'),

    url(r'^tag/(?P<urlized_tag_name>[A-Za-z0-9_\+]+)/$', 'tag_display'),

    url(r'^$','landing'),
    url(r'^feed/$','feed'),
    url(r'^login/$','landing'),
    url(r'^signup/$','landing'),

    # action views
    url(r'^register/$', 'register'),
    url(r'^login/process/$','login_process'),
    url(r'^logout/process/$','logout_process'),

    url(r'^search/$','search_profiles'),
    url(r'^search/profiles/','search_profiles'),
    url(r'^search/mixtapes/','search_mixtapes'),
    url(r'^suggested/profiles/$','suggest_profiles'),

    url(r'^create/mixtape/$', 'mixtape_create'),
    url(r'^mixtape/(?P<tracklist_id>\d+)/add/track/$', 'add_track'),
    url(r'^mixtape/(?P<tracklist_id>\d+)/bundle/(?P<bundle_id>\d+)/track/(?P<track_id>\d+)/keep/$', 'keep_track'),
    url(r'^mixtape/(?P<tracklist_id>\d+)/like/$', 'like_mixtape'),
    url(r'^mixtape/(?P<tracklist_id>\d+)/close/$', 'close_tracklist'),

    url(r'^feedback/$', 'give_feedback'),
    url(r'^saveemail/$', 'save_email'),

    #admin action views
    url(r'^populate/db/$', 'populate_db'),

    url(r'^reset/reputation/$', 'reset_reputation'),
    url(r'^reset/connects/$', 'reset_nb_connects'),
)