from typing import Any

from django.contrib.auth.mixins import AccessMixin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponseBase
from django.shortcuts import redirect
from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
)

from meta.views import MetadataMixin

from .models import (
    House,
    HouseProfile,
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

        if self.request.user.is_authenticated:
            context['profile'] = HouseProfile.objects.filter(user=self.request.user).first()

        return context


class HouseProfileDetailView(MetadataMixin, DetailView):

    model = HouseProfile

    context_object_name = 'profile'

    description = META_DESCRIPTION
    image = META_IMAGE

    def get_queryset(self) -> 'QuerySet[HouseProfile]':
        return super().get_queryset().prefetch_related('user', 'house')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['my_profile'] = context['profile'].user == self.request.user

        return context

    def get_meta_title(self, context: dict[str, Any]):
        return f'Perfil de {context["profile"].display_name} - Las Casas de la FIUM'


class SelectorAlgorithmView(AccessMixin, MetadataMixin, TemplateView):

    template_name = 'houses/selector_algorithm.html'

    title = 'Algoritmo Seleccionador - Las Casas de la FIUM'
    description = META_DESCRIPTION
    image = META_IMAGE

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()

        if HouseProfile.objects.filter(user=self.request.user).exists():
            return redirect('houses:profile')

        return super().dispatch(request, *args, **kwargs)
