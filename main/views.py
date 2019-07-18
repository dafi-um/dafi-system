from django.shortcuts import render

from blog.models import Post


def index(request):
    ctx = {
        'last_post': Post.objects.all().order_by('-pub_date').first()
    }

    return render(request, 'main/index.html', context=ctx)
