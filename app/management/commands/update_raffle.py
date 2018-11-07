#!/usr/bin/env python
import time

from django.contrib.auth.models import Permission, Group, ContentType
from django.core.management.base import BaseCommand

import app.models as models

class Command(BaseCommand):

    DELAY = 10

    def handle(self, *args, **options):
        while(True):

            # Check if a raffle finished
            raffles = models.Raffle.objects.filter(transaction__isnull=True, is_active=True)
            for raffle in raffles:
                #print(raffle.name)
                print(">", raffle)
                raffle.getWinner()
            
            # Check payment of raffles
            raffles = models.Raffle.objects.filter(is_active=False)
            for raffle in raffles:
                print("<", raffle)
                raffle.checkPayment()

            time.sleep(self.DELAY)



    
    
    
