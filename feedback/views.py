from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.db.models import (
    Count,
    Q,
)
from django.forms.models import ModelForm
from django.http import (
    HttpResponseForbidden,
    HttpResponseNotAllowed,
    JsonResponse,
)
from django.http.response import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
)

from meta.views import MetadataMixin

from users.utils import (
    AuthenticatedRequest,
    SimpleRequest,
)

from .models import (
    Comment,
    CommentVote,
    Topic,
)


class TopicListView(MetadataMixin, ListView):

    model = Topic

    title = 'Feedback - DAFI'
    description = (
        'Temas actuales y opiniones de alumnos en '
        'la Delegación de Estudiantes de Informática'
    )
    image = 'images/favicon.png'

    def get_queryset(self):
        return super().get_queryset().filter(is_public=True)


class TopicDetailView(UserPassesTestMixin, DetailView):

    request: SimpleRequest

    model = Topic

    def get_queryset(self):
        return (
            super().get_queryset()
            .prefetch_related('documents')
            .prefetch_related('comments')
            .select_related('official_position')
        )

    def test_func(self):
        topic: Topic = self.get_object()
        return topic.is_public or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        topic: Topic = self.get_object()

        comments = topic.comments.annotate(
            total_upvotes=Count('votes', filter=Q(votes__is_upvote=True)),
            total_downvotes=Count('votes', filter=Q(votes__is_upvote=False))
        )

        upvotes = []
        downvotes = []

        if self.request.user.is_authenticated:
            votes = (
                CommentVote.objects
                .filter(comment__topic=topic, user=self.request.user)
                .prefetch_related('comment')
            )

            for vote in votes:
                if vote.is_upvote:
                    upvotes.append(vote.comment)
                else:
                    downvotes.append(vote.comment)

        if topic.official_position:
            official_position = comments.filter(id=topic.official_position.id).first()
        else:
            official_position = None

        context = super().get_context_data(**kwargs)
        context['meta'] = topic.as_meta(self.request)
        context['official_position'] = official_position
        context['comments'] = comments.filter(is_official=False, is_point=False)
        context['points'] = comments.filter(is_point=True)
        context['upvotes'] = upvotes
        context['downvotes'] = downvotes

        return context


class HistoryView(UserPassesTestMixin, DetailView):

    request: SimpleRequest

    model = Topic

    template_name = 'feedback/topic_history.html'

    def get_queryset(self):
        return (
            super().get_queryset()
            .prefetch_related('documents')
            .prefetch_related('comments')
            .select_related('official_position')
        )

    def test_func(self) -> bool:
        topic: Topic = self.get_object()
        return topic.is_public or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        topic: Topic = self.get_object()

        comments = topic.comments.filter(is_official=True)

        context = super().get_context_data(**kwargs)
        context['meta'] = topic.as_meta(self.request)
        context['comments'] = comments
        return context


class CreateOfficialPositionView(UserPassesTestMixin, CreateView):

    request: SimpleRequest
    object: Comment

    model = Comment

    fields = ('text', 'topic')

    def test_func(self) -> bool:
        return self.request.user.is_staff

    def get_success_url(self) -> str:
        return reverse('feedback:history', args=[self.object.topic.slug])

    def form_valid(self, form: 'ModelForm[Comment]') -> HttpResponse:
        form.instance.is_official = True

        res = super().form_valid(form)

        Topic.objects.filter(pk=self.object.topic.pk).update(
            official_position=self.object,
            updated=timezone.now()
        )

        return res


class CreateTopicPointView(UserPassesTestMixin, CreateView):

    request: SimpleRequest
    object: Comment

    model = Comment

    fields = ('text', 'topic')

    def test_func(self) -> bool:
        return self.request.user.is_staff

    def get_success_url(self) -> str:
        return reverse('feedback:detail', args=[self.object.topic.slug])

    def form_valid(self, form: 'ModelForm[Comment]') -> HttpResponse:
        form.instance.is_point = True

        return super().form_valid(form)


class CreateCommentView(LoginRequiredMixin, CreateView):

    request: AuthenticatedRequest
    object: Comment

    model = Comment

    fields = ('text', 'topic', 'is_anonymous')

    def get_success_url(self):
        return reverse('feedback:detail', args=[self.kwargs['slug']])

    def form_valid(self, form: 'ModelForm[Comment]'):
        form.instance.author = self.request.user

        if not form.instance.topic.is_public and not self.request.user.is_staff:
            return HttpResponseForbidden()

        return super().form_valid(form)


class DeleteCommentView(
        LoginRequiredMixin,
        UserPassesTestMixin,
        MetadataMixin,
        DeleteView):

    request: SimpleRequest

    model = Comment

    image = 'images/favicon.png'

    def test_func(self):
        comment: Comment = self.get_object()

        if comment.is_point:
            return self.request.user.is_staff

        return self.request.user == comment.author

    def get_queryset(self):
        return super().get_queryset().select_related('topic')

    def get_meta_title(self, context):
        comment: Comment = self.get_object()
        return 'Eliminar comentario en {}'.format(comment.topic.title)

    def get_success_url(self):
        comment: Comment = self.get_object()
        return reverse('feedback:detail', args=[comment.topic.slug])


class CommentVoteView(LoginRequiredMixin, DetailView):

    request: AuthenticatedRequest

    model = Comment

    def get(self, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'], args, kwargs)

    def get_totals(self) -> HttpResponse:
        totals = (
            CommentVote.objects
            .filter(comment=self.get_object())
            .aggregate(
                upvotes=Count('pk', filter=Q(is_upvote=True)),
                downvotes=Count('pk', filter=Q(is_upvote=False))
            )
        )

        return JsonResponse({
            'total_upvotes': totals['upvotes'],
            'total_downvotes': totals['downvotes']
        })

    def post(self, request: AuthenticatedRequest, *args, **kwargs) -> HttpResponse:
        comment: Comment = self.get_object()

        if not comment.topic.is_public and not request.user.is_staff:
            return HttpResponseForbidden()

        try:
            action = int(request.POST.get('action', ''))
        except ValueError:
            return JsonResponse({
                'error': 'invalid action parameter',
            }, status=400)

        if action < -1 or action > 1:
            return JsonResponse({
                'error': 'invalid action parameter'
            }, status=400)

        vote = CommentVote.objects.filter(comment=comment, user=request.user).first()

        if action == 0:
            if not vote:
                return JsonResponse({
                    'error': 'invalid action'
                }, status=400)

            vote.delete()

            return self.get_totals()

        is_upvote = action == 1

        if not vote:
            vote = CommentVote(comment=comment, user=request.user, is_upvote=is_upvote)
        elif is_upvote:
            if vote.is_upvote:
                return JsonResponse({'nochange': True})

            vote.is_upvote = True
        else:
            if not vote.is_upvote:
                return JsonResponse({'nochange': True})

            vote.is_upvote = False

        vote.save()

        return self.get_totals()
