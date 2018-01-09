import re
import math
import discord
import asyncio
import platform
import requests
import mysql.connector
from discord.ext import commands
from discord.ext.commands import Bot
from mysql.connector import errorcode
#explorerURL = "http://explorer.grlc-bakery.fun/"
explorerURL = "http://explorer.garlicoin.io/"
r = requests.get(url=explorerURL+'api/getnetworkhashps')
khs = float(r.json())
client = Bot(description="Garlic Bread Bot by Puffycheeses#9541", command_prefix="!!", pm_help = True) # Initialise the Bot
cnx = mysql.connector.connect(user='root', password='1234',host='127.0.0.1',database='garliko') # Security is my no.1 Priority
cursor = cnx.cursor()
CreateUserQuery = ("INSERT INTO balances (username, balance) VALUES (%s, %s)")
CheckUserQuery = ("SELECT * FROM balances WHERE username = %s")
CheckCoinQuery = ("SELECT sum( balance ) FROM `balances`")
SetAddressQuery = ("INSERT INTO addresses (username, address) VALUES (%s, %s)")
UpdateAddressQuery = ("UPDATE addresses SET address = %s WHERE username = %s")
GetAddressQuery = ("SELECT * FROM addresses WHERE username = %s")
@client.event
async def on_ready():
    print('Logged in as '+client.user.name+' (ID:'+client.user.id+') | Connected to '+str(len(client.servers))+' servers | Connected to '+str(len(set(client.get_all_members())))+' users')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    await updateHashRate()
@client.event
async def on_message(message):
    global errorMessage
    errorMessage = "lol "+str(message.author)+" retarded"
    server = message.server # Set the server depending on where the message came fromS
    if message.content.startswith('!!help'):
        await help(message, server)
    #elif message.content.startswith('!!bal'):
        #await Checkbalance(message, server, message.author)
    #elif message.content.startswith('!!addBal') and str(message.author) == 'Puffycheeses#9541':
        #await addBalance(message, server)
    #elif message.content.startswith('!!tip'):
        #await tip(message, server)
    #elif message.content.startswith('!!topup'):
        #await client.send_message(message.author, 'This feature is currently in development. Sorry for any inconvenience')
    #elif message.content.startswith('!!withdraw'):
        #await client.send_message(message.author, 'This feature is currently in development. Sorry for any inconvenience')
    elif message.content.startswith('!!total'):
        await total(message)
    elif message.content.startswith('!!hashrate'):
        await showHashRate(message)
    elif message.content.startswith('!!address'):
        await checkAddress(message)
    elif message.content.startswith('!!setaddress'):
        await setaddress(message)
    elif message.content.startswith('!!myaddress'):
        await checkmyaddress(message)
    elif message.content.startswith('!!son'):
        if str(message.author) == 'Puffycheeses#9541':
            await client.send_message(message.channel, 'Papi')
        else:
            await client.send_message(message.channel, 'Ur not my dad')
    elif message.content.startswith('!!explorer'):
        await client.send_message(message.channel, 'I am currently using '+explorerURL+ ' to get my information')
# Commands as functions for easier and nicer editing
async def help(message, server):
    await client.send_message(message.author, '\n**Garlicoin Bot Help** - Version *0.8* __Puffycheeses__\n\nGRLC Commands:\n\t~~!!bal - Check your balance~~\n\t~~!!tip <user> <ammount> - Tip a user GRLC~~\n\t!!hashrate - Show the networks hash rate\n\t!!address <address> - Check an addresses balance, sent and last block\n\t!!setaddress <address> - Set your address\n\t!!myaddress - View the balance, sent and last block of your set address\n\nGeneral Commands:\n\t!!help - Show help\n\t!!topup - Top up your tipping account\n\t~~!!withdraw - Withdraw to a garlicoin address~~\n\t!!explorer - See what explorer I\'m using')
    try:
        await client.delete_message(message)
        print("Requested help")
    except:
        print("PM command")
async def Checkbalance(message, server, user):
    author = user
    user = (str(author),)
    cursor.execute(CheckUserQuery, (user))
    rows = cursor.fetchone()
    if rows:
        balance = str(rows[2])
        await client.send_message(message.channel, author.mention+", Your balance is "+u"\U0001F171"+" "+balance+" GRLC")
    else:
        cursor.execute(CreateUserQuery, (str(message.author), 0))
        cnx.commit()
        await client.send_message(message.channel, author.mention+", Your balance is "+u"\U0001F171"+" 0 GRLC")
    try:
        await client.delete_message(message)
    except:
        print("PM command")
def SilentCheckbalance(message, user):
    author = user
    user = (str(author),)
    cursor.execute(CheckUserQuery, (user))
    rows = cursor.fetchone()
    if rows:
        balance = str(rows[2])
        return float(balance)
    else:
        cursor.execute(CreateUserQuery, (str(author), 0))
        cnx.commit()
        return 0
def SilentCheckAddress(message):
    author = str(message.author)
    user = (str(author),)
    cursor.execute(GetAddressQuery, (user))
    rows = cursor.fetchone()
    if rows:
        print("Name exists")
        return False
    else:
        print("Name does not exist")
        return True
async def updateHashRate():
    await client.change_presence(game=discord.Game(name=convert_size(khs)+'| !!help'))
    print('Hash rate updated')
async def addBalance(message, server):
    User = message.mentions[0]
    SilentCheckbalance(message, User)
    AddBalance = float(message.content[len('!!addBal'+User.mention)+2:])
    print("Added "+str(AddBalance)+" to "+str(User))
    author = message.author
    cursor.execute("UPDATE balances SET balance=balance+%s WHERE username = %s", (AddBalance, str(User)))
    cnx.commit()
async def tip(message, server):
    try:
        author = message.author
        user = message.mentions[0]
        tipAmmount = float(message.content[len('!!tip'+user.mention)+1:])
        delMsg = await client.send_message(message.channel, 'Please type `!!confirm` to confirm the transaction or wait 15 seconds to cancel')
        msg = await client.wait_for_message(author=message.author, content='!!confirm', timeout=15)
        if msg:
            if SilentCheckbalance(message, str(author)) >= tipAmmount:
                SilentCheckbalance(message, str(user))
                cursor.execute("UPDATE balances SET balance=balance-%s WHERE username = %s", (tipAmmount, str(author)))
                cursor.execute("UPDATE balances SET balance=balance+%s WHERE username = %s", (tipAmmount, str(user)))
                await client.send_message(message.channel, author.mention+", You tipped "+user.mention+""+u"\U0001F171"+" "+str(tipAmmount)+" GRLC")
                cnx.commit()
            else:
                await client.send_message(message.channel, author.mention+", You do not have enough GRLC to do this")
            await client.delete_message(msg)
        else:
            await client.send_message(message.channel, 'Transaction canceled')
        await client.delete_message(delMsg)
        print('Tip')
    except:
        print(errorMessage)
async def total(message):
    cursor.execute(CheckCoinQuery)
    rows = cursor.fetchone()
    await client.send_message(message.channel, 'I currenty account for '+str(rows[0])+' Garlicoin in cirulation')
    print('total')
async def showHashRate(message):
    r = requests.get(url=explorerURL+'api/getnetworkhashps')
    khs = float(r.json())
    await client.change_presence(game=discord.Game(name=convert_size(khs)+' | !!help'))
    await client.send_message(message.channel, 'The current network hashrate is '+convert_size(khs))
    print('show hash rate')
async def checkAddress(message):
    try:
        address = message.content[len('!!address')+1:]
        addressAPI = requests.get(explorerURL+"ext/getaddress/"+address)
        addressJSON = addressAPI.json()
        try:
            await client.send_message(message.channel, '__**'+address+':**__\n**Balance:** '+str(addressJSON['balance'])+"\n**Sent**: "+str(addressJSON['sent'])+"\n**Last txs**: "+str(addressJSON['last_txs'][0]['addresses']))
        except:
            await client.send_message(message.channel, 'That isnt a valid address!\nIf you think this is wrong make sure you have a transaction (mining/trading) on the account')
        print('check address')
    except:
        print(errorMessage)
async def setaddress(message):
    try:
        Setaddress = message.content[len('!!setaddress')+1:]
        SetaddressAPI = requests.get(explorerURL+"ext/getaddress/"+Setaddress)
        SetaddressJSON = SetaddressAPI.json()
        try:
            print(str(SetaddressJSON['balance']))
        except:
            await client.send_message(message.channel, 'That isnt a valid address!\nIf you think this is wrong make sure you have a transaction (mining/trading) on the account')
            return
        if SilentCheckAddress(message):
            userTag = re.sub(r'.*#', '#',str(message.author))
            cursor.execute(SetAddressQuery, (userTag, Setaddress))
            await client.send_message(message.channel, 'You can now check your address with `!!myaddress`')
            cnx.commit()
        else:
            cursor.execute(UpdateAddressQuery, (Setaddress, userTag))
            await client.send_message(message.channel, 'You have updated your address and can now check it with `!!myaddress`')
            cnx.commit()
        print('set address')
    except:
        print(errorMessage)
async def checkmyaddress(message):
    author = re.sub(r'.*#', '#',str(message.author))
    user = (str(author),)
    cursor.execute(GetAddressQuery, (user))
    rows = cursor.fetchone()
    if rows:
        address = str(rows[2])
        addressAPI = requests.get(explorerURL+"ext/getaddress/"+address)
        addressJSON = addressAPI.json()
        try:
            await client.send_message(message.channel, '__**'+address+':**__\n**Balance:** '+str(addressJSON['balance'])+"\n**Sent**: "+str(addressJSON['sent'])+"\n**Last txs**: "+str(addressJSON['last_txs'][0]['addresses']))
        except:
            await client.send_message(message.channel, 'That isnt a valid address!\nIf you think this is wrong make sure you have a transaction (mining/trading) on the account')
    else:
        await client.send_message(message.channel, 'You havent set your address with `!!setaddress`')
    print('check my address')
def convert_size(size_bytes): #Vilsol
   if size_bytes == 0:
       return "0H/s"
   size_name = ("H/s", "KH/s", "MH/s", "GH/s", "TH/s", "PH/s", "EH/s", "ZH/s", "YH/s")
   i = int(math.floor(math.log(size_bytes, 1000)))
   s = round(size_bytes / math.pow(1000, i), 2)
   return "%s %s" % (s, size_name[i])
client.run('Key')
