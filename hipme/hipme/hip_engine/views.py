from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.forms.models import inlineformset_factory, modelformset_factory
from hip_engine.forms import ProfileEmailNotificationForm, UserEmailForm, TracklistForm, TrackForm

from hip_engine.models import User, UserProfile, Track, Bundle, Tracklist

from hip_engine.validation_tools import validateEmail, validateUsername
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from django.core.urlresolvers import reverse

# generic context methods
def get_profile_context(username):
    profile_focused = get_object_or_404(UserProfile,user__username=username)
    nb_followers = profile_focused.followed_by.count()
    nb_following = profile_focused.follows.count()
    return {'profile_focused':profile_focused, 'nb_followers':nb_followers, 'nb_following':nb_following,}

def get_tracklist_form_context(request):
    new_tracklist = Tracklist(owner = request.user.get_profile())
    tracklist_form = TracklistForm(prefix='tracklist', instance=new_tracklist, username=request.user.username)
    track_form = TrackForm()
    context = {'tracklist_form':tracklist_form, 'track_form': track_form,}
    return context

# display views
def landing(request):
    if not request.user.is_authenticated():
        redirect_to = request.GET.get('next','')
        return render_to_response('hip_engine/landing_page.html', {'redirect_to': redirect_to}, context_instance=RequestContext(request))
    else:
        return feed(request)

@login_required
def feed(request):
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_created')[:10]

    context = {
        'tracklist_list':tracklist_list,
    }
    context.update(get_tracklist_form_context(request))

    return render_to_response('hip_engine/feed.html', context, context_instance=RequestContext(request))

@login_required
def profile(request, username):
    return profile_activity(request, username)

@login_required
def profile_activity(request, username):
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_created')[:10]

    context = {
        'tracklist_list':tracklist_list,
    }
    context.update(get_profile_context(username))
    context.update(get_tracklist_form_context(request))

    return render_to_response('hip_engine/profile_activity.html', context, context_instance=RequestContext(request))

@login_required
def profile_collection(request, username):
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_created')[:10]

    context = {
        'tracklist_list':tracklist_list,
    }
    context.update(get_profile_context(username))
    context.update(get_tracklist_form_context(request))

    return render_to_response('hip_engine/profile_collection.html', context, context_instance=RequestContext(request))

@login_required
def profile_pending(request, username):
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_created')[:10]

    context = {
        'tracklist_list':tracklist_list,
    }
    context.update(get_profile_context(username))
    context.update(get_tracklist_form_context(request))

    return render_to_response('hip_engine/profile_pending.html', context, context_instance=RequestContext(request))

@login_required
def profile_followers(request, username):
    followers_list = profile_focused.followed_by.all()
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_created')[:10]

    context = {
        'tracklist_list':tracklist_list,
        'followers_list':follwing_list,
    }
    context.update(get_profile_context(username))
    context.update(get_tracklist_form_context(request))

    return render_to_response('hip_engine/profile_followers.html', context, context_instance=RequestContext(request))

@login_required
def profile_following(request, username):
    following_list = profile_focused.follows.all()
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_created')[:10]

    context = {
        'tracklist_list':tracklist_list,
        'following_list':follwing_list,
    }
    context.update(get_profile_context(username))
    context.update(get_tracklist_form_context(request))

    return render_to_response('hip_engine/profile_following.html', context, context_instance=RequestContext(request))

@login_required
def search_people(request):

    tracklist_form = TracklistForm(username=request.user.username)
    track_form = TrackForm()
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_created')[:10]

    return render_to_response('hip_engine/search_people.html', {'tracklist_list':tracklist_list,'tracklist_form':tracklist_form, 'track_form':track_form,}, context_instance=RequestContext(request))

@login_required
def search_mixtapes(request):

    tracklist_form = TracklistForm(username=request.user.username)
    track_form = TrackForm()
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_created')[:10]

    return render_to_response('hip_engine/search_mixtapes.html', {'tracklist_list':tracklist_list,'tracklist_form':tracklist_form, 'track_form':track_form,}, context_instance=RequestContext(request))

@login_required
def test_forms(request):
    email_form = UserEmailForm(instance=request.user)
    email_notif_form = ProfileEmailNotificationForm(instance=request.user)

    tracklist_form = TracklistForm(username=request.user.username)

    track_form = TrackForm()

    # tracklist_formset = TracklistFormset(initial=[{'owner': request.user.get_profile(), 'bundlego':bundlego}])

    return render_to_response('hip_engine/forms.html', {'email_form':email_form, 'email_notif_form':email_notif_form, 'tracklist_form':tracklist_form, 'track_form':track_form}, context_instance=RequestContext(request))

# action views
@login_required
def create_mixtape(request):
    tracklist_form = TracklistForm(request.POST, prefix='tracklist')
    if tracklist_form.is_valid():
        tracklist = tracklist_form.save()
        for i_str in ["_1","_2","_3"]:
                url = request.POST['url'+i_str]
                artist = request.POST['artist'+i_str]
                title = request.POST['title'+i_str]
                if url:
                    validate = URLValidator()
                    try:
                        validate(url)
                        track = Track(url=url)
                        if artist:
                            track.artist = artist
                        if title:
                            track.title = title
                        track.save()
                        tracklist.tracks.add(track)
                    except ValidationError, e:
                        return render_to_response('hip_engine/forms.html', {'error_message': "Some track urls are not valid. Please check the url fields.",}, context_instance=RequestContext(request))
        tracklist.save()

    if request.POST.get('next'):
        url_next = request.POST['next']
        return HttpResponseRedirect(url_next)
    else:
        return HttpResponseRedirect(reverse('hip_engine.views.feed'))

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
                return HttpResponseRedirect(reverse('hip_engine.views.profile'))
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

