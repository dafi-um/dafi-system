from itertools import groupby

from telegram import Update
from telegram.ext import CallbackContext

from heart.models import (
    Degree,
    Group,
    Year,
)
from main.models import Config


def cmd_listgroups(update: Update, context: CallbackContext) -> None:
    assert update.effective_message is not None

    years = {degree: list(years) for degree, years in groupby(
        Year
        .objects
        .all()
        .prefetch_related('degree')
        .order_by('degree', 'year'),

        key=lambda y: y.degree.id
    )}

    groups = {degree: list(groups) for degree, groups in groupby(
        Group
        .objects
        .exclude(telegram_group_link=None)
        .prefetch_related('year__degree')
        .order_by('year__degree', 'year', 'number'),

        key=lambda g: g.degree().id
    )}

    current_school_year = Config.get('current_school_year')

    msg = '💬💬 *Grupos de Telegram{}* 💬💬\n\n'.format(
        (' ' + current_school_year) if current_school_year else ''
    )

    for degree in Degree.objects.filter(id__in=groups.keys()):
        msg += f'📚 {degree.name} 📚\n'

        if degree.is_master:
            for group in groups[degree.id]:
                msg += '    🔗 [{}]({})\n'.format(
                    group.name, group.telegram_group_link
                )

            continue

        year_groups = {
            year: list(groups) for year, groups in
            groupby(groups[degree.id], lambda g: g.year.year)
        }

        for year in years[degree.id]:
            if year.telegram_group_link:
                msg += '    🔗 [{}º General]({})\n'.format(
                    year.year, year.telegram_group_link
                )

            if year.year in year_groups:
                for group in year_groups[year.year]:
                    msg += '    🔗 [{}º {}]({})\n'.format(
                        group.year.year, group.name, group.telegram_group_link
                    )

            msg += '\n'

    update.effective_message.reply_markdown(
        msg, disable_web_page_preview=True
    )
