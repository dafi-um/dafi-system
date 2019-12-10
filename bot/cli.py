import schedule

from cmd import Cmd

from . import persistence


class BotCLI(Cmd):
    intro = 'Bot started! Type exit to stop the bot.'
    prompt = 'bot> '

    def do_data(self, arg):
        'Print the current content of the persistent data dictionary.'

        print('Persistent data ({}):'.format(len(persistence.get_all())))

        for k, v in persistence.get_all():
            print('  {}: {}'.format(k, v))

    def do_exit(self, arg):
        'Stop the polling and the bot process.'

        return True

    def do_flush(self, arg):
        'Flush the persistent data dictionary.'

        persistence.flush()
        print('Persistent data flushed!!')

    def do_jobs(self, arg):
        'Print the scheduled jobs.'

        for job in schedule.jobs:
            print(' -', job)

    def do_sync(self, arg):
        'Force a persistent data sync to disk.'

        print('Saving persistent data...')
        persistence.sync()
        print('Done!')
