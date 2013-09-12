from settings import MEDIA_ROOT
from os.path import join
from hip_engine.models import User, Tracklist
from django.shortcuts import render_to_response

def generate_header_new_mixtape(tracklist):
    return "[hipMe] " + tracklist.owner.user.username +" asked you to contribute to a mixtape!"

def generate_body_new_mixtape(user_to_mail, tracklist):
    str1 = "Hey "+ user_to_mail.user.username + ","
    mixtape_url = 'http://hipme.fm/profile/'+user_to_mail.user.username+'/pending/'
    str2 = tracklist.owner.user.username + " created a new mixtape called " + tracklist.title + ", and he/she asked you to contribute! Go check it out: " + mixtape_url
    str3 = "Add tracks to that mixtape. If "+ tracklist.owner.user.username + " keeps your tracks in his mixtape, you'll get points and get higher in the rankings..."
    str4 = "Keep da hip,"
    str5 = "The HipMasters."
    edit_url = 'http://hipme.fm/profile/'+user_to_mail.user.username+'/edit/'
    str6 = "Don't forget that you can always go to the settings page to edit your account data and your notification preferences: " + edit_url
    return str1 + "\n\n" + str2 + "\n\n" + str3 + "\n\n" + str4 +"\n"+ str5 + "\n\n" + str6

def generate_header_mixtape_to_close(tracklist):
    return "[HipMe] Time is up for your mixtape " + tracklist.title + "."

def generate_body_mixtape_to_close(user_to_mail, tracklist):
    str1 = "Hey "+ user_to_mail.user.username + ","
    mixtape_url = 'http://hipme.fm/profile/'+ user_to_mail.user.username +'/pending/'
    str2 = "Time is up for your mixtape " + tracklist.title + ". Go check it out: " + mixtape_url
    str3 = "Pick the tracks you want to keep in that mixtape, then don't forget to close it! Contributors get points when you keep one of their tracks."
    str4 = "Keep da hip,"
    str5 = "The HipMasters."
    edit_url = 'http://hipme.fm/profile/'+user_to_mail.user.username+'/edit/'
    str6 = "Don't forget that you can always go to the settings page to edit your account data and your notification preferences: " + edit_url
    return str1 + "\n\n" + str2 + "\n\n" + str3 + "\n\n" + str4 +"\n"+ str5 + "\n\n" + str6