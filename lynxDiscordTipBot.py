#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import subprocess
import requests
import logging
import discord, asyncio
from discord.ext import commands
import re
import time

''' begin configuration section '''

BOTNAME  = '____CHANGEME____'
BOTUUID  = '____CHANGEME____'
BOTCHID  = '____CHANGEME____'
TOKEN    = '____CHANGEME____'
LOG_FILE = '____CHANGEME____'
APP_EXE  = '____CHANGEME____'

''' end configuration section '''



''' DO NOT EDIT BELLOW THS LINE '''

fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.INFO)
ft = logging.Formatter('%(asctime)-15s - %(message)s')
fh.setFormatter(ft)

logger = logging.getLogger(BOTNAME)
logger.setLevel(logging.INFO)
logger.addHandler(fh)

bot = commands.Bot(command_prefix='!') 
bot.remove_command('help')


def main():
    bot.run(TOKEN)


@bot.command(pass_context=True)
async def help(ctx):
    text = ctx.message.content
    name = ctx.message.author.name
    uuid = ctx.message.author.id

    n="The following commands are at your disposal:"
    v="!info, !balance, !deposit, !withdraw, !tip, !rain and !price"
    msg = discord.Embed(color=0x00b3b3)
    msg.add_field(name=n, value=v, inline=False)
    
    await bot.say(embed=msg)


@bot.command(pass_context=True)
async def info(ctx):
    uuid = ctx.message.author.id
    name = ctx.message.author.name

    msg = \
    """
      ```
                  INFO SECTION
      ```
      commands like *!tip* & *!withdraw* have a specfic format,\
    use them like so:
     
     Tipping format: 
       `!tip @[user] [amount]        (without brackets)`
       
     Rain format: 
       `!rain [amount]               (without brackets)`
          
     Withdrawing format: 
       `!withdraw [address] [amount] (without brackets)`


        WHERE:
            `[address] = withdraw #LYNX address`
            `[user] = discord username`
            `[amount] = amount of #lynx to utilise`

     *NOTE*:
      - don't deposit a significant amount of #LYNX through this #BOT
      - make sure that you enter a valid #LYNX address when you perform a withdraw
      - we are not responsible of your funds if something bad happen to this #BOT 
     ```
          USE THIS #BOT AT YOUR OWN RISK
     ```

    """

    embed = discord.Embed(color=0x00b3b3)
    embed.add_field(name="\a", value=msg, inline=False)

    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def balance(ctx):
    user_name = ctx.message.author.name
    user_uuid = ctx.message.author.id

    if user_name is None:
        msg = "Invalid username!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False
    if user_uuid is None:
        msg = "Invalid userid!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    cmd = [
        APP_EXE, 
        '-rpcuser=bitcoin',
        '-rpcpassword=local321', 
        'getbalance',
        str(user_uuid)
    ]
    ret = rpc_call(cmd)
    if ret is None:
        msg = 'rpc internal error!'
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    balance = float(ret)
    balance = str('{:,.8f}'.format(balance))

    msg = '@{0} your current balance is: {1} LYNX'.format(user_name, balance)
    embed = discord.Embed(color=discord.Color.green())
    embed.add_field(name="BALANCE", value=msg, inline=True)

    await bot.send_message(ctx.message.author, embed=embed)
    #await bot.say(embed=embed)


@bot.command(pass_context=True)
async def deposit(ctx):
    user_name = ctx.message.author.name
    user_uuid = ctx.message.author.id

    if user_name is None:
        msg = "Invalid username!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False
    if user_uuid is None:
        msg = "Invalid userid!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    cmd = [
        APP_EXE, 
        '-rpcuser=bitcoin',
        '-rpcpassword=local321', 
        'getaccountaddress',
        str(user_uuid)
    ] 
    ret = rpc_call(cmd)
    if ret is None:
        msg = 'rpc internal error!'
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    msg = '@{} your depositing address is: {}'.format(user_name, ret)
    embed = discord.Embed(color=discord.Color.green())
    embed.add_field(name="DEPOSIT", value=msg, inline=True)

    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def tip(ctx):
    user_name = ctx.message.author.name
    user_uuid = ctx.message.author.id

    if user_name is None:
        msg = "Invalid username!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False
    if user_uuid is None:
        msg = "Invalid userid!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False
    
    message = ctx.message.content.split(' ')
    if len(message) != 3:
        msg = "Please use !tip <username> <amount>!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    if not isValidUsername(message[1]):
        msg = "Please input a valid username (ex: @JonDoe01#0964)!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False
    if not isValidAmount(message[2]):
        msg = "Please input a valid amount (ex: 1000)!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    amount = float(message[2])
    target = message[1]
    uuid = list(filter(str.isdigit, target))
    target_uuid = str(''.join(uuid))

    if amount > 100000:
        msg = "Please send a lower amount (max: 100,000 LYNX)!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False
    if target_uuid == user_uuid:
        msg = "You can't tip yourself silly!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False
    if target_uuid == BOTUUID:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value="HODL.", inline=True)
        await bot.say(embed=embed)
        return False
    if not target_uuid:
        msg = '@{} has no activity in this chat!'.format(target)
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    cmd = [
        APP_EXE, 
        '-rpcuser=bitcoin',
        '-rpcpassword=local321', 
        'getbalance',
        str(user_uuid)
    ]
    ret = rpc_call(cmd)
    if ret is None:
        msg = 'rpc internal error!'
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    balance = float(ret)

    if balance < amount:
        msg = '@{0} you have insufficent funds.'.format(user_name)
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    cmd = [
        APP_EXE,
        '-rpcuser=bitcoin',
        '-rpcpassword=local321',
        'move',
        str(user_uuid),
        str(target_uuid),
        str(amount),
    ]
    tx = rpc_call(cmd)
    if tx is None:
        msg = 'rpc internal error!'
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    msg = '@{0} tipped {1} of {2} LYNX'.format(user_name, target, amount)
    embed = discord.Embed(color=discord.Color.green())
    embed.add_field(name="TIP", value=msg, inline=True)

    await bot.say(embed=embed)

    
@bot.command(pass_context=True)
async def rain(ctx):
    user_name = ctx.message.author.name
    user_uuid = ctx.message.author.id

    if user_name is None:
        msg = "Invalid username!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False
    if user_uuid is None:
        msg = "Invalid userid!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False
    
    message = ctx.message.content.split(' ')
    if len(message) != 2:
        msg = "Please use !rain <amount>!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False
    if not isValidAmount(message[1]):
        msg = "Please input a valid amount (ex: 1000)!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    amount = float(message[1])

    if amount > 100000:
        msg = "Please insert a lower amount (max: 100,000 LYNX)!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    cmd = [
        APP_EXE, 
        '-rpcuser=bitcoin',
        '-rpcpassword=local321', 
        'getbalance',
        str(user_uuid)
    ]
    ret = rpc_call(cmd)
    if ret is None:
        msg = 'rpc internal error!'
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    balance = float(ret)

    if balance < amount:
        msg = '@{0} you have insufficent funds.'.format(user_name)
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    users_online = {}
    for server in bot.servers:
      for u in server.members:
        if str(u.status) is 'online':
          users_online[u.id] = u.name

    online  = len(users_online)
    pamount = '{:,.8f}'.format(float(amount/online))

    for key in sorted(users_online):
      target_uuid = key
      target_name = users_online[target_uuid]
      cmd = [
        APP_EXE,
        '-rpcuser=bitcoin',
        '-rpcpassword=local321',
        'move',
        str(user_uuid),
        str(target_uuid),
        str(pamount),
      ]
      tx = rpc_call(cmd)
      if tx is None:
          msg = "failed to #tip @{}!".format(target_name)
          embed = discord.Embed(color=discord.Color.red())
          embed.add_field(name="ERROR", value=msg, inline=True)
          await bot.say(embed=embed)
          return False

    user_list = ",".join(users_online.values())
    msg = "{} invoked rain spell with {} LYNX over #{} users ({})"\
          .format(user_name, pamount, online, user_list)
    embed = discord.Embed(color=discord.Color.green())
    embed.add_field(name="RAIN", value=msg, inline=True)

    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def withdraw(ctx):
    user_name = ctx.message.author.name
    user_uuid = ctx.message.author.id

    if user_name is None:
        msg = "Invalid username!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False
    if user_uuid is None:
        msg = "Invalid userid!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    message = ctx.message.content.split(' ')
    if len(message) != 3:
        msg = 'Please use !withdraw <address> <amount>!'
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    if not isValidAddress(message[1]):
        msg = 'Please input a valid LYNX address!'
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False
    if not isValidAmount(message[2]):
        msg = 'Please input a valid amount (ex: 1000)!'
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    amount = float(message[2])
    address = message[1]

    cmd = [
        APP_EXE, 
        '-rpcuser=bitcoin',
        '-rpcpassword=local321', 
        'getbalance' ,
        str(user_uuid)
    ]
    ret = rpc_call(cmd)
    if ret is None:
        msg = 'rpc internal error!'
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    balance = float(ret)
    if balance < amount:
        msg = '@{0} you have insufficent funds.'.format(user_name)
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    cmd = [
        APP_EXE,
        '-rpcuser=bitcoin',
        '-rpcpassword=local321',
        'sendfrom',
        str(user_uuid),
        str(address),
        str(amount),
    ]
    tx = rpc_call(cmd)
    if tx is None:
        msg = 'rpc internal error!'
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    msg = '@{0} has successfully withdrew {2} LYNX to address: {1}'\
              .format(user_name, address, amount)
    embed = discord.Embed(color=discord.Color.green())
    embed.add_field(name="WITHDRAW", value=msg, inline=True)

    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def price(ctx):
    getmarket = 'https://chart.meanxtrade.com/info.php?market=LYNX_LTC'
    response  = requests.get(getmarket)
    json_data = response.json()

    if not json_data or json_data.get('error'):
        msg = "Failed to get data from meanxtrade.com exchange!"
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="ERROR", value=msg, inline=True)
        await bot.say(embed=embed)
        return False

    message = {}

    message['*LastPrice*'] = '{:,.8f}'.format(float(json_data['last']))
    message['*AskPrice*'] = '{:,.8f}'.format(float(json_data['lowest_ask']))
    message['*BidPrice*'] = '{:,.8f}'.format(float(json_data['highest_bid']))
    message['*Volume*'] = '{:,.8f}'.format(float(json_data['base_volume']))
    message['*High24Hr*'] = '{:,.8f}'.format(float(json_data['high_24hr']))
    message['*Low24Hr*'] = '{:,.8f}'.format(float(json_data['low_24hr']))
    message['*p%rate*'] = '{:,.8f}'.format(float(json_data['percent_change_24hr']))

    pretty_object = json.dumps(message, indent=4, sort_keys=True)
    label_market  = json_data['market']

    msg = '*meanxtrade* \[{0}]:\n{1}'.format(label_market, pretty_object)
    embed = discord.Embed(color=0x00b3b3)
    embed.add_field(name="PRICE", value=msg, inline=True)

    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def mcap(ctx):
    user_name = ctx.message.author.name
    user_uuid = ctx.message.author.id

    await bot.say('work in progress!')


@bot.command(pass_context=True)
async def moon(ctx):
    user_name = ctx.message.author.name
    user_uuid = ctx.message.author.id

    await bot.say('Moon mission inbound!')


@bot.command(pass_context=True)
async def hi(ctx):
    name = ctx.message.author.name
    uuid = ctx.message.author.id
    
    msg = 'Hello @{}[{}], how are you doing today?'.format(name, uuid)

    await bot.say(msg)


@bot.event
async def on_ready():
    print('Bot is ready for use!')


@bot.event
async def on_message(message, user: discord.Member = None):
    if message is None: return

    if user is None:
      user = message.author

    msg  = message.content
    uuid = user.id
    user = user.name

    logger.info("@{} [#{}]: {}".format(user, uuid, msg))

    cuid = str(message.channel.id)
    if cuid != BOTCHID and message.content.startswith('!'):
      logger.info("wrong #BOTCHID [@{}]".format(BOTCHID))
      await bot.delete_message(message)
    else:
      await bot.process_commands(message)



def rpc_call(cmd):
    try:
        result = subprocess.run(cmd,
            stdout=subprocess.PIPE)
    except:
        return
    ret = result.stdout.strip()
    ret = ret.decode('utf-8')
    if len(ret) == 0:
        return
    else:
        return ret


def isValidAddress(param):
    if len(param) < 30:
        return False
    elif len(param) > 35:
        return False
    elif not param.isalnum():
        return False
    elif not param[0] == 'K':
        return False
    else:
        return True


def isValidUsername(user):
    if re.match('^<@\!?[0-9]+>$', user):
        return True
    else:
        return False


def isValidAmount(amount):
    try:
        float(amount)
    except ValueError:
    	return False
    else:
        return True


if __name__ == '__main__':
    main()

