import json
from subprocess import check_output 

from raffle.settings import DASH_CLI, RPC_SERVER, RPC_PORT, RPC_USER, RPC_PASSWORD, DEFAULT_FROM_EMAIL

class Dash:
  command = ([DASH_CLI] +
        (["-rpcconnect="+RPC_SERVER] if RPC_SERVER else []) +
        (["-rpcport="+RPC_PORT] if RPC_PORT else []) +
        (["-rpcuser="+RPC_USER] if RPC_USER else []) +
        (["-rpcpassword="+RPC_PASSWORD] if RPC_PASSWORD else [])) #+
         #["-testnet"])
  
  @staticmethod
  def createrawtransaction(output, addressAmount):
    return Dash.call(["createrawtransaction",json.dumps(output), json.dumps(addressAmount)])
  
  @staticmethod  
  def createmultisig(signsRequired, pubkeys):
    d = Dash.call(["createmultisig", str(signsRequired), json.dumps(pubkeys)])
    return d
    # return {
    #   'address': 'asdasdasd',
    #   'redeemScript':'asdasdsdasd'
    # }

  
  @staticmethod
  def dumpprivkey(address):
    return Dash.call(["dumpprivkey", address]).replace('\n','')    
    # return address
  
  @staticmethod
  def getaddresstxids(addresses):
    return Dash.call(["getaddresstxids", json.dumps({"addresses":addresses})])
  
  @staticmethod
  def getaddressbalance(addresses):
    return Dash.call(["getaddressbalance",json.dumps({'addresses':addresses})])
    # return {'received':100}
  
  @staticmethod
  def getblock(blockHash):
    return Dash.call(["getblock", blockHash])
    # return {'time':5515236123}
  
  @staticmethod
  def getblockcount():
    count = Dash.call(['getblockcount'])
    return int(count) if count else 0
  
  @staticmethod
  def getblockhash(count):
    return Dash.call(["getblockhash", str(count)])
  
  @staticmethod  
  def getnewaddress():
    return Dash.call(["getnewaddress"]).replace('\n','')
    # return 'XaSDASDAXASFSDFWEDCSSD'
  
  @staticmethod
  def getrawmempool(verbose='false'):
    return Dash.call(['getrawmempool', verbose])
    
  @staticmethod
  def getrawtransaction(address, parsed=1):
    return Dash.call(["getrawtransaction", address, str(parsed)])
    # return {'time': 5566462526}

  @staticmethod
  def gettransaction(address):
    return Dash.call(["gettransaction", address])
    # return {'time': 5566462526}

  @staticmethod
  def importpubkey(pubkey, label='', rescan='false'):
    return Dash.call(["importpubkey", '%s'%pubkey, '"%s"'%label, rescan])
  
  @staticmethod
  def sendrawtransaction(hexadecimalValue, allowhighfees=False, instantsend=False, bypasslimits=False):
    return Dash.call(["sendrawtransaction",hexadecimalValue, json.dumps(allowhighfees), json.dumps(instantsend), json.dumps(bypasslimits)])  
  
  @staticmethod  
  def sendtoaddress(address, amount):
    return Dash.call(["sendtoaddress", address, str(amount)])
  
  @staticmethod
  def signrawtransaction(transaction, output, privkeys):
    return Dash.call(["signrawtransaction",transaction, json.dumps(output), json.dumps(privkeys)])  
  
  @staticmethod
  def validateaddress(address):
    return Dash.call(['validateaddress', address])
  
  @staticmethod
  def verifymessage(address, signature, finalMessage):
    return Dash.call(["verifymessage", address, signature, finalMessage])


  @staticmethod
  def call(args):
    try:
      #print(' '.join(Dash.command + args))
      data = check_output(Dash.command + args)
      try:
        data = json.loads(data.decode("utf-8"))
      except:
        if type(data) == bytes:
          data = data.decode("utf-8")
        else:
          data = str(data)
      return data
    except Exception as e:
      print(e)
      return None
