import os
import datetime

from django.core.management import BaseCommand

import os
import socket
import multiprocessing
import subprocess
import os

from app.models import RpmReading


def pinger(job_q, results_q):
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
    """
    Find my IP address
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


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

    pool = [multiprocessing.Process(target=pinger, args=(jobs, results)) for i in range(pool_size)]

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

def add_data(ips):
    import requests, re
    machine_no_regex = r"<H3>\s+Machine\s+(\d+)"
    RPM_regex = r"RPM\s+:\s+(\d+)"
    for ip in ips:
        try:
            response = requests.get(f"http://{ip}")
            machine_no = re.findall(machine_no_regex, response.text)
            rpm = re.findall(RPM_regex, response.text)
            print("url: ", ip, "Machine: ", machine_no, "RPM: ", rpm)
            if machine_no and rpm:
                RpmReading.objects.create(machine_no=int(machine_no[0]), rpm=int(rpm[0]))
        except:
            pass


class Command(BaseCommand):
    help = 'Discover all ip addresses'

    def handle(self, *args, **options):
        start = datetime.datetime.now()
        netword_ips = map_network()
        add_data(netword_ips)
        end = datetime.datetime.now()
        total = end - start
        self.stdout.write(self.style.SUCCESS(f'Successfully updated ips in {total.total_seconds()}'))