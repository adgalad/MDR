import json
import random
import datetime
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.template.loader import render_to_string, get_template
from django.core.mail import send_mail
from django.conf import settings
from ckeditor.fields import RichTextField

from app.helpers import EmailThread
from app.dash import Dash
from app.models.User import User
from app.models.models import Transaction, Notification

    
rafflePrice = {
  'Mini Raffle':0.01,
  'Raffle': 0.05,
  'Mega Raffle': 0.1
}

raffleDuration = {
  'Mini Raffle': 7,
  'Raffle': 14,
  'Mega Raffle': 30
}

SIGNS_REQUIRED = 2

PAYMENT_AMOUNT = 0.1 # Dash

MIN_TICKETS_SOLD = 20

DEFAULT_DOMAIN = "http://megadashraffle.org"

class Raffle(models.Model):
  name = models.CharField(verbose_name="Raffle Name", max_length=100, unique=True)
  created_at = models.DateTimeField(auto_now_add=True)
  is_active = models.BooleanField("Raffle was paid", default=False)
  summary = models.CharField(verbose_name="Summary", max_length=250)
  description = RichTextField(verbose_name="Description")
  thumbnail_url = models.CharField(verbose_name="Thumbnail Image URL (square image of at least 300x300 pixels)", blank=True, null=True, max_length=2048)
  addressPrize = models.CharField(verbose_name="Prize Address", blank=True, max_length=100)
  addressProject = models.CharField(null=True, verbose_name="Beneficiary Address", max_length=100)
  prizePercentage = models.FloatField(verbose_name="Prize Percentage", default=44.44445)
  projectPercentage = models.FloatField(verbose_name="Project Percentage", default=55.55555)
  drawDate = models.DateTimeField(verbose_name="Draw date")
  ticketsSold = models.IntegerField(verbose_name="Tickets Sold", default=0)
  ticketPrice = models.DecimalField(verbose_name="Ticket Price", max_digits=20, decimal_places=6)
  winner = models.ForeignKey(User, blank=True, null=True, related_name="rafflesWon")
  owner = models.ForeignKey(User, related_name="ownsRaffles", blank=True, null=True)
  winnerAddress = models.CharField(verbose_name="Winner Address", max_length=100, blank=True, null=True)
  totalPrize = models.DecimalField(verbose_name="totalPrize", default=0, max_digits=20, decimal_places=6, blank=True, null=True)
  transaction = models.CharField(verbose_name="Transaction", max_length=100, blank=True, null=True)
  # signers = models.ManyToManyField(User, blank=True, through='RaffleSigner', verbose_name="Signers",related_name="signs")
  type_choice = ( ('Mini Raffle', 'Mini Raffle'), ('Raffle', 'Raffle'), ('Mega Raffle', 'Mega Raffle') )
  type = models.CharField(null=True, blank=True, choices=type_choice, max_length=16, default='Mini Raffle', verbose_name="Type of Raffle")
  blockHeight = models.IntegerField(verbose_name="Block Height", default=0)
  isMultisig = models.BooleanField(default=True, verbose_name="Multisign Prize address")
  feeWasSendback = models.BooleanField(default=False)
  # signsRequired = models.IntegerField(blank=True, default=3, verbose_name="Signs Required", validators=[MaxValueValidator(6), MinValueValidator(1)])
  
  MSaddress = models.CharField(null=True, verbose_name="Generated address for MS", max_length=100)
  MSpubkey1 = models.CharField(verbose_name="Multisig Public Key 1", max_length=67, blank=True, null=True)
  MSpubkey2 = models.CharField(verbose_name="Multisig Public Key 2", max_length=67, blank=True, null=True)
  MSpubkey3 = models.CharField(verbose_name="Multisig Public Key 3", max_length=67, blank=True, null=True)
  MSpubkey4 = models.CharField(verbose_name="Multisig Public Key 4", max_length=67, blank=True, null=True)
  MSpubkey5 = models.CharField(verbose_name="Multisig Public Key 5", max_length=67, blank=True, null=True)
  MSpubkey6 = models.CharField(verbose_name="Multisig Public Key 6", max_length=67, blank=True, null=True)

  MSredeemScript = models.CharField(verbose_name="Multisig Redeem Script", max_length=1024, blank=True, null=True)
  
  commandSignRawTx = models.CharField(verbose_name="Command to sign raw transaction", max_length=1024*100, null=True, blank=True) # 100 kb


  @property
  def getPrice(self):
    print(rafflePrice[self.type], rafflePrice, self.type)
    return rafflePrice[self.type]

  @property
  def getPrize(self):
    return float(self.totalPrize)*self.prizePercentage/100.0

  @property
  def getCollected(self):
    return float(self.totalPrize)*self.projectPercentage/100.0


  @property
  def getDurationTimestamp(self):
    return raffleDuration[self.type] * 24 * 3600

  @property
  def getTimeLeft(self):
    return int((self.drawDate - timezone.now()).total_seconds())

  def __str__(self):
    return self.name

  def get_absolute_url(self):
    return "/raffle/%i" % self.id

  @property
  def isMultisigned(self):
    for i in range(1,7):
      if getattr(self,"MSpubkey"+str(i)):
        return True
    return False

  @property
  def thumbnail(self):
    if self.thumbnail_url != '':
      return self.thumbnail_url
    else:
      return '/static/img/placeholder.png'

  def getMSpubkey(self):
    keys = []
    for i in range(1,7):
      key = getattr(self,"MSpubkey"+str(i))
      if key:
        keys.append(key)
    return keys

  @property
  def getPrivkey(self):
    keys = []
    for i in range(1,7):
      key = getattr(self,"privkey"+str(i))
      if key:
        keys.append(key)
    return keys

  
  @property
  def finished(self):
    # count = Dash.getblockcount()
    # return self.blockHeight < count
    print(self.drawDate, timezone.now(),self.drawDate < timezone.now())
    return self.drawDate < timezone.now()

  def createMultisigAddress(self):
    if self.isMultisigned:
      data = Dash.createmultisig(str(SIGNS_REQUIRED), self.getMSpubkey())
      self.addressPrize = data['address']
      self.MSredeemScript = data['redeemScript']

  def checkPayment(self):
    if self.is_active:
      return
    
    balance = Dash.getaddressbalance([self.MSaddress])['balance']/100000000
    if balance >= PAYMENT_AMOUNT:
      self.is_active = True
      self.save()
      
      # models.Notification(user=self.owner, transaction=None, message="You've paid the raffle's fee.")
      subject = 'Your raffle, %s, has been published'%self.name
      from_email = settings.EMAIL_HOST_USER
      to_email = [self.owner.email]
      html_message = render_to_string(
                 'baseEmail.html',
                 {
                     'message': 'Now that you have paid the raffle creation fee, we\'ve published your raffle in our site. You can view the details with the following button. <br> <br> <a class="btn btn-primary" href="%s/raffle/%d">Raffle Details</a>'%( DEFAULT_DOMAIN, self.pk) ,
                     'title':  'Your raffle, %s, has been published'%self.name,
                 }
             )
      EmailThread(subject=subject,
                  message='Now that you have paid the raffle creation fee, we\'ve published your raffle in our site.',
                  html_message=html_message,
                  recipient_list=to_email).start()

    elif timezone.now()-self.created_at > datetime.timedelta(days=7):
      self.delete()


  def checkAllTx(self):
    transactions = self.transactions.all()
    for addressGenerated in self.addresses.all():
      txs = Dash.getaddresstxids([addressGenerated.address])
      if txs is None:
        continue

      for i in txs:
        if transactions.filter(address=i).exists():
          continue

        txRaw = Dash.getrawtransaction(i)
        if txRaw is None:
          continue

        dt = txRaw['time']
        if dt > self.drawDate.timestamp():
          continue

        total = 0
        for detail in txRaw['vout']:
          if addressGenerated.address in detail['scriptPubKey']['addresses']:
            amount = detail['value']
            tickets = int(round(amount/float(self.ticketPrice), 5))
            if Transaction.objects.filter(pk=txRaw['txid']).exists():
              continue
              
            Transaction(
              address=txRaw['txid'],
              amount=amount,
              user=addressGenerated.user,
              blockHeight=txRaw['height'],
              raffle=self,
              boughtTicket=tickets,
              notified=False,
            ).save()
            total += amount
        if total == 0.0:
          continue
        total = total*90/100
        Dash.sendtoaddress(
          self.addressPrize,
          str(total)
        )
        self.totalPrize += Decimal(total)
        self.save()
  
  def getTransactions(self):
    self.checkAllTx()
    txs = Dash.getrawmempool()
    transactions = self.transactions.all()
    
    for i in txs:
        if transactions.filter(address=i).exists():
          txs.remove(i)      

    for i in txs:
      txRaw = Dash.getrawtransaction(i)
      # tx = Dash.gettransaction(i)

      if txRaw is None: #or tx is None or not 'fee' in tx:
        continue

      # dt = txRaw['time']
      # if dt > self.drawDate.timestamp():
      #   continue
      total = 0
      for addressGenerated in self.addresses.all():
        
        for detail in txRaw['vout']:
          if 'scriptPubKey' in detail and 'addresses' in detail['scriptPubKey'] and addressGenerated.address in detail['scriptPubKey']['addresses']:
            amount = detail['value']
            tickets = int(round(amount/float(self.ticketPrice), 5))
            if Transaction.objects.filter(pk=txRaw['txid']).exists():
              continue
            Transaction(
              address=txRaw['txid'],
              amount=amount,
              user=addressGenerated.user,
              blockHeight=Dash.getblockcount(),
              raffle=self,
              boughtTicket=tickets,
              notified=False
            ).save()
            total += amount
      if total == 0.0:
        continue
      total = (total)*90/100
      Dash.sendtoaddress(
        self.addressPrize,
        str(total)
      )
      self.totalPrize += Decimal(total)

      self.save()

  def addPrivKey(self, privkey):
    for i in range(1, self.signsRequired + 1):
      _privkey = getattr(self, "privkey"+str(i))
      if not _privkey:
        setattr(self, "privkey"+str(i), privkey)
        self.save()
        break
      elif _privkey == privkey:
        return "Duplicated Private Key"
    self.__signMultisignedTransaction()
    return "Private Key succesfully added"
  
  def nPrivkey(self):
    n = 0
    for i in range(1, self.signsRequired + 1):
      if getattr(self, "privkey"+str(i)):
        n += 1
    return n


  def __signMultisignedTransaction(self):
    txs = Dash.getaddresstxids([self.addressPrize])
    if txs is None:
      return -1

    fee = 0.002
    scriptPubKey = None
    vout = 0
    txData = []
    print(">>>>", txs)
    for tx in txs:
      rawTx = Dash.getrawtransaction(tx)
      if rawTx is None:
        return -1

      for _vout in rawTx['vout']:
        if _vout['scriptPubKey']['type'] == 'scripthash' and self.addressPrize in _vout['scriptPubKey']['addresses']:
          scriptPubKey = _vout['scriptPubKey']['hex']
          vout = _vout['n']
          break

      txData.append({
        "txid": tx,
        "vout": vout,
        "scriptPubKey": scriptPubKey
      })


    # sortedTx = sorted(txData, key=lambda tx: -tx['time']) 

    outputs1 = [{"txid": tx['txid'], "vout": tx['vout']}  for tx in (txData)]
    outputs2 = 'null' #[{"txid": tx['txid'], "vout": tx['vout'],"scriptPubKey": tx['scriptPubKey'], "redeemScript": self.MSredeemScript} for tx in (txData)]

    
    prize = Dash.getaddressbalance([self.addressPrize])['balance']/100000000
    
    newAddress = Dash.getnewaddress()
    
    if self.winnerAddress == self.addressProject:
      toAddress = {
        self.winnerAddress: '%.8f'%(prize-fee),
      }
    else:
      winnerAmount = float('%.8f'%(prize*self.prizePercentage/100))
      projectAmount =  float('%.8f'%(prize-winnerAmount-fee)) 
      toAddress = {
        self.winnerAddress: winnerAmount,
        self.addressProject: projectAmount,
      }

    transaction = Dash.createrawtransaction(outputs1, toAddress)

    if transaction is None:
      return -1

    privkey = Dash.dumpprivkey(self.MSaddress)
    sign = Dash.signrawtransaction(transaction.replace('\n',''), outputs2, [privkey])
    self.commandSignRawTx = ' '.join(['signrawtransaction', "'%s'"%sign['hex'], "'%s'"%json.dumps(outputs2), "'%s'"%'[ "<b style="color:#990000">Your_private_key</b>" ]'])
    self.save()

    if not sign:
      return -1

    if self.ticketsSold >= MIN_TICKETS_SOLD and not self.feeWasSendback:
      Dash.sendtoaddress(self.addressProject, str(PAYMENT_AMOUNT))
      self.feeWasSendback = True
      self.save()

      html_message = render_to_string(
        'baseEmail.html',
        {
          'message': 'Your raffle has finished. Now, you\'ve to retrive the prize accumulated by your raffle, clicking on the link below, and send it to the winner and to your wallet. Moreover, we have sent you back the 0.1 Dash you paid as fee. <br> <br> <a class="btn btn-primary" href="%s/raffle/%d/finished">Withdraw funds</a>'%( DEFAULT_DOMAIN, self.pk) ,
          'title':  'Your raffle, %s, has ended.'%self.name,
        }
      )
      EmailThread(subject="The raffle %s has finished"%self.name, 
                  message="Your raffle has finished. Now, you've to retrive the prize accumulated by your raffle and send it to the winner and to your wallet. Moreover, we have send you back the 0.1 Dash you pay as fee.",
                  html_message=html_message,
                  recipient_list=[self.owner.email]).start()
                  
    else:
      html_message = render_to_string(
        'baseEmail.html',
        {
          'message': 'Your raffle has finished. Now, you\'ve to retrive the prize accumulated by your raffle, clicking on the link below, and send it to the winner and to your wallet. <br> <br> <a class="btn btn-primary" href="%s/raffle/%d/finished">Withdraw funds</a>'%( DEFAULT_DOMAIN, self.pk) ,
          'title':  'Your raffle, %s, has ended.'%self.name,
        }
      )
      EmailThread(subject="The raffle %s has finished"%self.name, 
                  message="Your raffle has finished. Now, you've to retrive the prize accumulated by your raffle and send it to the winner and to your wallet.",
                  html_message=html_message,
                  recipient_list=[self.owner.email]).start()

    # transaction = Dash.sendrawtransaction(sign['hex'], allowhighfees="true")
    return -1

  def prueba(self):
      html_message = render_to_string(
        'baseEmail.html',
        {
          'message': 'Your raffle has finished. Now, you\'ve to retrive the prize accumulated by your raffle, clicking on the link below, and send it to the winner and to your wallet. Moreover, we have sent you back the 0.1 Dash you paid as fee. <br> <br> <a class="btn btn-primary" href="%s/raffle/%d/finished">Withdraw funds</a>'%( DEFAULT_DOMAIN, self.pk) ,
          'title':  'Your raffle, %s, has ended.'%self.name,
        }
      )
      EmailThread(subject="The raffle %s has finished"%self.name, 
                  message="Your raffle has finished. Now, you've to retrive the prize accumulated by your raffle and send it to the winner and to your wallet. Moreover, we have send you back the 0.1 Dash you pay as fee.",
                  html_message=html_message,
                  recipient_list=["carlos.25896@gmail.com"]).start()
  def __send(self):
    #print("2))))    ", self.isMultisigned)
    if self.isMultisigned:
      self.__signMultisignedTransaction()
    else:
      prize = Dash.getaddressbalance([self.addressPrize])['balance']/100000000
      transaction = Dash.sendtoaddress(self.winnerAddress, prize if type(prize) == str else str(prize))
          
      if transaction:
        self.transaction = transaction
        self.save()



  def getWinner(self):
    if self.winnerAddress:
      if self.transaction or self.commandSignRawTx:
        return self.winnerAddress
      else:
        self.__send()
        return
    count = Dash.getblockcount()
    self.getTransactions()
    tickets = 0
    allTransactions = self.transactions.all()
    for tx in allTransactions:
      tickets += tx.boughtTicket

    self.ticketsSold = tickets
    self.save()

    if self.finished:
      txArray = []
      
      for tx in allTransactions:
        for i in range(0, tx.boughtTicket):
          txArray.append(tx)
      
      if txArray:
        random.shuffle(txArray)
        self.blockHeight = Dash.getblockcount()
        data = Dash.getblockhash(self.blockHeight)
      
        if data is not None:
          blockHash = int(data, 16)
          winnerIndex = blockHash % len(txArray)
          winnerTx = txArray[winnerIndex]
          self.winner = winnerTx.user
          if self.winner.username == "Anonymous" or self.winner.wallet_address is None:
            rawtx1 = Dash.getrawtransaction(winnerTx.address)
            for vin in rawtx1['vin']:
              rawtx2 = Dash.getrawtransaction(vin['txid'])
              for vout in rawtx2['vout']:
                for address in vout["scriptPubKey"]["addresses"]:
                  txids = Dash.getaddresstxids([address])
                  if winnerTx.address in txids:
                    self.winnerAddress = address
                    break
                if winnerTx.address in txids:
                  break
              if self.winnerAddress:
                break
            if not self.winnerAddress:
              print("Winner address not found")
              return
          else:
            self.winnerAddress = self.winner.wallet_address
          
          self.save()
          self.__send()
          # if self.transaction:
            # users = { tx.user for tx in allTransactions }
            # for user in users:
            #     #print(user)
            #     if user.email == "anonymous@admin.com":
            #         continue
            #     elif user.pk != self.winner.pk:
            #         sendEmailLoser(user)
            #     else:
            #         sendEmailWinner(user, self.name, amount)


