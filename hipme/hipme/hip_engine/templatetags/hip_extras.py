from django import template
from hip_engine.models import Track, Bundle, Tracklist
from django.utils import timezone

register = template.Library()

@register.filter()
def field_type(field):
    return field.field.__class__.__name__

@register.filter()
def free_spots(tracklist):
    nb_spots = 5 - tracklist.bundlebacks.all().count()
    return nb_spots

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