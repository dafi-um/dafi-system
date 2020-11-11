import datetime

from django.views.generic import TemplateView

from meta.views import MetadataMixin

from .common import EventMixin

def datetime_to_pos(date):
    m = date.hour * 60 + date.minute

    return m * 100 / 1440


class IndexView(EventMixin, MetadataMixin, TemplateView):
    '''Index event view'''

    template_name = 'sanalberto/index.html'

    def get_context_data(self, **kwargs):
        event = self.get_current_event()

        activities = event.activities.filter(is_public=True).order_by('start')
        polls = event.polls.all()

        days = {}

        for activity in activities:
            start = activity.start
            end = activity.end

            start_key = start.date().toordinal()
            end_key = end.date().toordinal()

            start_pos = datetime_to_pos(start)
            end_pos = datetime_to_pos(end)

            if start_key not in days:
                days[start_key] = []

            if start_key == end_key:
                days[start_key].append({
                    'obj': activity,
                    'top': str(start_pos),
                    'height': str(end_pos - start_pos),
                })

                continue

            days[start_key].append({
                'obj': activity,
                'top': str(start_pos),
                'height': str(100.0 - start_pos),
                'classes': 'day-extend-to'
            })

            if end_key not in days:
                days[end_key] = []

            days[end_key].append({
                'obj': activity,
                'top': '0',
                'height': str(end_pos),
                'classes': 'day-extend-from'
            })

            d = start + datetime.timedelta(days=1)

            while d < end:
                key = d.date().toordinal()

                if key not in days:
                    days[key] = []

                days[key].append({
                    'obj': activity,
                    'top': '0',
                    'height': '100',
                    'classes': 'day-extend-from day-extend-to'
                })

                d += datetime.timedelta(days=1)

        days = [(value, datetime.date.fromordinal(key)) for key, value in days.items()]

        context = super().get_context_data(**kwargs)
        context['days'] = days
        context['polls'] = polls
        return context


class InfoView(MetadataMixin, TemplateView):
    '''Information view'''

    title = 'San Alberto - DAFI'
    description = 'San Alberto: Fiestas patronales de la Facultad de Informática'
    image = 'images/favicon.png'

    template_name = 'sanalberto/info.html'
