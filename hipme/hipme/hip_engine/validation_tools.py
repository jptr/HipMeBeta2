#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import re

def validateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def validateUsername(username):
    regex_username = '^[a-zA-Z0-9\-_]+$'

    if re.search(regex_username, username):
        return True
    else:
        return False

def parseTags(string_tags):
    regex_tag = '^[a-zA-ZÀ-ÿ0-9\-_ ]+$'
    array_tags = string_tags.split(',')
    tags = []

    for tag in array_tags:
        if re.search(regex_tag, tag):
            tag = tag.lower()
            tag = tag.title()
            tag = " ".join(tag.split())
            tags.append(tag)

    return tags

def get_streaming_site_from(url):
    regex_youtube = '^(https?:\/\/)?(?:www\.)?youtube.com\/watch\?(?=.*v=[a-zA-Z0-9\-\_]+)v=\S+$'
    regex_youtube_short = '^(https?:\/\/)?(?:www\.)?youtu.be\/[a-zA-Z0-9\-\_]+$'
    regex_soundcloud = '^(https?:\/\/)?(?:www\.)?soundcloud.com\/[a-zA-Z0-9\-]+\/[a-zA-Z0-9\-]+(\/)?$'
    regex_grooveshark = '^(https?:\/\/)?(?:www\.)?grooveshark.com\/(#!\/)?s\/[a-zA-Z0-9\+]+\/\S+?$'
    regex_hypem = '^(https?:\/\/)?(?:www\.)?hypem.com\/track\/\S+?$'

    if re.search(regex_youtube, url) or re.search(regex_youtube_short, url):
        return 'youtube'
    elif re.search(regex_soundcloud, url):
        return 'soundcloud'
    elif re.search(regex_grooveshark, url):
        return 'grooveshark'
    elif re.search(regex_hypem, url):
        return 'hypem'
    else:
        return 'unknown'

def get_stream_id(url, site_from):
    regex_youtube = '^(https?:\/\/)?(?:www\.)?youtube.com\/watch\?(?=.*v=[a-zA-Z0-9\-\_]+)v=(?P<id>\S+)$'
    regex_youtube_short = '^(https?:\/\/)?(?:www\.)?youtu.be\/?(?=.*[a-zA-Z0-9\-\_]+)(?P<id>\S+)$'
    regex_soundcloud = '^(https?:\/\/)?(?:www\.)?soundcloud.com\/[a-zA-Z0-9\-]+\/[a-zA-Z0-9\-]+(\/)?$'
    regex_grooveshark = '^(https?:\/\/)?(?:www\.)?grooveshark.com\/(#!\/)?s\/[a-zA-Z0-9\+]+\/\S+?$'
    regex_hypem = '^(https?:\/\/)?(?:www\.)?hypem.com\/track\/\S+?$'
        
    if site_from == 'youtube':
        if re.search(regex_youtube, url):
            m = re.search(regex_youtube, url)
        else:
            m = re.search(regex_youtube_short, url)
        return m.group('id')
    elif site_from == 'soundcloud':
        return url
    else:
        return ''