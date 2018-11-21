#!/usr/bin/env python
import time
import os

from django.contrib.auth.models import Permission, Group, ContentType
from django.core.management.base import BaseCommand

import app.models as models

pidfile = ""

class Command(BaseCommand):

    DELAY = 10
   
    def add_arguments(self, parser):
        parser.add_argument(
            '--pid',
            help='Specify pid file to use when running as daemon.',
        )

    def writePidFile(self):
        pid = str(os.getpid())
        f = open(pidfile, 'w')
        f.write(pid+"\n")
        f.close()


    def handle(self, *args, **options):

        if options['pid'] is not None:
            global pidfile
            pidfile = options['pid']
            self.writePidFile()

        while(True):
            try:
                # Check if a raffle finished
                raffles = models.Raffle.objects.filter(transaction__isnull=True, is_active=True)
                for raffle in raffles:
                    #print(raffle.name)
                    raffle.getWinner()
                
                # Check payment of raffles
                raffles = models.Raffle.objects.filter(is_active=False)
                for raffle in raffles:
                    raffle.checkPayment()

                
            except Exception as e:
                print(e)
            time.sleep(self.DELAY)

def exit():
    if pidfile != "":
        os.remove(pidfile)


import atexit
atexit.register(exit)