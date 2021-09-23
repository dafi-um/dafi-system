import threading
from time import sleep

import schedule


_jobs = []


class SchedulerThread(threading.Thread):
    """Thread that runs scheduled jobs"""

    stopper = threading.Event()

    @classmethod
    def run(cls):
        print('Scheduler thread started!')

        while not cls.stopper.is_set():
            schedule.run_pending()
            sleep(1)


def add_job(timing):
    """Decorator to add a job to the scheduler"""

    def decorator(job):
        _jobs.append((timing, job))
        return job

    return decorator


def load_jobs(bot):
    """Loads all the scheduled jobs into the scheduler"""

    for timing, job in _jobs:
        timing.do(job, bot)

    _jobs.clear()
