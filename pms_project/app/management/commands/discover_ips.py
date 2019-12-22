import os
import datetime

from django.core.management import BaseCommand

import os
import socket
import multiprocessing
import subprocess
import os

from app.models import RpmReading, Loom


def add_data(self):
    import requests, re
    machine_no_regex = r"<H3>\s+Machine\s+(\d+)"
    RPM_regex = r"RPM\s+:\s+(\d+)"
    total_machines = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    found_machines = list()
    loom_id = Loom.objects.filter(loom_number=1).order_by('date_time')[:1].values('id')[0]['id']
    RpmReading.objects.create(machine_no=1, rpm=11 , meters=float(0.11), state="Running", loom_id=loom_id)
    for ip in range(100,117):
        base_ip = '192.168.0.'
        ip = base_ip+ str(ip) 
        try:

            response = requests.get(f"http://{ip}")
            
            machine_no = re.findall(machine_no_regex, response.text)
            rpm = re.findall(RPM_regex, response.text)
            machine_no = int(machine_no[0])
            rpm = int(rpm[0])
            # print("url: ", ip, "Machine: ", machine_no, "RPM: ", rpm)

            if machine_no>0 and rpm>0:

                circumference = Loom.objects.filter(loom_number=machine_no).order_by('date_time')[:1].values('circumference')[0]['circumference']
                meters = float(circumference) * 2.54 * float(rpm)  / 100.0
                loom_id = Loom.objects.filter(loom_number=machine_no).order_by('date_time')[:1].values('id')[0]['id']

                RpmReading.objects.create(machine_no=machine_no, rpm=rpm, meters=float(meters), state="Running", loom=loom_id)
                found_machines.append(machine_no)
                
            elif rpm is 0:
                loom_id = Loom.objects.filter(loom_number=machine_no).order_by('date_time')[:1].values('id')[0]['id']
                RpmReading.objects.create(machine_no=machine_no, rpm=0, meters=0.0 ,state="Stopped", loom=loom_id)
                found_machines.append(machine_no)

        except Exception as e:
            pass
            self.stdout.write(self.style.SUCCESS(f'Exception {e}'))                


    not_found = list(set(total_machines)-set(found_machines)) 
    self.stdout.write(self.style.SUCCESS(f'not_found list  {not_found}'))
    for machine in not_found:
        print("not found machine ", machine)
        loom_id = Loom.objects.filter(loom_number=machine).order_by('date_time')[:1].values('id')[0]['id']
        RpmReading.objects.create(machine_no=machine, rpm=0, meters=0.0, state="NoSensor", loom_id=loom_id)

class Command(BaseCommand):
    help = 'Discover all ip addresses'

    def handle(self, *args, **options):
        start = datetime.datetime.now()
        #netword_ips = map_network()
        add_data(self)

        end = datetime.datetime.now()
        total = end - start
        self.stdout.write(self.style.SUCCESS(f'Successfully updated ips in {total.total_seconds()}'))
