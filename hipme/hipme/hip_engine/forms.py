from django.forms import ModelForm, HiddenInput, Widget
from hip_engine.models import UserProfile, User, Track, Tracklist, Bundle

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
        fields = ('owner', 'userto', )
        widgets = {
            'owner': HiddenInput(),
        }
    def __init__(self,*args, **kwargs):
        username = kwargs.pop('username', '')
        super(TracklistForm, self).__init__(*args, **kwargs)
        self.fields['userto'].choices = UserProfile.objects.exclude(user__username=username).values_list('id','user__username')

class TrackForm(ModelForm):
    class Meta:
        model = Track
        fields = ('url','artist','name')