#!/usr/bin/env python
import time

from django.contrib.auth.models import Permission, Group, ContentType
from django.core.management.base import BaseCommand

import app.models as models

class Command(BaseCommand):

    DELAY = 1*60

    def handle(self, *args, **options):
        while(True):
            raffles = models.Raffle.objects.filter(transaction__isnull=True)
            for raffle in raffles:
                print(raffle.name)
                raffle.getWinner()
            print('-------- Delay ' + self.DELAY + ' seconds --------')
            time.sleep(self.DELAY)



    
    
    
