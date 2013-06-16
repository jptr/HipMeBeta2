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
    regex_tag = '^[a-zA-Z0-9\-_ ]+$'
    array_tags = string_tags.split(',')
    tags = []

    for tag in array_tags:
        if re.search(regex_tag, tag):
            tag = tag.title()
            tag = " ".join(tag.split())
            tags.append(tag)

    return tags