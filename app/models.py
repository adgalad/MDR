import json
import random
import threading

from subprocess import check_output 
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.mail import send_mail

from raffle.settings import DASH_CLI, RPC_SERVER, RPC_PORT, RPC_USER, RPC_PASSWORD, DEFAULT_FROM_EMAIL
# Create your models here.

class EmailThread(threading.Thread):
    def __init__(self, subject, message, html_message, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        self.html_message = html_message
        threading.Thread.__init__(self)

    def run (self):
        send_mail(subject=self.subject,
                  message=self.message,
                  html_message=self.html_message,
                  from_email=DEFAULT_FROM_EMAIL,
                  recipient_list=self.recipient_list)

def sendEmailLoser(user):
    plain_message = "You didn't win the raffle."
    html_message = "You didn't win the raffle."
    EmailThread(subject="Verificación de correo electrónico",
                  message=plain_message,
                  html_message=html_message,
                  recipient_list=[user.email]).start()

def sendEmailWinner(user, name, amount):
    plain_message = "You won the <b> name <b> raffle. The prize is " + str(amount)
    html_message  = "You won the <b> name <b> raffle. The prize is " + str(amount)
    EmailThread(subject="Verificación de correo electrónico",
                message=plain_message,
                html_message=html_message,
                recipient_list=[user.email]).start()


def call(args):

    try:
        command = ([DASH_CLI] +
                (["-rpcconnect="+RPC_SERVER] if RPC_SERVER else []) +
                (["-rpcport="+RPC_PORT] if RPC_PORT else []) +
                (["-rpcuser="+RPC_USER] if RPC_USER else []) +
                (["-rpcpassword="+RPC_PASSWORD] if RPC_PASSWORD else []) +
                 ["-testnet"] + args)

        print("Command: ", ' '.join(command))
        data = check_output(command)
        try:
            print("string")
            data = json.loads(data)
        except:
            if type(data) == bytes:
                print("byte")
                data = data.decode("utf-8")
            else:
                print("other")
                data = str(data)
        print(">>", data)
        return data
    except Exception as e:
        print(e)
        return None

class MyUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('verified', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text=('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text=(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    
    email = models.EmailField(unique=True, null=True)
    is_superuser = models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')
    username     = models.CharField(unique=True, max_length=64, verbose_name='Username')
    verified     = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    wallet_address = models.CharField(null=True, unique=True, max_length=64, verbose_name='Wallet Address')
    signature = models.CharField(null=True, unique=True, max_length=128, verbose_name='Signature')
    message = models.CharField(null=True, unique=True, max_length=128, verbose_name='Message')
    final_message = models.CharField(null=True, unique=True, max_length=128, verbose_name='Message')


    USERNAME_FIELD = 'email'
    objects = MyUserManager()


    def __str__(self):
        return self.username

    def get_username(self):
        return self.username

    def get_short_name(self):
        return self.username
    # @property
    # def id_back_url(self):
    #     if self.id_back and hasattr(self.id_back, 'url'):
    #         return self.id_back.url
    #     else:
    #         return '/static/images/placeholder.png'


class Transaction(models.Model):
    address = models.CharField(max_length=100, primary_key=True)
    user   = models.ForeignKey(User, related_name="transactions")
    amount = models.DecimalField(max_digits=20, decimal_places=6)
    raffle = models.ForeignKey("Raffle", related_name="transactions")
    blockHeight = models.IntegerField(verbose_name="Block Height")
    boughtTicket = models.IntegerField(verbose_name="Bought Tickets")
    
    def __str__(self):
        return self.address

class RaffleSigner(models.Model):
    user = models.ForeignKey(User)
    raffle = models.ForeignKey("Raffle")
    signed = models.BooleanField(default=False)
    class Meta():
        auto_created=True
        
class Raffle(models.Model):
    name = models.CharField(verbose_name="Raffle Name", max_length=100, unique=True)
    addressPrize = models.CharField(verbose_name="Prize Address", blank=True, max_length=100)
    addressProject = models.CharField(verbose_name="Beneficiary Address", max_length=100)
    prizePercentage = models.FloatField(verbose_name="Prize Percentage", default=40.0)
    projectPercentage = models.FloatField(verbose_name="Project Percentage", default=50.0)
    blockHeight = models.IntegerField(verbose_name="Block Height")
    ticketsSold = models.IntegerField(verbose_name="Tickets Sold", default=0)
    ticketPrice = models.DecimalField(verbose_name="Ticket Price", max_digits=20, decimal_places=6)
    winner = models.ForeignKey(User, null=True, related_name="rafflesWon")
    owner = models.ForeignKey(User, related_name="ownsRaffles", null=True)
    winnerAddress = models.CharField(verbose_name="Winner Address", max_length=100, null=True)
    transaction = models.CharField(verbose_name="Transaction", max_length=100, null=True)
    signers = models.ManyToManyField(User, blank=True, through='RaffleSigner', verbose_name="Signers", related_name="signs")
    type_choice = ( ('Mini Raffle', 'Mini Raffle'), ('Raffle', 'Raffle'), ('Mega Raffle', 'Mega Raffle') )
    type = models.CharField(choices=type_choice, max_length=9, default='Mini Raffle', verbose_name="Type")
    isMultisig = models.BooleanField(default=False, verbose_name=" Multisign Prize address")
    signsRequired = models.IntegerField(blank=True, default=3, verbose_name="Signs Required", validators=[MaxValueValidator(6), MinValueValidator(2)])
    MSpubkey1 = models.CharField(verbose_name="Multisig Public Key 1", max_length=67, blank=True, null=True)
    MSpubkey2 = models.CharField(verbose_name="Multisig Public Key 2", max_length=67, blank=True,null=True)
    MSpubkey3 = models.CharField(verbose_name="Multisig Public Key 3", max_length=67, blank=True,null=True)
    MSpubkey4 = models.CharField(verbose_name="Multisig Public Key 4", max_length=67, blank=True,null=True)
    MSpubkey5 = models.CharField(verbose_name="Multisig Public Key 5", max_length=67, blank=True,null=True)
    MSpubkey6 = models.CharField(verbose_name="Multisig Public Key 6", max_length=67, blank=True,null=True)

    privkey1 = models.CharField(verbose_name="Private Key 1", max_length=53, null=True)
    privkey2 = models.CharField(verbose_name="Private Key 2", max_length=53, null=True)
    privkey3 = models.CharField(verbose_name="Private Key 3", max_length=53, null=True)
    privkey4 = models.CharField(verbose_name="Private Key 4", max_length=53, null=True)
    privkey5 = models.CharField(verbose_name="Private Key 5", max_length=53, null=True)
    privkey6 = models.CharField(verbose_name="Private Key 6", max_length=53, null=True)

    MSredeemScript = models.CharField(verbose_name="Multisig Redeem Script", max_length=100, null=True)
    
    def save(self, *args, **kwargs):
        print(self.isMultisigned)
        if not self.addressPrize and self.isMultisigned:
            self.createMultisigAddress()

        super(Raffle, self).save(*args, **kwargs)    

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/raffle/%i" % self.id

    @property
    def isMultisigned(self):
        for i in range(1,7):
            if not getattr(self,"MSpubkey"+str(i)):
                return False
        return True

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
        count = int(call(['getblockcount']))
        return self.blockHeight < count

    def createMultisigAddress(self):
        if self.isMultisigned:
            data = call(['createmultisig', str(self.signsRequired), json.dumps(self.getMSpubkey())])
            self.addressPrize = data['address']
            self.MSredeemScript = data['redeemScript']

    def getTransactions(self):
        for ag in self.addresses.all():
            txs = call(["getaddresstxids", json.dumps({"addresses":[ag.address]})])
                
            if txs is None:
                continue

            for i in txs:
                if Transaction.objects.filter(address=i).exists():
                    continue

                txRaw = call(["getrawtransaction", i, "1"])
                if txRaw is None:
                    continue

                blockHeight = txRaw['height']
                if blockHeight > self.blockHeight:
                    continue

                for detail in txRaw['vout']:
                    if ag.address in detail['scriptPubKey']['addresses']:
                        tickets = int(detail['value']/float(self.ticketPrice))
                        tx = Transaction(
                            address=txRaw['txid'],
                            amount=detail['value'],
                            user=ag.user,
                            blockHeight=blockHeight,
                            raffle=self,
                            boughtTicket=tickets
                        )
                        total = float(tickets*self.ticketPrice)
                        left = total
                        transaction = call([
                                    "sendtoaddress",
                                    self.addressPrize,
                                    str((total*self.prizePercentage)/100.0)
                                ])
                        left -= (total*self.prizePercentage)/100.0
                        call([
                            "sendtoaddress",
                            self.addressProject,
                            str((total*self.projectPercentage)/100.0)
                        ])
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
        print(">>>>>>>>>>")
        if self.nPrivkey() >= self.signsRequired:
            print("1: ", self.nPrivkey() >= self.signsRequired)
            txs = call(["getaddresstxids", json.dumps({"addresses":[self.addressPrize]})])
            if txs is None:
                return -1

            fee = 0.002
            scriptPubKey = None
            vout = 0
            outputs1 = []
            outputs2 = []
            for tx in txs:
                rawTx = call(['getrawtransaction', tx, "1"])
                if rawTx is None:
                    return -1
    
                for _vout in rawTx['vout']:
                    print(">>", _vout)
                    print(_vout['scriptPubKey']['type'] == 'scripthash', self.addressPrize in _vout['scriptPubKey']['addresses'])
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
            
            prize = call(['getaddressbalance', json.dumps({'addresses':[self.addressPrize]})])['balance']/100000000
            toAddress = {self.winnerAddress: round(prize-fee,6)}
            transaction = call(['createrawtransaction', json.dumps(outputs1), json.dumps(toAddress)])
            if transaction is None:
                return -1


            sign = call(['signrawtransaction', transaction.replace('\n',''), json.dumps(outputs2), json.dumps(self.getPrivkey)])
            if not sign or not "complete" in sign:
                return -1

            if not sign['complete']:
                return -1
            
            hex = sign['hex']

            transaction = call(['sendrawtransaction', sign['hex'], "true", "false", "false" ])
            if transaction:
                self.transaction = transaction
                self.save()
                return prize-fee
            else:
                self.__resetPrivkey()
            return -1

    def __send(self):
        print("2))))    ", self.isMultisigned)
        if self.isMultisigned:
            return self.__signMultisignedTransaction()
        else:
            prize = call(['getaddressbalance', json.dumps({'addresses':[self.addressPrize]})])['balance']/100000000
            transaction = call(["sendtoaddress",
                                self.winnerAddress,
                                str(6.2)
                            ])
                    
            if transaction:
                self.transaction = transaction
                self.save()
                return prize
        return -1

    def getWinner(self):
        print("Winner: ", self.winnerAddress, self.transaction)
        if self.winnerAddress:
            if self.transaction:
                return self.winnerAddress
            else:
                print("1))))")
                self.__send()
        data = call(["getblockcount"])
        count = int(data) if data else 0
        self.getTransactions()
        tickets = 0
        allTransactions = self.transactions.all()
        
        for tx in allTransactions:
            tickets += tx.boughtTicket

        self.ticketsSold = tickets
        self.save()

        if count >= self.blockHeight:
            users = []
            
            for tx in allTransactions:
                for i in range(0, tx.boughtTicket):
                    users.append(tx.user)
            
            if users:
                random.shuffle(users)
                data = call(["getblockhash", str(self.blockHeight)])
            
                if data is not None:
                    blockHash = int(data, 16)
                    winnerIndex = blockHash % len(users)
                    self.winner = users[winnerIndex]
                    self.winnerAddress = self.winner.wallet_address
                    
                    self.save()
                    amount  = self.__send()
                    if self.transaction:
                        users = { tx.user for tx in allTransactions }
                        for user in users:
                            print(user)
                            if user.pk != self.winner.pk:
                                sendEmailLoser(user)
                            else:
                                sendEmailWinner(user, self.name, amount)


class AddressGenerated(models.Model):
    user    = models.ForeignKey(User)
    raffle  = models.ForeignKey(Raffle, related_name="addresses")
    address = models.CharField(unique=True, max_length=64, verbose_name='Address')




