from apscheduler.schedulers.background import BackgroundScheduler

from brownie.utils import cron


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(cron.schedule_execute_interview_request(), 'interval', minutes=60)
    scheduler.start()
