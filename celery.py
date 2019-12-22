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
def read_sensor_data():
    import requests
    from app.models import RpmReading
    import re
    print('Mapping...')
    lst = map_network()
    print(lst)
    for i in range(len(lst)):
        try:
            url = "http://" + lst[i]
            response = requests.get(url)
            machine_no_regex = r"<H3>\s+Machine\s+(\d+)"
            RPM_regex = r"RPM\s+:\s+(\d+)"

            machine_no = re.findall(machine_no_regex, response.text)
            rpm = re.findall(RPM_regex, response.text)
            print("IP: ", lst[i], "Machine: ", machine_no, "RPM: ", rpm)
            if machine_no and rpm:
                RpmReading.objects.create(machine_no=int(machine_no[0]), rpm=int(rpm[0]))
        except:
            print("This IP isn't from sensor: ", lst[i])


def pinger(job_q, results_q):
    import os, subprocess
    """
    Do Ping
    :param job_q:
    :param results_q:
    :return:
    """
    DEVNULL = open(os.devnull, 'w')
    while True:

        ip = job_q.get()

        if ip is None:
            break

        try:
            subprocess.check_call(['ping', '-c1', ip],
                                  stdout=DEVNULL)
            results_q.put(ip)
        except:
            pass

def get_my_ip():
    import socket
    """
    Find my IP address
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip
##
import multiprocessing
import multiprocessing.pool
class NoDaemonProcess(multiprocessing.Process):
    @property
    def daemon(self):
        print(".........false.......")
        return False

    @daemon.setter
    def daemon(self, value):
        pass


class NoDaemonContext(type(multiprocessing.get_context())):
    Process = NoDaemonProcess

# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class MyPool(multiprocessing.pool.Pool):
    def __init__(self, *args, **kwargs):
        print(".........classMyPool init.....")
        kwargs['context'] = NoDaemonContext()
        super(MyPool, self).__init__(*args, **kwargs)
##

def map_network(pool_size=255):

    """
    Maps the network
    :param pool_size: amount of parallel ping processes
    :return: list of valid ip addresses
    """

    ip_list = list()

    # get my IP and compose a base like 192.168.1.xxx
    ip_parts = get_my_ip().split('.')
    base_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'

    # prepare the jobs queue
    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()
    print("......pool..........")
    pool = [NoDaemonProcess(target=pinger, args=(jobs, results)) for i in range(pool_size)]

    for p in pool:
        p.start()

    # cue hte ping processes
    for i in range(1, 255):
        jobs.put(base_ip + '{0}'.format(i))

    for p in pool:
        jobs.put(None)

    for p in pool:
        p.join()

    # collect he results
    while not results.empty():
        ip = results.get()
        ip_list.append(ip)

    return ip_list



app.conf.beat_schedule = {
    "see-you-in-ten-seconds-task": {
        "task": "pms_project.celery.read_sensor_data",
        "schedule": 5.0
    }
}