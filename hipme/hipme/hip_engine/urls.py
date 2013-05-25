from django.conf.urls import patterns, include, url

urlpatterns = patterns('hip_engine.views',
    # classic views
    url(r'^$','test'),
    url(r'^forms/$','test_forms'),
    url(r'^login/$','login_form'),
)