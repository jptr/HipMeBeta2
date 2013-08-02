from settings import MEDIA_ROOT
from os.path import join
from hip_engine.models import User, Tracklist
from django.shortcuts import render_to_response

def generate_header_new_mixtape(tracklist):
    return "[hipMe] " + tracklist.owner.user.username +" asked you to contribute to a mixtape!"

def generate_body_new_mixtape(user_to_mail, tracklist):
    str1 = "Hey "+ user_to_mail.user.username + ","
    mixtape_url = 'http://hipme.fm/profile/'+user_to_mail.user.username+'/pending/'
    str2 = tracklist.owner.user.username + " created a new mixtape called" + tracklist.title + ", and he asked you to contribute! Go check it out: " + mixtape_url
    str3 = "Add tracks to that mixtape. If "+ tracklist.owner.user.username + "keeps your tracks in his mixtape, you'll get points and get higher in the rankings..."
    str4 = "Keep da hip,"
    str5 = "The HipMasters."
    edit_url = 'http://hipme.fm/profile/'+user_to_mail.user.username+'/edit/'
    str6 = "Don't forget that you can always go to the settings page to edit your account data and your notification preferences: " + edit_url
    return str1 + "\n\n" + str2 + "\n" + str3 + "\n\n" + str4 +"\n"+ str5 + "\n\n" + str6

# def generate_header_bundleback(swap):
#     return "[HipMe] " + swap.userto.user.username +" has just sent you a bundle back!"

# def generate_body_bundleback(swap):
#     str1 = "Hey "+ swap.userfrom.user.username + ","
#     str2 = swap.userto.user.username+ " has just replied to your bundle !"
#     swap_url = 'http://hipme.co/people/'+swap.userfrom.user.username+'/pending/'
#     str3 = "Listen to it and rate it: " + swap_url
#     str4 = "Keep da hip,"
#     str5 = "The HipMasters."
#     edit_url = 'http://hipme.co/people/'+swap.userfrom.user.username+'/edit/'
#     str6 = "Don't forget that you can always go to the settings page to edit your account data and your notification preferences: " + edit_url
#     return str1 + "\n\n" + str2 + "\n\n" + str3 + "\n\n" + str4 +"\n"+ str5 + "\n\n" + str6
 
# def bunch_create_tracks():
#     """Feed the database with tracks from the .txt"""
#     file_path = join(MEDIA_ROOT, 'setup/track_db.txt')
#     with open(file_path, 'r') as f:
#         for line in f:
#             line_data = line.split("_")
#             artist = line_data[0]
#             name = line_data[1]
#             url = line_data[2]
#             sg = Song(url=url, artist=artist, name=name)
#             sg.save()