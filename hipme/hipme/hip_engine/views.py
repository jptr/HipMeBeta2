from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.forms.models import inlineformset_factory, modelformset_factory
# from hip_engine.forms import ProfileEmailNotificationForm, UserEmailForm, TracklistForm, TrackForm

from hip_engine.models import User, UserProfile, Track, Bundle, Tracklist

def login_form(request):
    if not request.user.is_authenticated():
        redirect_to = request.GET.get('next','')
        return render_to_response('hip_engine/login.html', {'redirect_to': redirect_to}, context_instance=RequestContext(request))
    else:
        return test(request)

def test(request):
    return render_to_response('hip_engine/listen22_network_music_popular.html', context_instance=RequestContext(request))

# @login_required
# def test_forms(request):
#     email_form = UserEmailForm(instance=request.user)
#     email_notif_form = ProfileEmailNotificationForm(instance=request.user)

#     tracklist_form = TracklistForm(instance=request.user, username=request.user.username)

#     track_form = TrackForm()
#     # tracklist_formset = TracklistFormset(initial=[{'owner': request.user.get_profile(), 'bundlego':bundlego}])

#     return render_to_response('hip_engine/forms.html', {'email_form':email_form, 'email_notif_form':email_notif_form, 'tracklist_form':tracklist_form, 'track_form':track_form}, context_instance=RequestContext(request))