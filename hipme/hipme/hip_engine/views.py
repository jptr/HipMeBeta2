from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.forms.models import inlineformset_factory, modelformset_factory
from hip_engine.forms import ProfileEmailNotificationForm, UserEmailForm, TracklistForm, TrackForm

from hip_engine.models import User, UserProfile, Track, Bundle, Tracklist

from hip_engine.validation_tools import validateEmail, validateUsername

from django.core.urlresolvers import reverse

def login_form(request):
    if not request.user.is_authenticated():
        redirect_to = request.GET.get('next','')
        return render_to_response('hip_engine/login.html', {'redirect_to': redirect_to}, context_instance=RequestContext(request))
    else:
        return profile(request)

@login_required
def profile(request):
    return render_to_response('hip_engine/profile_activity.html', context_instance=RequestContext(request))

def profile_activity(request):
    tracklist_form = TracklistForm(instance=request.user, username=request.user.username)
    track_form = TrackForm()

    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile())|Tracklist.objects.filter(userto = request.user.get_profile())
    tracklist_list = tracklist_queryset.distinct().order_by('-date_last_edit')[:10]

    return render_to_response('hip_engine/profile_activity.html', {'tracklist_list':tracklist_list,'tracklist_form':tracklist_form, 'track_form':track_form}, context_instance=RequestContext(request))

def profile_my_pending(request):

    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_created')[:10]

    return render_to_response('hip_engine/profile_my_pending.html', {'tracklist_list':tracklist_list,}, context_instance=RequestContext(request))

def profile_pending_contributions(request):

    tracklist_queryset = Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_created')[:10]

    return render_to_response('hip_engine/profile_pending_contributions.html', context_instance=RequestContext(request))

def my_music_all(request):
    return render_to_response('hip_engine/listen11_my_music_all.html', context_instance=RequestContext(request))

def my_music_my(request):
    return render_to_response('hip_engine/listen12_my_music_my.html', context_instance=RequestContext(request))

def network_newest(request):
    return render_to_response('hip_engine/listen21_network_newest.html', context_instance=RequestContext(request))

def network_popular(request):
    return render_to_response('hip_engine/listen22_network_popular.html', context_instance=RequestContext(request))

@login_required
def test_forms(request):
    email_form = UserEmailForm(instance=request.user)
    email_notif_form = ProfileEmailNotificationForm(instance=request.user)

    tracklist_form = TracklistForm(instance=request.user, username=request.user.username)

    track_form = TrackForm()

    # tracklist_formset = TracklistFormset(initial=[{'owner': request.user.get_profile(), 'bundlego':bundlego}])

    return render_to_response('hip_engine/forms.html', {'email_form':email_form, 'email_notif_form':email_notif_form, 'tracklist_form':tracklist_form, 'track_form':track_form}, context_instance=RequestContext(request))

# action views
def logout_process(request):
    logout(request)
    return HttpResponseRedirect(reverse('hip_engine.views.login_form'))

def login_process(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            if request.GET.get('next',''):
                url = request.GET.get('next','')
                return HttpResponseRedirect(url)
            else:
                return HttpResponseRedirect(reverse('hip_engine.views.profile_activity'))
        else:
            return render_to_response('hip_engine/forms.html', {'error_message': "Sorry, your account has been disabled.",}, context_instance=RequestContext(request)) 
    else:
        return render_to_response('hip_engine/forms.html', {'error_message': "Your username and password do not match. Please try again.",}, context_instance=RequestContext(request))  

def register(request):
    username = request.POST['username']
    email_1 = request.POST['email_1']
    email_2 = request.POST['email_2']
    password = request.POST['password']
    if username and email_1 and email_2 and password:
        if validateUsername(username):
            if not User.objects.filter(username=username):
                if email_1==email_2:
                    if validateEmail(email_1):
                        user = User.objects.create_user(username, email_1, password)
                        login_process(request)
                        return HttpResponseRedirect(reverse('hip_engine.views.test_forms'))
                    else:
                        return render_to_response('hip_engine/forms.html', {'username':username, 'email_1':email_1, 'email_2':email_2, 'password':password, 'error_message_email': "Your email is not valid. Please try again",}, context_instance=RequestContext(request))
                else:
                    return render_to_response('hip_engine/forms.html', {'username':username, 'email_1':email_1, 'email_2':email_2, 'password':password, 'error_message_email': "Your emails do not match. Please try again",}, context_instance=RequestContext(request))
            else:
                return render_to_response('hip_engine/forms.html', {'username':username, 'email_1':email_1, 'email_2':email_2, 'password':password, 'error_message_username': "Username already exists. Please choose another one.",}, context_instance=RequestContext(request))
        else:
            return render_to_response('hip_engine/forms.html', {'username':username, 'email_1':email_1, 'email_2':email_2, 'password':password, 'error_message_username': "Username is not valid. Please use only letters, numbers, '-' and '_'.",}, context_instance=RequestContext(request))
    else:
        return render_to_response('hip_engine/forms.html', {'username':username, 'email_1':email_1, 'email_2':email_2, 'password':password, 'error_message_fields': "You must fill in all of the fields.",}, context_instance=RequestContext(request))