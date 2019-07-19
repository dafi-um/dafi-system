from datetime import date

from django.shortcuts import render

from blog.models import Post
from clubs.models import ClubMeeting


def index(request):
    ctx = {
        'last_post': Post.objects.all().order_by('-pub_date').first(),
        'meetings': ClubMeeting.objects.all().exclude(moment__lt=date.today()).order_by('moment')[:5],
    }

    return render(request, 'main/index.html', context=ctx)
