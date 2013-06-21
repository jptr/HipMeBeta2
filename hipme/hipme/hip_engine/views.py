from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.forms.models import inlineformset_factory, modelformset_factory
from hip_engine.forms import ProfileEmailNotificationForm, UserEmailForm, TracklistForm, TrackForm

from hip_engine.models import User, UserProfile, Track, Bundle, Tracklist, Tag
from hip_engine.search import get_query

from hip_engine.validation_tools import validateEmail, validateUsername, parseTags
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from django.core.urlresolvers import reverse

from django.utils.html import escape

from django.utils import timezone

# generic context methods
def get_nav_context():
    nb_mixtapes = Tracklist.objects.all().count()
    nb_users = UserProfile.objects.all().count()
    nb_tracks = Track.objects.all().count()
    return {'nb_users':nb_users, 'nb_mixtapes':nb_mixtapes, 'nb_tracks':nb_tracks}

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

def get_rankings(request):
    profile_queryset = UserProfile.objects.filter(followed_by=request.user.get_profile())
    profile_list = profile_queryset.distinct().order_by('-reputation')
    for index in range(len(profile_list)):
        if profile_list[index].reputation > request.user.get_profile().reputation:
            profile_list = profile_list[index-2:index+2]
            break
    profile_list.insert(2, request.user.get_profile())
    context = {'ranking_profile_list':profile_list,}
    return context

def get_generic_context(request):
    context = {}
    context.update(get_tracklist_form_context(request))
    context.update(get_nav_context())
    return context

# display views
def landing(request):
    if not request.user.is_authenticated():
        redirect_to = request.GET.get('next','')
        return render_to_response('hip_engine/landing_page.html', {'redirect_to': redirect_to}, context_instance=RequestContext(request))
    else:
        return feed(request)

@login_required
def populate_db(request):
    if request.user.username == "hipmaster":
        from hip_engine.hipme_db_setup_3 import INSTANCES
        for instance in INSTANCES:
            if instance["model"] == "UserProfile":

                username = instance["username"]
                email = instance["email"]
                password = instance["password"]

                user = User.objects.create_user(username, email, password)

            if instance["model"] == "TrackList":

                owner = get_object_or_404(UserProfile,user__username=instance["owner"])
                title = instance["title"]
                # description = instance["description"]
                is_finished = instance["is_finished"]

                tracklist = Tracklist(
                    owner = owner, 
                    title = title, 
                    # description = description, 
                    is_finished=is_finished
                )
                tracklist.save()

                bundlebacks = instance["bundlebacks"]

                if instance["tags"]:
                    for tag_name in instance["tags"]:
                        tag_name = tag_name.title()
                        tag_name = " ".join(tag_name.split())
                        tag = Tag(name=tag_name)
                        tag.save()
                        tracklist.tags.add(tag)

                if instance["tracks"]:
                    for track_dic in instance["tracks"]:
                        url = track_dic["url"]
                        artist = track_dic["artist"]
                        name = track_dic["name"]
                        track = Track(url=url, artist=artist, name=name)
                        track.save()
                        tracklist.tracks_initial.add(track)

                if instance["bundlebacks"]:
                    for bundleback_dic in instance["bundlebacks"]:
                        owner = get_object_or_404(UserProfile,user__username=bundleback_dic["owner"])
                        bundleback = Bundle(owner=owner)
                        bundleback.save()                
                        for track_dic in bundleback_dic["tracks"]:
                            url = track_dic["url"]
                            artist = track_dic["artist"]
                            name = track_dic["name"]
                            track = Track(url=url, artist=artist, name=name)
                            track.save()
                            bundleback.tracks.add(track)
                        tracklist.userto.add(owner)
                        tracklist.bundlebacks.add(bundleback)

        return render_to_response('hip_engine/populate_success.html', {}, context_instance=RequestContext(request))
    else:
        return feed(request)

@login_required
def feed(request):
    # tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_queryset = Tracklist.objects.all()
    tracklist_list = tracklist_queryset.distinct().order_by('-date_latest_event')[:10]

    context = {
        'tracklist_list':tracklist_list,
    }
    context.update(get_generic_context(request))

    return render_to_response('hip_engine/feed.html', context, context_instance=RequestContext(request))

@login_required
def profile(request, username):
    return profile_activity(request, username)

@login_required
def profile_activity(request, username):
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_latest_event')[:10]

    context = {
        'tracklist_list':tracklist_list,
    }
    context.update(get_profile_context(username))
    context.update(get_generic_context(request))

    return render_to_response('hip_engine/profile_activity.html', context, context_instance=RequestContext(request))

@login_required
def profile_collection(request, username):
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_latest_event')[:10]

    context = {
        'tracklist_list':tracklist_list,
    }
    context.update(get_profile_context(username))
    context.update(get_generic_context(request))

    return render_to_response('hip_engine/profile_collection.html', context, context_instance=RequestContext(request))

@login_required
def profile_pending(request, username):
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_latest_event')[:10]

    context = {
        'tracklist_list':tracklist_list,
    }
    context.update(get_profile_context(username))
    context.update(get_generic_context(request))

    return render_to_response('hip_engine/profile_pending.html', context, context_instance=RequestContext(request))

@login_required
def profile_followers(request, username):
    followers_list = profile_focused.followed_by.all()
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_latest_event')[:10]

    context = {
        'tracklist_list':tracklist_list,
        'followers_list':follwing_list,
    }
    context.update(get_profile_context(username))
    context.update(get_generic_context(request))

    return render_to_response('hip_engine/profile_followers.html', context, context_instance=RequestContext(request))

@login_required
def profile_following(request, username):
    following_list = profile_focused.follows.all()
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_latest_event')[:10]

    context = {
        'tracklist_list':tracklist_list,
        'following_list':follwing_list,
    }
    context.update(get_profile_context(username))
    context.update(get_generic_context(request))

    return render_to_response('hip_engine/profile_following.html', context, context_instance=RequestContext(request))

@login_required
def search(request):
    query_string = ''
    found_profiles = None
    found_tracklists = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        profile_query = get_query(query_string, ['user__username',])
        tracklist_query = get_query(query_string, ['title', 'tags__name', 'owner__user__username', 'tracks_initial__artist', 'tracks_initial__name', 'tracks_kept__artist', 'tracks_kept__tracks__name'])
        found_tracklists = Tracklist.objects.filter(message_query).order_by('-date_latest_event')
        found_profiles = UserProfile.objects.filter(user_query).order_by('user__username')

    return render_to_response('hip_engine/search_results.html', {'query_string': query_string, 'tracklist_list': found_tracklists, 'profile_list': found_profiles}, context_instance=RequestContext(request))

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
                url = request.POST.get('url'+i_str)
                artist = request.POST.get('artist'+i_str)
                title = request.POST.get('title'+i_str)
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
                        tracklist.tracks_initial.add(track)
                    except ValidationError, e:
                        return render_to_response('hip_engine/forms.html', {'error_message': "Some track urls are not valid. Please check the url fields.",}, context_instance=RequestContext(request))
    
        title = request.POST.get('title')
        if title:
            tracklist.title = title

        tracklist.latest_event = tracklist.owner.user.username + " created a new mixtape."

        # description = request.POST.get('description')
        # if description:
        #     tracklist.description = description

        string_tags = request.POST.get('tags')
        if string_tags:
            tags = parseTags(string_tags)
            for tag_name in tags:
                if Tag.objects.filter(name=tag_name):
                    tag = get_object_or_404(Tag, name=tag_name)
                    tracklist.tags.add(tag)
                else:
                    tag = Tag(name=tag_name)
                    tag.save()
                    tracklist.tags.add(tag)

        tracklist.save()

    if request.POST.get('next'):
        url_next = request.POST['next']
        return HttpResponseRedirect(url_next)
    else:
        return HttpResponseRedirect(reverse('hip_engine.views.feed'))

@login_required
def add_track(request, tracklist_id):
    tracklist = get_object_or_404(Tracklist, pk=tracklist_id)
    # if tracklist.userto.filter(user=request.user):
    url = request.POST.get('url')
    artist = request.POST.get('artist')
    name = request.POST.get('name')
    track = Track(url=url, artist=artist, name=name)
    track.save()
    if tracklist.bundlebacks.filter(owner=request.user.get_profile()):
        bundleback = get_object_or_404(Bundle, owner=request.user.get_profile())
    else:
        bundleback = Bundle(owner=request.user.get_profile())
        bundleback.save()

    bundleback.tracks.add(track)
    bundleback.save()

    tracklist.bundlebacks.add(bundleback)
    tracklist.date_latest_event = timezone.now()
    tracklist.date_latest_edit = timezone.now()
    tracklist.latest_event = request.user.username + " added a track to " + tracklist.owner.user.username +"'s mixtape."
    tracklist.save()

    if request.POST.get('next'):
        url_next = request.POST['next']
        return HttpResponseRedirect(url_next)
    else:
        return HttpResponseRedirect(reverse('hip_engine.views.feed'))

@login_required
def keep_track(request, tracklist_id, bundle_id, track_id):
    tracklist = get_object_or_404(Tracklist, pk=tracklist_id)
    bundleback = get_object_or_404(Bundle, pk=bundle_id)
    track = get_object_or_404(Track, pk=track_id)

    tracklist.tracks_kept.add(track)
    tracklist.date_latest_event = timezone.now()
    tracklist.save()

    bundleback.owner.reputation += 1
    bundleback.owner.save()

    bundleback.nb_tracks_kept += 1
    bundleback.save()

    if request.POST.get('next'):
        url_next = request.POST['next']
        return HttpResponseRedirect(url_next)
    else:
        return HttpResponseRedirect(reverse('hip_engine.views.feed'))

@login_required
def remove_track(request, tracklist_id, bundle_id, track_id):
    tracklist = get_object_or_404(Tracklist, pk=tracklist_id)
    bundleback = get_object_or_404(Bundle, pk=bundle_id)
    track = get_object_or_404(Track, pk=track_id)

    tracklist.tracks_kept.remove(track)
    tracklist.date_latest_event = timezone.now()
    tracklist.save()

    bundleback.owner.reputation -= 1
    bundleback.owner.save()

    bundleback.nb_tracks_kept -= 1
    bundleback.save()

    if request.POST.get('next'):
        url_next = request.POST['next']
        return HttpResponseRedirect(url_next)
    else:
        return HttpResponseRedirect(reverse('hip_engine.views.feed'))

@login_required
def close_tracklist(request, tracklist_id):
    tracklist = get_object_or_404(Tracklist, pk=tracklist_id)
    if tracklist.owner == request.user.get_profile():
        tracklist.is_finished = True
        tracklist.date_latest_event = timezone.now()
        tracklist.date_latest_edit = tracklist.date_latest_event
        tracklist.latest_event = tracklist.owner__user__username + " finished his mixtape."
        tracklist.save()

    if request.POST.get('next'):
        url_next = request.POST['next']
        return HttpResponseRedirect(url_next)
    else:
        return HttpResponseRedirect(reverse('hip_engine.views.feed'))

def logout_process(request):
    logout(request)
    return HttpResponseRedirect(reverse('hip_engine.views.landing'))

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
                return HttpResponseRedirect(reverse('hip_engine.views.feed'))
        else:
            return render_to_response('hip_engine/forms.html', {'error_message': "Sorry, your account has been disabled.",}, context_instance=RequestContext(request)) 
    else:
        return render_to_response('hip_engine/forms.html', {'error_message': "Your username and password do not match. Please try again.",}, context_instance=RequestContext(request))  

def register(request):
    username = request.POST['username']
    email_1 = request.POST['email_1']
    email_2 = request.POST['email_2']
    password = request.POST['password']
    context = {'username':username, 'email_1':email_1, 'email_2':email_2, 'password':password, }
    all_fields = True
    for field_key in ['username', 'email_1', 'email_2', 'password']:
        if not request.POST[field_key]:
            all_fields = False
            if 'email' in field_key:
                context.update({'error_message_email': "You must fill in all of the fields.",})
            else:
                context.update({'error_message_username': "You must fill in all of the fields.",})
    if all_fields:
        if validateUsername(username):
            if not User.objects.filter(username=username):
                if email_1==email_2:
                    if not User.objects.filter(email=email_1):
                        if validateEmail(email_1):
                            user = User.objects.create_user(username, email_1, password)
                            login_process(request)
                            return HttpResponseRedirect(reverse('hip_engine.views.feed'))
                        else:
                            context.update({'error_message_email': "Your email is not valid. Please try again",})
                            return render_to_response('hip_engine/landing_page.html', context, context_instance=RequestContext(request))
                    else:
                        context.update({'error_message_email': "Email already exists. Please choose another one",})
                        return render_to_response('hip_engine/landing_page.html', context, context_instance=RequestContext(request)) 
                else:
                    context.update({'error_message_email': "Your emails do not match. Please try again",})
                    return render_to_response('hip_engine/landing_page.html', context, context_instance=RequestContext(request))
            else:
                context.update({'error_message_username': "Username already exists. Please choose another one.",})
                return render_to_response('hip_engine/landing_page.html', context, context_instance=RequestContext(request))
        else:
            context.update({'error_message_username': "Username is not valid. Please use only letters, numbers, '-' and '_'.",})
            return render_to_response('hip_engine/landing_page.html', context, context_instance=RequestContext(request))
    else:
        return render_to_response('hip_engine/landing_page.html', context, context_instance=RequestContext(request))

