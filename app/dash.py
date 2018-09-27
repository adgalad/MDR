import json
from subprocess import check_output 

from raffle.settings import DASH_CLI, RPC_SERVER, RPC_PORT, RPC_USER, RPC_PASSWORD, DEFAULT_FROM_EMAIL

class Dash:
  command = ([DASH_CLI] +
        (["-rpcconnect="+RPC_SERVER] if RPC_SERVER else []) +
        (["-rpcport="+RPC_PORT] if RPC_PORT else []) +
        (["-rpcuser="+RPC_USER] if RPC_USER else []) +
        (["-rpcpassword="+RPC_PASSWORD] if RPC_PASSWORD else []) +
         ["-testnet"])
  
  @staticmethod
  def createrawtransaction(output, addressAmount):
    return Dash.call(["createrawtransaction",json.dumps(output), json.dumps(addressAmount)])
  
  @staticmethod  
  def createmultisig(signsRequired, pubkeys):
    return Dash.call(["createmultisig", str(signsRequired), json.dumps(pubkeys)])
  
  @staticmethod
  def dumpprivkey(address):
    return Dash.call(["dumpprivkey", address]).replace('\n','')    
  
  @staticmethod
  def getaddresstxids(addresses):
    return Dash.call(["getaddresstxids", json.dumps({"addresses":addresses})])
  
  @staticmethod
  def getaddressbalance(addresses):
    return {'received':100}
    return Dash.call(["getaddressbalance",json.dumps({'addresses':addresses})])
  
  @staticmethod
  def getblock(blockHash):
    return {'time':5515236123}
    return Dash.call(["getblock", blockHash])
  
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
  
  @staticmethod
  def getrawtransaction(address, parsed=1):
    return Dash.call(["getrawtransaction", address, parsed])
  
  @staticmethod
  def sendrawtransaction(hexadecimalValue, allowhighfees=False, instantsend=False, bypasslimits=False):
    return Dash.call(["sendrawtransaction",hexadecimalValue, allowhighfees, instantsend, bypasslimits])  
  
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
      #print("Command: ", ' '.join(command))
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
      #print(e)
      return None