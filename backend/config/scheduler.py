# config/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from helpers.helper import getAuthToken, check_and_notify_women

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(getAuthToken, 'interval', minutes=50)
    scheduler.start()

def start_notify():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_notify_women, 'cron', hour='7,19')
    scheduler.start()