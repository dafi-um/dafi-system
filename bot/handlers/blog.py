from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from blog.models import Post

from main.utils import get_url

from .handlers import add_handler

@add_handler('blog')
def blog_list(update, context):
    posts = Post.objects.order_by('-pub_date')[:10]

    if not posts:
        return '*El Blog de DAFI*\n\n_No hay entradas disponibles_'

    msg = '*El Blog de DAFI*\n\nMostrando los últimos {} posts.'.format(len(posts))

    buttons = []

    for p in posts:
        buttons.append([
            InlineKeyboardButton(p.title, url=get_url('blog:detail', args=[p.slug]))
        ])

    return msg, InlineKeyboardMarkup(buttons)
