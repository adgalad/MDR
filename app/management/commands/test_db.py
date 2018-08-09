#!/usr/bin/env python
import datetime

from app.models import *
from django.utils import timezone
from django.contrib.auth.models import Permission, Group, ContentType
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def createOperations(self):
        user = User.objects.get(email="admin@admin.com")
        currency = Currency.objects.all()[0]
        # account = Account(number="12312312", id_bank=Bank.objects.all()[0], id_currency=currency)
        account = Account.objects.get(pk=1)
        for i in ['Cancelada','Faltan recaudos','Por verificar','Verificado','Fondos ubicados','Fondos transferidos','En reclamo']:
            for j in range(1,100):
            
                o = Operation(fiat_amount=100,
                          status=i,
                          date=timezone.now(),
                          expiration=timezone.now(),
                          id_client=user,
                          id_account=account,
                          exchange_rate = 10,
                          origin_currency=currency,
                          target_currency=currency,
                          is_active=(i!='Fondos transferidos'))
                o._save( "US","VE", timezone.now())


    def handle(self, *args, **options):
        self.createOperations()



    
    
    
