from settings import MEDIA_ROOT
from os.path import join
from hip_engine.models import User, Tracklist
from django.shortcuts import render_to_response

def generate_header_new_mixtape(tracklist):
    return "[hipme] " + tracklist.owner.user.username +" asked you to contribute to a mixtape!"

def generate_body_new_mixtape(profile_to_mail, tracklist):
    str1 = "Hey "+ profile_to_mail.user.username + ","
    mixtape_url = 'http://hipme.fm/profile/'+profile_to_mail.user.username+'/pending/'
    if tracklist.title:
        str2 = tracklist.owner.user.username + " created a new mixtape called " + tracklist.title + ", and he/she asked you to contribute! Go check it out: " + mixtape_url
    else:
        str2 = tracklist.owner.user.username + " created a new mixtape, and he/she asked you to contribute! Go check it out: " + mixtape_url
    str3 = "Add tracks to this mixtape. For every track "+ tracklist.owner.user.username + " keeps in his/her mixtape, you get points!"
    str4 = "Keep da hip,"
    str5 = "The hipmasters."
    edit_url = 'http://hipme.fm/profile/'+profile_to_mail.user.username+'/edit/'
    str6 = "Don't forget that you can always go to the settings page to edit your account data and your notification preferences: " + edit_url
    return str1 + "\n\n" + str2 + "\n\n" + str3 + "\n\n" + str4 +"\n"+ str5 + "\n\n" + str6

def generate_header_new_follower(user_following, user_to_mail, follow_back):
    if follow_back:
        return "[hipme] " + user_following.username +" is now following you back!"
    return "[hipme] " + user_following.username +" is now following you!"

def generate_body_new_follower(user_following, user_to_mail, follow_back):
    str1 = "Hey "+ user_to_mail.username + ","
    follower_url = 'http://hipme.fm/profile/'+user_following.username
    follow_back_str = "back " if follow_back else ""
    str2 = user_following.username + " is now following you "+follow_back_str+"on hipme."
    str3 = "Check out his profile: " + follower_url
    str4 = "Keep da hip,"
    str5 = "The hipmasters."
    edit_url = 'http://hipme.fm/profile/'+user_to_mail.username+'/edit/'
    str6 = "Don't forget that you can always go to the settings page to edit your account data and your notification preferences: " + edit_url
    return str1 + "\n\n" + str2 + "\n\n" + str3 + "\n\n" + str4 +"\n"+ str5 + "\n\n" + str6

def generate_header_mixtape_to_close(tracklist):
    if tracklist.title:
        return "[hipme] Time is up for your mixtape '" + tracklist.title + "'."
    else:
        return "[hipme] Time is up for one of your mixtapes"

def generate_body_mixtape_to_close(user_to_mail, tracklist):
    str1 = "Hey "+ user_to_mail.user.username + ","
    mixtape_url = 'http://hipme.fm/profile/'+ user_to_mail.user.username +'/pending/'
    if tracklist.title:
        str2 = "Time is up for your mixtape " + tracklist.title + ". Go check it out: " + mixtape_url
    else:
        str2 = "Time is up for one of your mixtapes. Go check it out: " + mixtape_url
    str3 = "Pick the tracks you want to keep in this mixtape, then don't forget to close it! Contributors get points when you keep one of their tracks."
    str4 = "Keep da hip,"
    str5 = "The hipmasters."
    edit_url = 'http://hipme.fm/profile/'+ user_to_mail.user.username +'/edit/'
    str6 = "Don't forget that you can always go to the settings page to edit your account data and your notification preferences: " + edit_url
    return str1 + "\n\n" + str2 + "\n\n" + str3 + "\n\n" + str4 +"\n"+ str5 + "\n\n" + str6

def generate_header_contribute(tracklist):
    return "[hipme] 2 days left to contribute to " + tracklist.owner.user.username + "'s mixtape!"

def generate_body_contribute(user_to_mail, tracklist):
    str1 = "Hey "+ user_to_mail.user.username + ","
    mixtape_url = 'http://hipme.fm/profile/'+ user_to_mail.user.username +'/pending/'
    if tracklist.title:
        str2 = "Only 48 hours left to contribute to " + tracklist.owner.user.username + "'s mixtape called " + tracklist.title + "! Go check it out: " + mixtape_url
    else:
        str2 = "Only 48 hours left to contribute to " + tracklist.owner.user.username + "'s mixtape! Go check it out: " + mixtape_url
    str3 = "Add tracks to this mixtape. For every track "+ tracklist.owner.user.username + " keeps in his/her mixtape, you get points!"
    str4 = "Keep da hip,"
    str5 = "The hipmasters."
    edit_url = 'http://hipme.fm/profile/'+user_to_mail.user.username+'/edit/'
    str6 = "Don't forget that you can always go to the settings page to edit your account data and your notification preferences: " + edit_url
    return str1 + "\n\n" + str2 + "\n\n" + str3 + "\n\n" + str4 +"\n"+ str5 + "\n\n" + str6

def generate_header_come_back():
    return "[hipme] We haven't seen you in a while!"

def generate_body_come_back(user_to_mail):
    str1 = "Hey "+ user_to_mail.user.username + ", long time no see!"
    feed_url = 'http://hipme.fm/'
    str2 = "Have you stopped looking for great music? Your friends haven't. Find out what's been happening on hipme.fm while you weren't there: " + feed_url
    str3 = "Go create new mixtapes and ask your friends to put great music in them. Or just improve your ranking by contributing to their mixtapes! The more tracks they keep, the more points you get."
    str4 = "Keep da hip,"
    str5 = "The hipmasters."
    edit_url = 'http://hipme.fm/profile/'+user_to_mail.user.username+'/edit/'
    str6 = "Don't forget that you can always go to the settings page to edit your account data and your notification preferences: " + edit_url
    return str1 + "\n\n" + str2 + "\n\n" + str3 + "\n\n" + str4 +"\n"+ str5 + "\n\n" + str6

def generate_header_signup(user):
    return "[hipme] Hey " + user.username + ", welcome to hipme.fm!"

def generate_body_signup(user):
    str1 = "Hey "+ user.username + ", welcome aboard!"
    feed_url = 'http://hipme.fm/'
    str2 = "Great music is just one click away:  " + feed_url
    str3 = "hipme is where you and your friends discover music together. Put tracks into each other's mixtapes, and try to be the best music advisor!"
    fb_url = 'https://www.facebook.com/hipmemusic'
    str7 = "We need your advice to improve hipme. Use the feedback button, or ping us at hipmail.me@gmail.com or on Facebook: " + fb_url
    str4 = "Keep da hip,"
    str5 = "The hipmasters."
    edit_url = 'http://hipme.fm/profile/'+user.username+'/edit/'
    str6 = "Don't forget that you can always go to the settings page to edit your account data and your notification preferences: " + edit_url
    return str1 + "\n\n" + str2 + "\n\n" + str3 + "\n\n" + str7 + "\n\n" + str4 +"\n"+ str5 + "\n\n" + str6

def generate_header_welcome():
    return "[hipme] We are ready. Are you?"

def generate_body_welcome():
    str1 = "Hi all,"
    str2 = "The moment you've all been waiting for has finally arrived: our brand-new beta version is out!"
    feed_url = 'http://hipme.fm/'
    str3 = "hipme is where your friends make you discover music, while you try to be the best music advisor. Go check it out: " + feed_url
    fb_url = 'https://www.facebook.com/hipmemusic'
    str4 = "Keep in mind that this is a beta version. It's far from perfect, but you can help us make it better. Give us as much feedback as possible through the big button on hipme.fm, or drop us a line at hipmail.me@gmail.com or on Facebook: "+ fb_url
    str5 = "Keep da hip,"
    str6 = "The hipmasters."

    return str1 + "\n\n" + str2 + "\n\n" + str3 + "\n\n" + str4 + "\n\n" + str5 +"\n"+ str6
