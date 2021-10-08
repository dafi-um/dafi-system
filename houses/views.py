from django.db.models import QuerySet
from django.views.generic import ListView

from meta.views import MetadataMixin

from .models import House


class HousesListView(MetadataMixin, ListView):

    model = House

    title = 'Las Casas de la FIUM'
    description = 'Las Casas de Estudiantes de la Facultad de Informática de la UM'
    image = 'images/favicon.png'

    def get_queryset(self) -> QuerySet[House]:
        queryset = super().get_queryset()

        # Don't prefetch if we're not going to use it
        if self.request.user.is_authenticated:
            queryset = queryset.prefetch_related('managers')

        return queryset
