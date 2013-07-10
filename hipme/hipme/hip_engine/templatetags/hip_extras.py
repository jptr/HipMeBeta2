from django import template
from hip_engine.models import Track, Bundle, Tracklist
from django.utils import timezone

register = template.Library()

@register.filter()
def field_type(field):
    return field.field.__class__.__name__

@register.filter()
def urlize_string(query_string):
    words = query_string.split()
    return "+".join(words)

@register.filter()
def free_spots(tracklist):
    nb_spots = 5 - tracklist.bundlebacks.all().count()
    return nb_spots

@register.filter()
def has_tracks(tracklist):
    if tracklist.tracks_initial.all():
        return True
    for bundle in tracklist.bundlebacks.all():
        if bundle.tracks.all():
            return True
    return False

@register.filter()
def featuring_string(tracklist):
    track_list = []
    for track in tracklist.tracks_initial.all():
        if track.artist:
            track_list.append(track.artist.title())
    for bundle in tracklist.bundlebacks.all():
        for track in bundle.tracks.all():
            if track.artist:
                track_list.append(track.artist.title())
    
    if track_list:
        track_list = remove_duplicate(track_list)
        track_list = track_list[:3]

        featuring_string = ", ".join(track_list) + "..."

        return featuring_string

    return ""

def remove_duplicate(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

@register.filter()
def delta_string(timeDiff):
    days = timeDiff.days 
    hours = timeDiff.seconds/3600
    minutes = timeDiff.seconds%3600/60
    seconds = timeDiff.seconds%3600%60
    str = ""
    tStr = ""
    if days > 0:
        if days == 1:   tStr = "day"
        else:           tStr = "days"
        str = str + "%s %s" %(days, tStr)
        return str
    elif hours > 0:
        if hours == 1:  tStr = "hour"
        else:           tStr = "hours"
        str = str + "%s %s" %(hours, tStr)
        return str
    elif minutes > 0:
        if minutes == 1:tStr = "min"
        else:           tStr = "mins"           
        str = str + "%s %s" %(minutes, tStr)
        return str
    elif seconds > 0:
        if seconds == 1:tStr = "sec"
        else:           tStr = "secs"
        str = str + "%s %s" %(seconds, tStr)
        return str
    else:
        return "1 sec"

@register.filter()
def js_tracklist(tracklist):
    js_list = []
    for track in tracklist.tracks_initial.all():
        js_list.append("['" + track.site_from + "','" + track.stream_id + "']")
    for bundle in tracklist.bundlebacks.all():
        for track in bundle.tracks.all():
            js_list.append("['" + track.site_from + "','" + track.stream_id + "']")
    
    if js_list:
        return "[0,"+",".join(js_list)+"]"

    return ''

@register.filter()
def js_track(tracklist, current_track_id):
    js_list = []
    track_counter = 0
    index_current_track = 0

    for track in tracklist.tracks_initial.all():
        js_list.append("['" + track.site_from + "','" + track.stream_id + "']")
        if track.id == current_track_id:
            index_current_track = track_counter
        track_counter += 1
    
    for bundle in tracklist.bundlebacks.all():
        for track in bundle.tracks.all():
            js_list.append("['" + track.site_from + "','" + track.stream_id + "']")
            if track.id == current_track_id:
                index_current_track = track_counter
            track_counter += 1
    
    if js_list:
        return "["+str(index_current_track)+","+",".join(js_list)+"]"

    return ''