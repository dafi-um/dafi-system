from django.db.models import QuerySet
from django.views.generic import (
    ListView,
)

from meta.views import MetadataMixin

from .models import (
    House,
)


META_DESCRIPTION = 'Las Casas de Estudiantes de la Facultad de Informática de la UM'
META_IMAGE = 'images/favicon.png'


class HousesListView(MetadataMixin, ListView):

    model = House

    title = 'Las Casas de la FIUM'
    description = META_DESCRIPTION
    image = META_IMAGE

    def get_queryset(self) -> QuerySet[House]:
        queryset = super().get_queryset().order_by('name')

        # No need to prefetch if we're not going to use it
        if self.request.user.is_authenticated:
            queryset = queryset.prefetch_related('managers')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        houses: list[House] = context['object_list']
        best_house: House = max(houses, key=lambda h: h.points)

        # Only show the best house if it's really the best one
        if not any(house != best_house and house.points == best_house.points for house in houses):
            context['best_house'] = best_house

        return context
