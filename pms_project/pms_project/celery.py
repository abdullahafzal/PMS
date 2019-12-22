from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pms_project.settings')
app = Celery('pms_project')

# Using a string here means the worker will not have to
# pickle the object when using Windows.

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)



@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))



@app.task
def read_ip_data():
    import requests
    import re
    from app.models import RpmReading

    print("ip method")
    base_ip = "http://192.168.43."
    valid_urls = []
    for i in range(185,255):
        url = base_ip + str(i)
        try:
            response = requests.get(url)
            valid_urls.append(url)
            #print("found: ",url)

        except:
            #print("not found", i)
            pass
    machine_no_regex = r"<H3>\s+Machine\s+(\d+)"
    RPM_regex = r"RPM\s+:\s+(\d+)"
    for url in valid_urls:
        response = requests.get(url)
        machine_no = re.findall(machine_no_regex, response.text)
        rpm = re.findall(RPM_regex, response.text)
        print("url: ", url, "Machine: ", machine_no, "RPM: ", rpm)
        if machine_no and rpm:
            RpmReading.objects.create(machine_no=int(machine_no[0]), rpm=int(rpm[0]))

app.conf.beat_schedule = {
    "New_see-you-in-ten-seconds-task": {
        "task": "pms_project.celery.read_ip_data",
        "schedule": 60.0
    }

}