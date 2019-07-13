from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, CallbackQueryHandler

from blog.models import Post

def generate_blog_list():
    msg = '*El Blog de DAFI*\n\n'
    reply_markup = None

    posts = Post.objects.all()

    if not posts:
        msg += '_No hay entradas disponibles_'
    else:
        buttons = []

        for p in posts:
            txt = '{} ({})'.format(p.title, p.pub_date.strftime('%d %b %y'))
            buttons.append([InlineKeyboardButton(txt, callback_data='blog=' + p.slug)])

        reply_markup = InlineKeyboardMarkup(buttons)

    return msg, reply_markup

def blog_list(update, context):
    msg, reply_markup = generate_blog_list()

    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

def blog_detail(update, context):
    post = None
    slug = update.callback_query.data.replace('blog=', '')

    msg = '_No se ha encontrado el artículo que buscabas_'
    reply_markup = None

    if slug == '.List':
        msg, reply_markup = generate_blog_list()
    elif slug:
        try:
            post = Post.objects.get(slug=slug)
        except:
            pass

        if post:
            msg = '*- ' + post.title + ' -*\n\n' + post.content

        buttons = [[InlineKeyboardButton('<< Volver a la lista', callback_data='blog=.List')]]
        reply_markup = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

def add_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('blog', blog_list))
    dispatcher.add_handler(CallbackQueryHandler(blog_detail, pattern='blog'))
