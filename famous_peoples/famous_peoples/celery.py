import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famous_peoples.settings')

app = Celery('famous_peoples')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# app.conf.beat_schedule = {
#     'send-daily-greeting': {
#         'task': 'users.tasks.send_daily_greeting',
#         'schedule': crontab(hour=18, minute=40),
#     },
# }