from datetime import timedelta
from typing import (
    Any,
    cast,
)

from django.contrib import messages
from django.contrib.auth.mixins import (
    AccessMixin,
    LoginRequiredMixin,
)
from django.db import transaction
from django.db.models import QuerySet
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.http.response import HttpResponseBase
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import (
    DetailView,
    TemplateView,
)
from django.views.generic.base import View
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from meta.views import MetadataMixin
from stripe.api_resources import PaymentIntent
from stripe.api_resources.checkout.session import Session
from stripe.error import StripeError

from users.utils import AuthenticatedRequest

from ..models import (
    Activity,
    ActivityRegistration,
)
from ..payments import (
    create_registration_checkout,
    is_checkout_paid,
)
from .common import EventMixin


class ActivitiesIndexView(EventMixin, MetadataMixin, TemplateView):
    """Activities index view.
    """

    template_name = 'sanalberto/activity_list.html'

    subtitle = 'Actividades'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activities'] = self.event.activities.order_by('start')
        return context


class ActivityDetailView(EventMixin, MetadataMixin, DetailView):
    """Activity detail view.
    """

    model = Activity

    def get_queryset(self):
        return super().get_queryset().prefetch_related('organisers', 'documents')

    def get_subtitle(self, context: dict[str, Any]) -> str:
        return cast(Activity, context['object']).title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        activity: Activity = context['object']
        context['user_registration'] = activity.registrations.filter(user=self.request.user).first()

        return context


class ActivityRegistrationsView(EventMixin, MetadataMixin, LoginRequiredMixin, DetailView):
    """Activity registrations view.
    """

    model = Activity

    template_name = 'sanalberto/activity_registrations.html'

    def get_queryset(self) -> QuerySet[Activity]:
        return super().get_queryset().filter(organisers=self.request.user)

    def get_subtitle(self, context: dict[str, Any]) -> str:
        return 'Inscripciones para ' + cast(Activity, context['object']).title


class ActivityRegisterView(EventMixin, MetadataMixin, AccessMixin, DetailView):
    """Activity create registration view.
    """

    model = Activity

    template_name = 'sanalberto/activity_register.html'

    activity: Activity

    def get_subtitle(self, context: dict[str, Any]) -> str:
        title = cast(Activity, context['object']).title
        return f'Inscripción para {title}'

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        self.activity = cast(Activity, self.get_object())

        if not self.activity.accepts_registration:
            return redirect('sanalberto:activity_detail', self.activity.id)

        existing = self.activity.registrations.filter(user=self.request.user).first()

        if existing:
            return redirect('sanalberto:registration_detail', existing.id)

        return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        obj = ActivityRegistration(
            activity=self.activity,
            user=self.request.user,
            comments=request.POST.get('comments')
        )

        obj.save()

        try:
            session = create_registration_checkout(obj)

            obj.payment_id = session.id
        except Exception as e:
            obj.payment_error = str(e)

            messages.error(
                request,
                f'¡No se pudo crear la sesión de pago! Contacta con nosotros indicando este ID: R-{obj.id}'
            )

            return redirect('sanalberto:registration_detail', obj.id)
        finally:
            obj.save(update_fields=('payment_id', 'payment_error'))

        return redirect(session.url)


class RegistrationListView(EventMixin, MetadataMixin, LoginRequiredMixin, ListView):
    """Activity registrations list view.
    """

    model = ActivityRegistration

    subtitle = 'Mis inscripciones'

    def get_queryset(self):
        return super().get_queryset().filter(
            activity__event=self.event,
            user=self.request.user
        )


class RegistrationDetailView(EventMixin, MetadataMixin, LoginRequiredMixin, DetailView):
    """Activity registration detail view.
    """

    model = ActivityRegistration

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                activity__event=self.event,
                user=self.request.user
            )
            .prefetch_related('activity', 'user')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        created = cast(ActivityRegistration, context['object']).created
        context['old'] = created < timezone.now() - timedelta(seconds=3600 * 2)

        return context

    def get_subtitle(self, context: dict[str, Any]) -> str:
        title = cast(ActivityRegistration, context['object']).activity.title
        return f'Mi inscripción para {title}'


class RegistrationUpdateView(EventMixin, MetadataMixin, LoginRequiredMixin, UpdateView):
    """Activity registration update view"""

    model = ActivityRegistration

    fields = ('comments',)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                activity__event=self.event,
                user=self.request.user
            )
            .prefetch_related('activity', 'user')
        )

    def get_subtitle(self, context: dict[str, Any]) -> str:
        title = cast(ActivityRegistration, context['object']).activity.title
        return f'Editar mi inscripción para {title}'


class RegistrationPayView(EventMixin, LoginRequiredMixin, View):

    def post(self, request: AuthenticatedRequest, *args, **kwargs):
        with transaction.atomic():
            try:
                obj = (
                    ActivityRegistration
                    .objects
                    .filter(
                        activity__event=self.event,
                        user=request.user,
                        pk=kwargs['pk']
                    )
                    .select_for_update()
                    .prefetch_related('user')
                    .get()
                )
            except ActivityRegistration.DoesNotExist:
                return redirect('sanalberto:index')

            if obj.is_paid:
                messages.success(
                    request, '¡El pago se ha procesado correctamente!'
                )
                return redirect('sanalberto:registration_detail', obj.id)

            if obj.payment_id:
                existing_session: Session = Session.retrieve(
                    obj.payment_id,
                    expand=('payment_intent',)
                )

                if existing_session['payment_status'] == 'paid':
                    obj.is_paid = True
                    obj.payment_error = None
                    obj.save(update_fields=('is_paid', 'payment_error'))
                    return redirect('sanalberto:registration_detail', obj.id)

                intent: PaymentIntent = existing_session['payment_intent']

                try:
                    intent.cancel()
                except StripeError:
                    # If we cannot cancel it, the most probable cause is
                    # because it already expired - so we don't care ^^
                    pass

            try:
                session = create_registration_checkout(obj)

                obj.payment_id = session.id
                obj.payment_error = None
            except Exception as e:
                obj.payment_error = str(e)

                messages.error(
                    request,
                    '¡No se pudo crear la sesión de pago! '
                    f'Contacta con nosotros indicando este ID: R-{obj.id}'
                )

                return redirect('sanalberto:registration_detail', obj.id)
            finally:
                obj.save(update_fields=('payment_id', 'payment_error'))

        return redirect(session.url)


class RegistrationPaidView(EventMixin, LoginRequiredMixin, View):
    """Activity registration paid view"""

    def get(self, request: AuthenticatedRequest, *args, **kwargs) -> HttpResponse:
        with transaction.atomic():
            try:
                obj = (
                    ActivityRegistration
                    .objects
                    .filter(
                        activity__event=self.event,
                        user=request.user,
                        pk=kwargs['pk']
                    )
                    .select_for_update()
                    .prefetch_related('user')
                    .get()
                )
            except ActivityRegistration.DoesNotExist:
                return redirect('sanalberto:index')

            if obj.is_paid or not obj.payment_id:
                return redirect('sanalberto:registration_detail', obj.id)

            if is_checkout_paid(obj.payment_id):
                obj.payment_error = None
                obj.is_paid = True
            else:
                obj.payment_error = 'El pago no se ha verificado'

            obj.save(update_fields=('payment_error', 'is_paid'))

        return redirect('sanalberto:registration_detail', obj.id)
