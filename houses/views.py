from random import shuffle
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.db import transaction
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

from users.utils import AuthenticatedRequest

from .models import (
    House,
    HouseProfile,
    SelectorQuestion,
    SelectorResult,
    SelectorResultPoints,
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

        if SelectorResult.objects.filter(user=self.request.user).exists():
            return redirect('houses:selector_done')

        if HouseProfile.objects.filter(user=self.request.user).exists():
            return redirect('houses:profile')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        questions = list(
            SelectorQuestion
            .objects
            .filter(options__points__isnull=False)
            .prefetch_related('options')
            .distinct()
        )

        shuffle(questions)

        context = super().get_context_data(**kwargs)
        context['questions'] = questions[:30]
        return context

    def post(self, request: AuthenticatedRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        questions_queryset = (
            SelectorQuestion
            .objects
            .filter(options__points__isnull=False)
            .prefetch_related('options__points')
            .distinct()
        )

        houses = House.objects.all()
        questions = {q.id: q for q in questions_queryset}

        points = {house: 0 for house in houses}

        count = 0

        for key, value in request.POST.items():
            if not key.startswith('q-'):
                continue

            try:
                question = questions[int(key.removeprefix('q-'))]
                option = next(o for o in question.options.all() if o.id == int(value))
            except (ValueError, KeyError, StopIteration):
                messages.error(request, 'No se pudo analizar la respuesta enviada')
                return redirect('houses:selector')

            for opt_points in option.points.all():
                points[opt_points.house] += opt_points.points

            count += 1

        if count != len(questions):
            messages.error(request, 'No se pudo analizar la respuesta enviada')
            return redirect('houses:selector')

        with transaction.atomic():
            try:
                result = (
                    SelectorResult
                    .objects
                    .filter(user=request.user)
                    .select_for_update()
                    .get()
                )

                result.points.delete()
            except SelectorResult.DoesNotExist:
                result = SelectorResult.objects.create(user=request.user)

            for house, points_num in points.items():
                if points_num != 0:
                    SelectorResultPoints.objects.create(
                        result=result,
                        house=house,
                        points=points_num,
                    )

        return redirect('houses:selector_done')


class SelectorAlgorithmDoneView(MetadataMixin, TemplateView):

    template_name = 'houses/selector_algorithm_done.html'

    title = 'Algoritmo Seleccionador - Las Casas de la FIUM'
    description = META_DESCRIPTION
    image = META_IMAGE
