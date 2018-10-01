import json
import random
import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from ckeditor.fields import RichTextField

from app.dash import Dash
from app.models.User import User
from app.models.models import Transaction
    
rafflePrice = {
  'Mini Raffle':0.01,
  'Raffle': 0.05,
  'Mega Raffle': 0.1
}

class Raffle(models.Model):
  name = models.CharField(verbose_name="Raffle Name", max_length=100, unique=True)
  description = RichTextField()
  thumbnail_url = models.CharField(verbose_name="Thumbnail Image URL", blank=True, max_length=2048)
  addressPrize = models.CharField(verbose_name="Prize Address", blank=True, max_length=100)
  addressProject = models.CharField(verbose_name="Beneficiary Address", max_length=100)
  prizePercentage = models.FloatField(verbose_name="Prize Percentage", default=40.0)
  projectPercentage = models.FloatField(verbose_name="Project Percentage", default=50.0)
  drawDate = models.DateField(verbose_name="Draw date")
  ticketsSold = models.IntegerField(verbose_name="Tickets Sold", default=0)
  ticketPrice = models.DecimalField(verbose_name="Ticket Price", max_digits=20, decimal_places=6)
  winner = models.ForeignKey(User, blank=True, null=True, related_name="rafflesWon")
  owner = models.ForeignKey(User, related_name="ownsRaffles", blank=True, null=True)
  winnerAddress = models.CharField(verbose_name="Winner Address", max_length=100, blank=True, null=True)
  totalPrize = models.DecimalField(verbose_name="totalPrize", max_digits=20, decimal_places=6, blank=True, null=True)
  transaction = models.CharField(verbose_name="Transaction", max_length=100, blank=True, null=True)
  signers = models.ManyToManyField(User, blank=True, through='RaffleSigner', verbose_name="Signers", related_name="signs")
  type_choice = ( ('Mini Raffle', 'Mini Raffle'), ('Raffle', 'Raffle'), ('Mega Raffle', 'Mega Raffle') )
  type = models.CharField(null=True, blank=True, choices=type_choice, max_length=16, default='Mini Raffle', verbose_name="Type")
  blockHeight = models.IntegerField(verbose_name="Block Height", default=0)
  isMultisig = models.BooleanField(default=True, verbose_name=" Multisign Prize address")
  signsRequired = models.IntegerField(blank=True, default=3, verbose_name="Signs Required", validators=[MaxValueValidator(6), MinValueValidator(1)])

  MSpubkey1 = models.CharField(verbose_name="Multisig Public Key 1", max_length=67, blank=True, null=True)
  MSpubkey2 = models.CharField(verbose_name="Multisig Public Key 2", max_length=67, blank=True, null=True)
  MSpubkey3 = models.CharField(verbose_name="Multisig Public Key 3", max_length=67, blank=True, null=True)
  MSpubkey4 = models.CharField(verbose_name="Multisig Public Key 4", max_length=67, blank=True, null=True)
  MSpubkey5 = models.CharField(verbose_name="Multisig Public Key 5", max_length=67, blank=True, null=True)
  MSpubkey6 = models.CharField(verbose_name="Multisig Public Key 6", max_length=67, blank=True, null=True)

  privkey1 = models.CharField(verbose_name="Private Key 1", max_length=53, blank=True, null=True)
  privkey2 = models.CharField(verbose_name="Private Key 2", max_length=53, blank=True, null=True)
  privkey3 = models.CharField(verbose_name="Private Key 3", max_length=53, blank=True, null=True)
  privkey4 = models.CharField(verbose_name="Private Key 4", max_length=53, blank=True, null=True)
  privkey5 = models.CharField(verbose_name="Private Key 5", max_length=53, blank=True, null=True)
  privkey6 = models.CharField(verbose_name="Private Key 6", max_length=53, blank=True, null=True)

  MSredeemScript = models.CharField(verbose_name="Multisig Redeem Script", max_length=100, blank=True, null=True)
  
  def save(self, *args, **kwargs):
    #print(self.isMultisigned)
    if not self.addressPrize and self.isMultisigned:
      self.createMultisigAddress()

    super(Raffle, self).save(*args, **kwargs)    

  @property
  def getPrice(self):
    return rafflePrice[self.type]

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
  def getDate(self):
    
    if self.winnerAddress:
      count = self.blockHeight
      blockHash = Dash.getblockhash(count)
      blockTime = Dash.getblock(blockHash)['time']
      date = datetime.datetime.fromtimestamp(blockTime)
    else:
      count = Dash.getblockcount()
      blockHash = Dash.getblockhash(count)
      blockTime = Dash.getblock(blockHash)['time']
      date = datetime.datetime.fromtimestamp(blockTime + (self.blockHeight-count) * (2.6*60))
    return date
  
  @property
  def finished(self):
    count = Dash.getblockcount()
    return self.blockHeight < count

  def createMultisigAddress(self):
    if self.isMultisigned:
      data = Dash.createmultisig(str(self.signsRequired), json.dumps(self.getMSpubkey()))
      self.addressPrize = data['address']
      self.MSredeemScript = data['redeemScript']

  def getTransactions(self):
    for addressGenerated in self.addresses.all():
      txs = Dash.getaddresstxids([addressGenerated.address])
      if txs is None:
        continue

      for i in txs:
        if Transaction.objects.filter(address=i).exists():
          continue

        txRaw = Dash.getrawtransaction(i)
        if txRaw is None:
          continue

        blockHeight = txRaw['height']
        if blockHeight > self.blockHeight:
          continue

        for detail in txRaw['vout']:
          if addressGenerated.address in detail['scriptPubKey']['addresses']:
            tickets = int(detail['value']/float(self.ticketPrice))
            tx = Transaction(
              address=txRaw['txid'],
              amount=detail['value'],
              user=addressGenerated.user,
              blockHeight=blockHeight,
              raffle=self,
              boughtTicket=tickets
            )
            total = float(tickets*self.ticketPrice)
            left = total
            transaction = Dash.sendtoaddress(
              self.addressPrize,
              str((total*self.prizePercentage)/100.0)
            )

            left -= (total*self.prizePercentage)/100.0
            Dash.sendtoaddress(
              self.addressProject,
              str((total*self.projectPercentage)/100.0)
            )

            left -= (total*self.projectPercentage)/100.0
            tx.save()

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

  def __resetPrivkey(self):
    for i in range(1, self.signsRequired + 1):
      setattr(self, "privkey"+str(i), None)
    self.save()
  
  def nPrivkey(self):
    n = 0
    for i in range(1, self.signsRequired + 1):
      if getattr(self, "privkey"+str(i)):
        n += 1
    return n


  def __signMultisignedTransaction(self):
    #print(">>>>>>>>>>")
    if self.nPrivkey() >= self.signsRequired:
      #print("1: ", self.nPrivkey() >= self.signsRequired)
      txs = Dash.getaddresstxids([self.addressPrize])
      if txs is None:
        return -1

      fee = 0.002
      scriptPubKey = None
      vout = 0
      outputs1 = []
      outputs2 = []
      for tx in txs:
        rawTx = Dash.getrawtransaction(tx)
        if rawTx is None:
          return -1
  
        for _vout in rawTx['vout']:
          #print(">>", _vout)
          #print(_vout['scriptPubKey']['type'] == 'scripthash', self.addressPrize in _vout['scriptPubKey']['addresses'])
          if _vout['scriptPubKey']['type'] == 'scripthash' and self.addressPrize in _vout['scriptPubKey']['addresses']:
            scriptPubKey = _vout['scriptPubKey']['hex']
            vout = _vout['n']
            break

        txData = {
          "txid": tx,
          "vout": vout
        }

        outputs1.append({"txid": tx, "vout": vout})

        outputs2.append({"txid": tx, 
                 "vout": vout,
                 "scriptPubKey": scriptPubKey,
                 "redeemScript": self.MSredeemScript})
      
      prize = Dash.getaddressbalance([self.addressPrize])['balance']/100000000
      toAddress = {self.winnerAddress: round(prize-fee,6)}
      transaction = Dash.createrawtransaction(outputs1, toAddress)
      if transaction is None:
        return -1


      sign = Dash.signrawtransaction(transaction.replace('\n',''), outputs2, self.getPrivkey)
      if not sign or not "complete" in sign:
        return -1

      if not sign['complete']:
        return -1
      
      hex = sign['hex']

      transaction = Dash.sendrawtransaction(sign['hex'], allowhighfees="true")
      if transaction:
        self.transaction = transaction
        self.save()
        return prize-fee
      else:
        self.__resetPrivkey()
      return -1

  def __send(self):
    #print("2))))    ", self.isMultisigned)
    if self.isMultisigned:
      return self.__signMultisignedTransaction()
    else:
      prize = Dash.getaddressbalance([self.addressPrize])['balance']/100000000
      transaction = Dash.sendtoaddress(self.winnerAddress, prize if type(prize) == str else str(prize))
          
      if transaction:
        self.transaction = transaction
        self.save()
        return prize
    return -1

  def getWinner(self):
    if self.winnerAddress:
      if self.transaction:
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

    if count >= self.blockHeight:
      txArray = []
      
      for tx in allTransactions:
        for i in range(0, tx.boughtTicket):
          txArray.append(tx)
      
      if txArray:
        random.shuffle(txArray)
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
          amount  = self.__send()
          self.totalPrize = amount
          self.save()
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
