from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DetailView, TemplateView
from django.views.generic.base import View
from django.views.generic.list import ListView

from meta.views import MetadataMixin

from website.settings import STRIPE_PK

from ..models import Activity, ActivityRegistration
from ..payments import create_registration_checkout, is_checkout_paid

from .common import EventMixin


class ActivitiesIndexView(EventMixin, MetadataMixin, TemplateView):
    '''Activities index view'''

    template_name = 'sanalberto/activity_list.html'

    title = 'Actividades'

    def get_context_data(self, **kwargs):
        event = self.get_current_event()

        activities = Activity.objects.filter(event=event).order_by('start')

        context = super().get_context_data(**kwargs)
        context['activities'] = activities
        return context


class ActivityDetailView(EventMixin, MetadataMixin, DetailView):
    '''Activity detail view'''

    model = Activity

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if obj:
            self.title = obj.title

        return obj

    def get_context_data(self, **kwargs):
        activity = self.get_object()

        registration = activity.get_user_registration(self.request.user)

        context = super().get_context_data(**kwargs)
        context['user_registration'] = registration
        return context


class ActivityRegisterView(EventMixin, MetadataMixin, LoginRequiredMixin, DetailView):
    '''Activity create registration view'''

    model = Activity

    template_name = 'sanalberto/activity_register.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if obj:
            self.title = 'Inscripción ' + obj.title

        return obj

    def get(self, request, *args, **kwargs):
        activity = self.get_object()

        already = activity.get_user_registration(self.request.user)

        if already:
            return redirect('sanalberto:registration_detail', already.id)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.get_current_event():
            return redirect('sanalberto:index')

        activity = self.get_object()

        already = activity.get_user_registration(request.user)

        if already:
            return redirect('sanalberto:registration_detail', already.id)

        obj = ActivityRegistration(
            activity=activity,
            user=self.request.user,
            comments=request.POST.get('comments')
        )

        try:
            obj.save()
        except:
            # TODO: Display error

            return redirect('sanalberto:activity_detail', activity.id)

        try:
            session = create_registration_checkout(obj)

            obj.payment_id = session.id
        except Exception as e:
            obj.payment_error = str(e)

        obj.save()

        return redirect('sanalberto:registration_detail', obj.id)


class RegistrationListView(EventMixin, MetadataMixin, LoginRequiredMixin, ListView):
    '''Activity registrations list view'''

    model = ActivityRegistration

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class RegistrationDetailView(EventMixin, MetadataMixin, LoginRequiredMixin, DetailView):
    '''Activity registration detail view'''

    model = ActivityRegistration

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if obj:
            self.title = 'Mi inscripción para ' + obj.activity.title

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['STRIPE_PK'] = STRIPE_PK
        return context


class RegistrationPaidView(EventMixin, LoginRequiredMixin, View):
    '''Activity registration paid view'''

    def get(self, request, *args, **kwargs):
        if not self.get_current_event():
            return redirect('sanalberto:index')

        obj_id = kwargs['pk']

        obj = ActivityRegistration.objects.filter(user=request.user, pk=obj_id).first()

        if not obj:
            return redirect('sanalberto:index')

        if obj.is_paid:
            return redirect('sanalberto:registration_detail', obj.id)

        if is_checkout_paid(obj.payment_id):
            obj.payment_error = None
            obj.is_paid = True
        else:
            obj.payment_error = 'El pago no se ha verificado'

        obj.save()

        return redirect('sanalberto:registration_detail', obj.id)
