import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ThreatModelGenerator.settings")
app = Celery("ThreatModelGenerator")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.update({
    "broker_connection_retry_on_startup":
    True}
)
app.autodiscover_tasks()