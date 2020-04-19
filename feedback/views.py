from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.http import HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from meta.views import MetadataMixin

from .models import Comment, CommentVote, Topic


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
    model = Topic

    def get_queryset(self):
        return (
            super().get_queryset()
                .prefetch_related('documents')
                .prefetch_related('comments')
                .select_related('official_position')
        )

    def test_func(self):
        return self.get_object().is_public or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        topic = self.get_object()

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
    model = Topic

    template_name = 'feedback/topic_history.html'

    def get_queryset(self):
        return (
            super().get_queryset()
                .prefetch_related('documents')
                .prefetch_related('comments')
                .select_related('official_position')
        )

    def test_func(self):
        return self.get_object().is_public or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        topic = self.get_object()
        comments = topic.comments.filter(is_official=True)

        context = super().get_context_data(**kwargs)
        context['meta'] = topic.as_meta(self.request)
        context['comments'] = comments

        return context


class CreateOfficialPositionView(UserPassesTestMixin, CreateView):
    model = Comment

    fields = ('text', 'topic')

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse('feedback:history', args=[self.object.topic.slug])

    def form_valid(self, form):
        form.instance.is_official = True

        res = super().form_valid(form)

        Topic.objects.filter(pk=self.object.topic.pk).update(
            official_position=self.object,
            updated=timezone.now()
        )

        return res


class CreateTopicPointView(UserPassesTestMixin, CreateView):
    model = Comment

    fields = ('text', 'topic')

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse('feedback:detail', args=[self.object.topic.slug])

    def form_valid(self, form):
        form.instance.is_point = True

        return super().form_valid(form)


class CreateCommentView(LoginRequiredMixin, CreateView):
    model = Comment

    fields = ('text', 'topic', 'is_anonymous')

    def get_success_url(self):
        return reverse('feedback:detail', args=[self.kwargs['slug']])

    def form_valid(self, form):
        form.instance.author = self.request.user

        if not form.instance.topic.is_public and not self.request.user.is_staff:
            return HttpResponseForbidden()

        return super().form_valid(form)


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, MetadataMixin, DeleteView):
    model = Comment

    image = 'images/favicon.png'

    def test_func(self):
        if self.get_object().is_point:
            return self.request.user.is_staff

        return self.request.user == self.get_object().author

    def get_queryset(self):
        return super().get_queryset().select_related('topic')

    def get_meta_title(self, context):
        return 'Eliminar comentario en {}'.format(self.get_object().topic.title)

    def get_success_url(self):
        return reverse('feedback:detail', args=[self.get_object().topic.slug])


class CommentVoteView(DetailView):
    model = Comment

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'], args, kwargs)

    def get_totals(self):
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

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        comment = self.get_object()

        if not comment.topic.is_public and not request.user.is_staff:
            return HttpResponseForbidden()

        try:
            action = int(request.POST.get('action'))
        except:
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
                return JsonResponse({'error': 'invalid action'}, status=400)

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
