from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.forms.models import inlineformset_factory, modelformset_factory
from hip_engine.forms import ProfileImageForm, ProfileEmailNotificationForm, UserEmailForm, TracklistForm, TrackForm

from PIL import Image
from django.conf import settings
from settings import MEDIA_ROOT
from os.path import join

from hip_engine.models import User, UserProfile, Track, Bundle, Tracklist, Tag, Event, Relationship, Suggestion, SavedEmail
from hip_engine.search_tools import get_query

from hip_engine.validation_tools import validateEmail, validateUsername, parseTags
from hip_engine.tools import rescale_square
from hip_engine.mailer import generate_header_new_mixtape, generate_body_new_mixtape
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
    return {'profile_focused':profile_focused, }

def get_tracklist_form_context(request):
    event = get_object_or_404(Event, pk=1)
    new_tracklist = Tracklist(owner = request.user.get_profile(), latest_event = event)
    tracklist_form = TracklistForm(prefix='tracklist', instance=new_tracklist, username=request.user.username)
    context = {'tracklist_form':tracklist_form, }
    return context

def suggest_profiles(request):
    from django.db.models import Count

    suggested_profiles =  []
    following_queryset = request.user.get_profile().get_following()

    if following_queryset:
        # if has friends, take 10 most connected second degree following
        followings_username = [following.user.username for following in following_queryset] 
        followings_username.append(request.user.get_profile())
        second_degree_followings = []
        
        for following in following_queryset:
            second_degree_followings += list(following.get_following().exclude(user__username__in=followings_username))
        
        if len(second_degree_followings) != 0:
            suggested_profiles_with_count = []
            
            for following in set(second_degree_followings):
                suggested_profiles_with_count.append((following, second_degree_followings.count(following)))
            suggested_profiles_with_count.sort(key = lambda x: -x[1])
            suggested_profiles = list(zip(*suggested_profiles_with_count)[0])[:10]
        
        if len(suggested_profiles) < 10:
            # suggest 10 most connected users on hipme not followed yet.
            all_users_sorted = list(UserProfile.objects.annotate(num_relationships=Count('relationships')).order_by('-num_relationships'))
            for person in all_users_sorted:
                if len(suggested_profiles) >= 10:
                    break
                elif person != request.user.get_profile() and person not in request.user.get_profile().get_following() and person not in suggested_profiles:
                    suggested_profiles.append(person)

    else:
        # if no friends, suggest 10 most connected users
        suggested_profiles = list(UserProfile.objects.annotate(num_relationships=Count('relationships')).order_by('-num_relationships').exclude(user=request.user.get_profile())[:10])

    context = {"suggested_profiles":suggested_profiles,}
    context.update(get_generic_context(request))
    context.update(get_rankings(request))

    return render_to_response('hip_engine/suggested_profiles.html', context, context_instance=RequestContext(request))

def get_rankings(request):
    my_index = 0
    in_list = False

    follows_queryset = request.user.get_profile().get_following()
    profile_list = list(follows_queryset.distinct().order_by('-reputation'))

    for index in range(len(profile_list)):
        if profile_list[index].reputation <= request.user.get_profile().reputation:
            profile_list.insert(index, request.user.get_profile())
            my_index = index
            in_list = True
            break

    if in_list == False:
        profile_list.append(request.user.get_profile())
        my_index = len(profile_list)-1

    mini_rank_list = [request.user.get_profile()]

    if my_index > 0:
        mini_rank_list.insert(0, profile_list[my_index-1])
    if my_index > 1:
        mini_rank_list.insert(0, profile_list[my_index-2])
    if my_index < len(profile_list)-1:
        mini_rank_list.append(profile_list[my_index+1])
    if my_index < len(profile_list)-2:
        mini_rank_list.append(profile_list[my_index+2])

    context = {'ranking_profile_list':mini_rank_list,}
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

def save_email(request):
    semail_text = request.POST['email_temp']
    context = {}

    if validateEmail(semail_text):
        semail = SavedEmail(email = request.POST['email_temp'], submit_date = timezone.now())
        semail.save()
        context.update({'info_message_saved_email': "Awesome, you're in.",})
        return render_to_response('hip_engine/landing_page.html', context, context_instance=RequestContext(request))

    else:
        context.update({'error_message_saved_email': "Your email is not valid. Please try again.",})
        return render_to_response('hip_engine/landing_page.html', context, context_instance=RequestContext(request))

@login_required
def populate_db(request):
    if request.user.username == "hipmaster":
        from hip_engine.hipme_db_setup_clean import INSTANCES
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

                event = Event(main_profile = owner, event_type = "creation")
                event.save()

                tracklist = Tracklist(
                    owner = owner, 
                    title = title, 
                    # description = description, 
                    is_finished=is_finished,
                    latest_event=event,
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
    profile_me = request.user.get_profile()
    profile_queryset = request.user.get_profile().get_following()
    tracklist_queryset = Tracklist.objects.filter(owner__in=profile_queryset)|Tracklist.objects.filter(userto__in=profile_queryset)|profile_me.tracklists_created.all()|profile_me.tracklists_contributed.all()
    tracklist_list = tracklist_queryset.distinct().order_by('-date_latest_edit')[:20]

    context = {
        'tracklist_list':tracklist_list,
    }
    context.update(get_generic_context(request))
    context.update(get_rankings(request))

    return render_to_response('hip_engine/feed.html', context, context_instance=RequestContext(request))

@login_required
def profile(request, username):
    return profile_activity(request, username)

@login_required
def profile_activity(request, username):
    profile_focused = get_object_or_404(UserProfile,user__username=username)
    tracklist_queryset = profile_focused.tracklists_created.all()|profile_focused.tracklists_contributed.all()
    tracklist_list = tracklist_queryset.distinct().order_by('-date_latest_edit')[:20]

    context = {
        'tracklist_list':tracklist_list,
    }
    context.update(get_profile_context(username))
    context.update(get_generic_context(request))
    context.update(get_rankings(request))

    return render_to_response('hip_engine/profile_activity.html', context, context_instance=RequestContext(request))

@login_required
def profile_collection(request, username):
    profile_focused = get_object_or_404(UserProfile,user__username=username)
    tracklist_queryset = profile_focused.tracklist_kept.all()
    tracklist_list = tracklist_queryset.distinct().order_by('-date_latest_edit')

    context = {
        'tracklist_list':tracklist_list,
    }
    context.update(get_profile_context(username))
    context.update(get_generic_context(request))
    context.update(get_rankings(request))

    return render_to_response('hip_engine/profile_collection.html', context, context_instance=RequestContext(request))

@login_required
def profile_pending(request, username):
    profile_focused = get_object_or_404(UserProfile,user__username=username)
    tracklist_queryset = profile_focused.tracklists_created.all()|profile_focused.tracklists_contributed.all()
    tracklist_list = tracklist_queryset.filter(is_finished=False).distinct().order_by('-date_latest_edit')

    context = {
        'tracklist_list':tracklist_list,
    }
    context.update(get_profile_context(username))
    context.update(get_generic_context(request))
    context.update(get_rankings(request))

    return render_to_response('hip_engine/profile_pending.html', context, context_instance=RequestContext(request))

@login_required
def profile_followers(request, username):
    profile_focused = get_object_or_404(UserProfile, user__username=username)
    followers_list = profile_focused.get_followers()
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_latest_edit')[:10]

    context = {
        'tracklist_list':tracklist_list,
        'followers_list':followers_list,
    }
    context.update(get_profile_context(username))
    context.update(get_generic_context(request))
    context.update(get_rankings(request))

    return render_to_response('hip_engine/profile_followers.html', context, context_instance=RequestContext(request))

@login_required
def profile_following(request, username):
    profile_focused = get_object_or_404(UserProfile,user__username=username)
    following_list = profile_focused.get_following()
    tracklist_queryset = Tracklist.objects.filter(owner = request.user.get_profile()).filter(is_finished=False)|Tracklist.objects.filter(userto = request.user.get_profile()).filter(is_finished=False)
    tracklist_list = tracklist_queryset.distinct().order_by('-date_latest_edit')[:10]

    context = {
        'tracklist_list':tracklist_list,
        'following_list':following_list,
    }
    context.update(get_profile_context(username))
    context.update(get_generic_context(request))
    context.update(get_rankings(request))

    return render_to_response('hip_engine/profile_following.html', context, context_instance=RequestContext(request))

@login_required
def profile_edit(request, username):
    if (username == request.user.username):

        email_form = UserEmailForm(instance=request.user)
        email_notif_form = ProfileEmailNotificationForm(instance=request.user.get_profile())
        image_form = ProfileImageForm(instance=request.user.get_profile())
        psw_form = PasswordChangeForm(request.user)

        tracklist_form = TracklistForm(username=request.user.username)

        track_form = TrackForm()

        if request.method == "POST":
            if request.POST['form-type'] == "image-form":
                image_form = ProfileImageForm(request.POST, request.FILES, instance=request.user.get_profile())
                if image_form.is_valid():
                    image_form.save()
                    # resize and save image under same filename
                    im_path = join(MEDIA_ROOT, request.user.get_profile().avatar.name)
                    im = Image.open(im_path)
                    im = rescale_square(im, 256)
                    im.save(im_path, "JPEG")
            elif request.POST['form-type'] == "email-form":
                email_form = UserEmailForm(request.POST, instance=request.user)
                if email_form.is_valid():
                    email_form.save() 
                    return HttpResponseRedirect(reverse('hip_engine.views.profile_edit', args=(request.user.username,)))
            elif request.POST['form-type'] == "email-notif-form":
                email_notif_form = ProfileEmailNotificationForm(request.POST, instance=request.user.get_profile())
                if email_notif_form.is_valid():
                    email_notif_form.save() 
                    return HttpResponseRedirect(reverse('hip_engine.views.profile_edit', args=(request.user.username,)))
            else:
                psw_form = PasswordChangeForm(request.user, request.POST)
                if psw_form.is_valid():
                    psw_form.save()
                    return HttpResponseRedirect(reverse('hip_engine.views.profile_edit', args=(request.user.username,)))

        context = {
            'email_form':email_form, 
            'email_notif_form':email_notif_form,
            'image_form':image_form,
            'psw_form':psw_form,
        }
        context.update(get_profile_context(username))
        context.update(get_generic_context(request))
        context.update(get_rankings(request))

        # tracklist_formset = TracklistFormset(initial=[{'owner': request.user.get_profile(), 'bundlego':bundlego}])

        return render_to_response('hip_engine/profile_edit.html', context, context_instance=RequestContext(request))

    else:
        return HttpResponseRedirect(reverse('hip_engine.views.feed'))

@login_required
def profile_rankings(request, username):
    if (username == request.user.username):
        follows_queryset = request.user.get_profile().get_following()
        profile_list = list(follows_queryset.distinct().order_by('-reputation'))
        for index in range(len(profile_list)):
            if profile_list[index].reputation <= request.user.get_profile().reputation:
                profile_list.insert(index, request.user.get_profile())
                break

        context = {'full_rankings_profile_list':profile_list,}
        context.update(get_generic_context(request))
        context.update(get_rankings(request))

        return render_to_response('hip_engine/profile_rankings.html', context, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('hip_engine.views.feed'))

def get_search_results(query_string):  
    tracklist_query = get_query(query_string, ['title', 'tags__name', 'owner__user__username', 'tracks_initial__artist', 'tracks_initial__name', 'tracks_kept__artist', 'tracks_kept__name'])
    found_tracklists = Tracklist.objects.filter(tracklist_query).distinct().order_by('-date_latest_edit')

    profile_query = get_query(query_string, ['user__username',])
    found_profiles = UserProfile.objects.filter(profile_query).distinct().order_by('user__username')

    return found_tracklists, found_profiles

def get_search_context(request):
    query_string = ''
    found_profiles = None
    found_tracklists = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        found_tracklists, found_profiles = get_search_results(query_string)
    else:
        found_tracklists = Tracklist.objects.all().order_by('-date_latest_edit')
        found_profiles = UserProfile.objects.all().exclude(user__username=request.user.username).order_by('user__username')

    context = {
        'query_string': query_string, 
        'tracklist_list': found_tracklists, 
        'profile_list': found_profiles,
    }
    context.update(get_generic_context(request))
    context.update(get_rankings(request))

    return context
    
@login_required
def search_profiles(request):
    context = get_search_context(request)
    return render_to_response('hip_engine/search_profiles.html', context, context_instance=RequestContext(request))

@login_required
def search_mixtapes(request):
    context = get_search_context(request)
    return render_to_response('hip_engine/search_mixtapes.html', context, context_instance=RequestContext(request))

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
    userto = request.POST.get('tracklist-userto')
    if not userto:
        profile_me = request.user.get_profile()
        profile_queryset = request.user.get_profile().get_following()
        tracklist_queryset = Tracklist.objects.filter(owner__in=profile_queryset)|Tracklist.objects.filter(userto__in=profile_queryset)|profile_me.tracklists_created.all()|profile_me.tracklists_contributed.all()
        tracklist_list = tracklist_queryset.distinct().order_by('-date_latest_edit')[:10]

        context = {
            'tracklist_list':tracklist_list,
            'error_message_userto': "You must select at least one contributor. Click the 'New Mixtape' button to start over.",
        }
        context.update(get_generic_context(request))
        context.update(get_rankings(request))

        return render_to_response('hip_engine/feed.html', context, context_instance=RequestContext(request))

    tracklist_form = TracklistForm(request.POST, prefix='tracklist', username=request.user.username)
    if tracklist_form.is_valid():
        tracklist = tracklist_form.save()
        for i_str in ["_1","_2","_3"]:
                url = request.POST.get('url'+i_str)
                artist = request.POST.get('artist'+i_str)
                name = request.POST.get('name'+i_str)
                if url:
                    validate = URLValidator()
                    try:
                        validate(url)
                        track = Track(url=url)
                        if artist:
                            track.artist = artist
                        if name:
                            track.name = name
                        track.save()
                        tracklist.tracks_initial.add(track)
                    except ValidationError, e:
                        tracklist_queryset = Tracklist.objects.all()
                        tracklist_list = tracklist_queryset.distinct().order_by('-date_latest_edit')[:10]
                        context = {
                            'tracklist_form':tracklist_form,
                            'tracklist_list':tracklist_list,
                            'error_message_url': "Some track urls are invalid, please check them. Click the 'New Mixtape' button to start over.",
                        }
                        context.update(get_nav_context())
                        context.update(get_rankings(request))

                        return render_to_response('hip_engine/feed.html', context, context_instance=RequestContext(request))
    
        title = request.POST.get('title')
        if title:
            tracklist.title = title

        event = Event(main_profile = request.user.get_profile(), event_type = "creation")
        event.save()
        tracklist.latest_event = event
        tracklist.date_latest_edit = timezone.now()

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

    for user_to_mail in tracklist.userto.all():
        if user_to_mail.is_email_notified:
            from django.core.mail import send_mail
            send_mail(generate_header_new_mixtape(tracklist), generate_body_new_mixtape(user_to_mail, tracklist), 'HipMe', [user_to_mail.user.email])

    if request.POST.get('next-success'):
        url_next = request.POST['next-success']
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

    validate = URLValidator()
    try:
        validate(url)
    except ValidationError, e:
        tracklist_queryset = Tracklist.objects.all()
        tracklist_list = tracklist_queryset.distinct().order_by('-date_latest_edit')[:10]
        context = {
            'tracklist_list': tracklist_list,
            'error_message_url': "Your track url is not valid. Please stop trying to break the internet.",
        }
        context.update(get_nav_context())
        context.update(get_rankings(request))

        return render_to_response('hip_engine/feed.html', context, context_instance=RequestContext(request))

    track = Track(url=url)
    if artist:
        track.artist = artist
    if name:
        track.name = name
    track.save()

    if request.user.get_profile() == tracklist.owner:
        tracklist.tracks_initial.add(track)

        event = Event(main_profile=tracklist.owner, event_type="add_track_owner")
        event.save()
        tracklist.latest_event = event
        tracklist.date_latest_edit = timezone.now()
        tracklist.save()

    else:
        if tracklist.bundlebacks.filter(owner=request.user.get_profile()):
            # bundleback = get_object_or_404(Bundle, owner=request.user.get_profile())
            bundleback = tracklist.bundlebacks.filter(owner=request.user.get_profile())[:1].get()
            bundleback.save()
        else:
            bundleback = Bundle(owner=request.user.get_profile())
            bundleback.save()
            tracklist.userto.add(request.user.get_profile())
            tracklist.save()

        bundleback.tracks.add(track)
        bundleback.save()

        tracklist.bundlebacks.add(bundleback)

        event = Event(main_profile=bundleback.owner, secondary_profile=tracklist.owner, event_type="add_track_contrib")
        event.save()
        tracklist.latest_event = event
        tracklist.date_latest_edit = timezone.now()
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

    if track not in tracklist.tracks_kept.all():
        bundleback.tracks_kept.add(track)
        tracklist.tracks_kept.add(track)

        event = Event(main_profile = tracklist.owner, secondary_profile=bundleback.owner, event_type = "keep_track")
        event.save()
        tracklist.latest_event = event

        tracklist.date_latest_edit = timezone.now()

        bundleback.owner.reputation += 10

        bundleback.nb_tracks_kept += 1

    else:
        bundleback.tracks_kept.remove(track)
        tracklist.tracks_kept.remove(track)
        tracklist.date_latest_edit = timezone.now()

        bundleback.owner.reputation -= 10
        
        bundleback.nb_tracks_kept -= 1

    tracklist.save()
    bundleback.owner.save()
    bundleback.save()

    if request.POST.get('next'):
        url_next = request.POST['next']
        return HttpResponseRedirect(url_next)
    else:
        return HttpResponseRedirect(reverse('hip_engine.views.feed'))

@login_required
def like_mixtape(request, tracklist_id):
    tracklist = get_object_or_404(Tracklist, pk=tracklist_id)

    if request.POST.get('like'):
        tracklist.owner.reputation += 3
        tracklist.likes += 1
        request.user.get_profile().tracklist_kept.add(tracklist)

    if request.POST.get('unlike'):
        tracklist.owner.reputation -= 3
        tracklist.likes -= 1
        request.user.get_profile().tracklist_kept.remove(tracklist)

    tracklist.owner.save()
    tracklist.save()
    request.user.get_profile().save()

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
        tracklist.date_latest_edit = timezone.now()

        event = Event(main_profile = request.user.get_profile(), event_type = "closing")
        event.save()
        tracklist.latest_event = event

        tracklist.save()

    if request.POST.get('next'):
        url_next = request.POST['next']
        return HttpResponseRedirect(url_next)
    else:
        return HttpResponseRedirect(reverse('hip_engine.views.feed'))

@login_required
def profile_follow(request, username):
    profile_focused = get_object_or_404(UserProfile, user__username=username)

    if profile_focused not in request.user.get_profile().get_following():
        request.user.get_profile().add_following(profile_focused)
    else:
        request.user.get_profile().remove_following(profile_focused) 
    
    request.user.get_profile().save()

    if request.POST.get('next'):
        url_next = request.POST['next']
        return HttpResponseRedirect(url_next)
    else:
        return HttpResponseRedirect(reverse('hip_engine.views.feed'))

@login_required
def give_feedback(request):
    if request.method == "POST":
        if request.POST['body']:

            if request.POST['kind']:
                kind = request.POST['kind']
            else:
                kind = ""

            sugg = Suggestion(userfrom = request.user.get_profile(), body = request.POST['body'], kind = kind, submit_date = timezone.now())
            sugg.save()

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
            request.user.get_profile().nb_connects += 1
            request.user.get_profile().save()
            if not request.user.get_profile().get_following():
                return HttpResponseRedirect(reverse('hip_engine.views.suggest_profiles'))
            elif request.GET.get('next',''):
                url = request.GET.get('next','')
                return HttpResponseRedirect(url)
            else:
                return HttpResponseRedirect(reverse('hip_engine.views.feed'))
        else:
            return render_to_response('hip_engine/landing_page.html', {'error_message_login': "Sorry, your account has been disabled.",}, context_instance=RequestContext(request)) 
    else:
        return render_to_response('hip_engine/landing_page.html', {'error_message_login': "Your username and password do not match. Please try again.",}, context_instance=RequestContext(request))  

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
            if 'email_2' in field_key:
                context.update({'error_message_email_2': "You must fill in all of the fields.",})
            elif 'email_1' in field_key:
                context.update({'error_message_email_1': "You must fill in all of the fields.",})
            elif 'password' in field_key:
                context.update({'error_message_password': "You must fill in all of the fields.",})
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
                            messages.info(request, 'Welcome to hipMe, the social game for music discovery.', extra_tags='welcome_message_line1')
                            messages.info(request, 'Create mixtapes and ask your friends to contribute with great music...', extra_tags='welcome_message_line2')
                            messages.info(request, 'Or contribute to your friends\' mixtapes, you\'ll get points if they keep your tracks!', extra_tags='welcome_message_line2')
                            messages.info(request, 'First, follow a few of the people below. Then check out your stream and start playing!')
                            return HttpResponseRedirect(reverse('hip_engine.views.suggest_profiles'))
                        else:
                            context.update({'error_message_email_1': "Your email is not valid. Please try again.",})
                            return render_to_response('hip_engine/landing_page.html', context, context_instance=RequestContext(request))
                    else:
                        context.update({'error_message_email_1': "Email already exists. Please choose another one.",})
                        return render_to_response('hip_engine/landing_page.html', context, context_instance=RequestContext(request)) 
                else:
                    context.update({'error_message_email_2': "Your emails do not match. Please try again.",})
                    return render_to_response('hip_engine/landing_page.html', context, context_instance=RequestContext(request))
            else:
                context.update({'error_message_username': "Username already exists. Please choose another one.",})
                return render_to_response('hip_engine/landing_page.html', context, context_instance=RequestContext(request))
        else:
            context.update({'error_message_username': "Username is not valid. Please use only letters, numbers, '-' and '_'.",})
            return render_to_response('hip_engine/landing_page.html', context, context_instance=RequestContext(request))
    else:
        return render_to_response('hip_engine/landing_page.html', context, context_instance=RequestContext(request))