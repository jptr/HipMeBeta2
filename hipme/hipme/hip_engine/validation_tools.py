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