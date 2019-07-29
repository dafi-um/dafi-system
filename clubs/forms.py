from django.forms import DateTimeInput, ModelForm

from .models import ClubMeeting


class ClubMeetingForm(ModelForm):
    class Meta:
        model = ClubMeeting
        exclude = ['club']
        help_texts = {
            'moment': ('Formato: DD/MM/YYYY HH:mm'),
        }
