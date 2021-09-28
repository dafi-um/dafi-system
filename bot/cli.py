from cmd import Cmd

from telegram.ext import (
    BasePersistence,
    JobQueue,
)


class BotCLI(Cmd):

    intro = 'Bot started! Type exit to stop the bot.'
    prompt = 'bot> '

    def __init__(self, persistence: BasePersistence[dict, dict, dict], job_queue: JobQueue) -> None:
        super().__init__()
        self.persistence = persistence
        self.job_queue = job_queue

    def do_data(self, arg):
        'Shows the content of the bot persistent data dictionary.'

        persistence = self.persistence.get_bot_data()

        print('Persistent data ({}):'.format(len(persistence.keys())))

        for k, v in persistence.items():
            print('  {}: {}'.format(k, v))

    def do_exit(self, arg):
        'Stop the polling and the bot process.'

        return True

    def do_flush(self, arg):
        'Flush the bot persistent data dictionary.'

        self.persistence.flush()
        print('Bot persistent data flushed to disk!')

    def do_jobs(self, arg):
        'Print the scheduled jobs.'

        for job in self.job_queue.jobs():
            print(f'{job.callback} - next at {job.next_t}')

    def do_clear(self, arg):
        'Clears the bot persistent data.'

        self.persistence.update_bot_data({})

        print('Bot persistent data cleared!')
