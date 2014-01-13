from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^user/password/reset/$', 
        'django.contrib.auth.views.password_reset', 
        {'post_reset_redirect' : '/user/password/reset/done/'},
        name="password_reset"),
    (r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'),
    (r'^user/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 
        'django.contrib.auth.views.password_reset_confirm', 
        {'post_reset_redirect' : '/user/password/done/'}),
    (r'^user/password/done/$', 
        'django.contrib.auth.views.password_reset_complete'),
)

urlpatterns += patterns('hip_engine.views',
    
    # classic views

    url(r'^profile/(?P<username>[a-zA-Z0-9\-_]+)/$','profile_activity'),
    url(r'^profile/(?P<username>[a-zA-Z0-9\-_]+)/activity/$','profile_activity'),
    url(r'^profile/(?P<username>[a-zA-Z0-9\-_]+)/collection/$','profile_collection'),
    url(r'^profile/(?P<username>[a-zA-Z0-9\-_]+)/pending/$','profile_pending'),
    url(r'^profile/(?P<username>[a-zA-Z0-9\-_]+)/followers/$','profile_followers'),
    url(r'^profile/(?P<username>[a-zA-Z0-9\-_]+)/following/$','profile_following'),
    url(r'^profile/(?P<username>[a-zA-Z0-9\-_]+)/edit/$','profile_edit'),
    url(r'^profile/(?P<username>[a-zA-Z0-9\-_]+)/rankings/$','profile_rankings'),

    url(r'^mixtape/(?P<tracklist_id>\d+)/$', 'mixtape_display'),
    url(r'^mixtape/(?P<tracklist_id>\d+)/edit/$', 'mixtape_edit'),

    url(r'^tag/(?P<urlized_tag_name>[A-Za-z0-9_\+\-]+)/$', 'tag_display'),

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
    url(r'^mixtape/(?P<tracklist_id>\d+)/add/track/$', 'mixtape_add_track'),
    url(r'^mixtape/(?P<tracklist_id>\d+)/bundle/(?P<bundle_id>\d+)/track/(?P<track_id>\d+)/keep/$', 'mixtape_keep_track'),
    url(r'^mixtape/(?P<tracklist_id>\d+)/like/$', 'mixtape_like'),
    url(r'^mixtape/(?P<tracklist_id>\d+)/close/$', 'mixtape_close'),

    url(r'^mixtape/(?P<tracklist_id>\d+)/ajaxlike/$', 'mixtape_ajax_like'),
    url(r'^mixtape/(?P<tracklist_id>\d+)/ajaxunlike/$', 'mixtape_ajax_unlike'),

    url(r'^mixtape/(?P<tracklist_id>\d+)/bundle/(?P<bundle_id>\d+)/track/(?P<track_id>\d+)/ajaxkeep/$', 'mixtape_ajax_keep_track'),

    url(r'^profile/(?P<user_id>\d+)/ajaxfollow/$','profile_ajax_follow'),

    url(r'^feedback/$', 'give_feedback'),
    url(r'^saveemail/$', 'save_email'),

    #admin action views
    url(r'^populate/db/$', 'populate_db'),

    url(r'^reset/reputation/$', 'reset_reputation'),
    url(r'^reset/connects/$', 'reset_nb_connects'),

    url(r'^mail/welcome/$', 'mail_welcome'),
    url(r'^mail/welcome/send/$', 'mail_welcome_send'),
    url(r'^mail/welcome/success/$', 'mail_welcome_success'),
)