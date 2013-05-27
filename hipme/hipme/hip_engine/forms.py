from django.forms import ModelForm
from hip_engine.models import UserProfile, User, Track, Tracklist, Bundle

# from chosen import forms as chosenforms

class ChosenModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ChosenModelForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if self.fields[field].__class__.__name__ in ['ChoiceField', 'TypedChoiceField', 'MultipleChoiceField']:
                choices = self.fields[field].choices
                self.fields[field] = chosenforms.ChosenChoiceField(choices=choices)
            elif self.fields[field].__class__.__name__ in ['ModelChoiceField', 'ModelMultipleChoiceField']:
                queryset = self.fields[field].queryset
                self.fields[field] = chosenforms.ChosenModelChoiceField(queryset=queryset)

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
        fields = ('userto', 'title','description')
    def __init__(self,*args, **kwargs):
        username = kwargs.pop('username', '')
        super(TracklistForm, self).__init__(*args, **kwargs)
        self.fields['userto'].choices = UserProfile.objects.filter(user__username__startswith="hip").values_list('id','user__username')

class TrackForm(ModelForm):
    class Meta:
        model = Track
        fields = ('url','artist','name')