from django.forms import DateTimeInput, ModelForm

from .models import Club, ClubMeeting


class ClubForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        query = self.fields['members'].queryset
        self.fields['members'].queryset = query.order_by('first_name', 'last_name')

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
