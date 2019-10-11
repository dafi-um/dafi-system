from django.forms import DateTimeInput, ModelForm

from .models import Club, ClubMeeting


class ClubForm(ModelForm):
    class Meta:
        model = Club
        fields = ('description', 'members')


class ClubMeetingForm(ModelForm):
    class Meta:
        model = ClubMeeting
        exclude = ['club']
        help_texts = {
            'moment': ('Formato: DD/MM/YYYY HH:mm'),
        }
