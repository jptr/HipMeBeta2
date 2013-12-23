from django.forms import ModelForm, HiddenInput, Widget
from hip_engine.models import UserProfile, User, Track, Tracklist, Bundle, Event
from django.shortcuts import get_object_or_404

class ProfileImageForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('avatar',)

class UserUsernameForm(ModelForm):
    class Meta:
        model = User
        fields = ('username',)

class UserEmailForm(ModelForm):
    class Meta:
        model = User
        fields = ('email',)

class ProfileEmailNotificationForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('is_email_notified',)

class UserRegistrationForm(ModelForm):
    class Meta:
        model = User
        fields = ('username','email','password',)

class TracklistForm(ModelForm):
    class Meta:
        model = Tracklist
        fields = ('owner', 'userto', 'latest_event')
        widgets = {
            'owner': HiddenInput(),
            'latest_event': HiddenInput(),
        }
    def __init__(self,*args, **kwargs):
        username = kwargs.pop('username', '')
        super(TracklistForm, self).__init__(*args, **kwargs)
        user_focused = get_object_or_404(UserProfile, user__username=username)
        profiles_queryset = user_focused.get_following()
        self.fields['userto'].choices = profiles_queryset.values_list('id','user__username')
        # self.fields['userto'].choices = UserProfile.objects.exclude(user__username=username).values_list('id','user__username')

class TrackForm(ModelForm):
    class Meta:
        model = Track
        fields = ('url','artist','name')