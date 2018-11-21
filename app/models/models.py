import json
import random
import datetime

from django.db import models

from app.dash import Dash
from app.models.User import User


class Transaction(models.Model):
  address = models.CharField(max_length=100, primary_key=True)
  user   = models.ForeignKey(User, related_name="transactions")
  amount = models.DecimalField(max_digits=20, decimal_places=6)
  raffle = models.ForeignKey("Raffle", related_name="transactions")
  blockHeight = models.IntegerField(verbose_name="Block Height")
  boughtTicket = models.IntegerField(verbose_name="Bought Tickets")
  notified = models.BooleanField(verbose_name="Was notified", default=True)
  date = models.DateTimeField(verbose_name="Datetime", null=True)
  sent = models.BooleanField(verbose_name="Sent", default=False)
  class Meta:
    ordering = ['-blockHeight']

  def __init__(self, *args, **kwargs):
    super(Transaction, self).__init__(*args, **kwargs)

  def save(self, *args, **kwargs):
    super(Transaction, self).save(*args, **kwargs)

  def __str__(self):
    return str((self.user, self.address))

  @property
  def getDate(self):
    if not self.date:
      rawTransaction = Dash.getrawtransaction(self.address)
      if not rawTransaction:
        return "-"
      if  'time' in rawTransaction:
        timestamp = rawTransaction['time']
        if 'height' in rawTransaction and self.blockHeight != rawTransaction['height']:
          self.blockHeight = rawTransaction['height']
          self.date = datetime.datetime.fromtimestamp(timestamp)
          self.save()
        return datetime.datetime.fromtimestamp(timestamp)
      else:
        return "Not confirmed Yet"
    else:
      return self.date

class AddressGenerated(models.Model):
  user    = models.ForeignKey(User)
  raffle  = models.ForeignKey("Raffle", related_name="addresses")
  address = models.CharField(unique=True, max_length=64, verbose_name='Address')


  def __str__(self):
    return str((self.user, self.address))