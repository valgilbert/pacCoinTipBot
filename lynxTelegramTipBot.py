#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import subprocess
import requests
import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram import ParseMode
from telegram import TelegramError
from telegram import Update
from telegram.ext.dispatcher import run_async
import pickledb
import re
import time

''' begin configuration section '''

BOTNAME  = '____CHANGEME____'
TOKEN    = '____CHANGEME____'
LOG_FILE = '____CHANGEME____'
DB_FILE  = '____CHANGEME____'
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

db = pickledb.load(DB_FILE, True)

def main():
    
    updater = Updater(TOKEN, workers=10)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('hi', hi))
    dp.add_handler(CommandHandler('moon', moon))
    dp.add_handler(CommandHandler('info', info))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('balance', balance))
    dp.add_handler(CommandHandler('withdraw', withdraw))
    dp.add_handler(CommandHandler('deposit', deposit))
    dp.add_handler(CommandHandler('tip', tip))
    dp.add_handler(CommandHandler('mcap', mcap))
    dp.add_handler(CommandHandler('price', price))

    dp.add_handler(MessageHandler(Filters.all, events))

    update_queue = updater.start_polling()

    updater.idle()


def getUserID(bot, update, username):
    cid = update.message.chat_id

    value = None
    users = db.getall()
    for uid in users:
        user = db.get(uid)
        
        if user != username:
            continue

        user_data = bot.getChatMember(cid, uid)
        user_name = user_data.user.username

        db.set(str(uid), user_name)
 
        if username == user_name:
            value = uid

    return value


def events(bot, update):
    from_user = update.message.from_user
    user_name = from_user.username
    user_uuid = from_user.id

    db.set(str(user_uuid), user_name)

    return True


def receive_message(message):
    msg  = message.text
    user = message.from_user.username
    uuid = message.from_user.id

    logger.info("@{} [#{}]: {}".format(user, uuid, msg))

    return True


def send_message(bot, cid, msg, mode):
    if "commands" not in msg and "cryptopia" not in msg:
        logger.info("{}: {}".format(BOTNAME, msg))

    mode = ParseMode.MARKDOWN or False
    bot.send_message(chat_id=cid, text=msg, parse_mode=mode)

    return True


def info(bot, update):
    chat_uuid = update.message.chat_id

    user_name = update.message.from_user.username
    user_uuid = update.message.from_user.id

    msg = \
    """
      ```
                  INFO SECTION
      ```
      commands like */tip* & */withdraw* have a specfic format,\
    use them like so:
     
     Tipping format: 
       `/tip @[user] [amount]        (without brackets)`
     
     Withdrawing format: 
       `/withdraw [address] [amount] (without brackets)`

     WHERE:
    ` 
       [address] = withdraw #PacCoin address
          [user] = telegram username 
        [amount] = amount of #pacCoin to utilise 
    `

     *NOTE*:
      - don't deposit a significant amount of #PacCoin through this #BOT
      - make sure that you enter a valid #PacCoin address when you perform a withdraw
      - we are not responsible of your funds if something bad happen to this #BOT 
     ```
          USE THIS #BOT AT YOUR OWN RISK
     ```
    """

    send_message(bot, chat_uuid, msg, True)

    return True


def help(bot, update):
    chat_uuid = update.message.chat_id

    user_name = update.message.from_user.username
    user_uuid = update.message.from_user.id

    msg = \
    """
      The following commands are at your disposal:
       /info, /balance, /deposit, /withdraw, /tip and /price
    """

    send_message(bot, chat_uuid, msg, True)

    return True


def tip(bot, update):
    chat_uuid = update.message.chat_id

    receive_message(update.message)

    user_name = update.message.from_user.username
    user_uuid = update.message.from_user.id

    message = update.message.text.split(' ')
    if len(message) != 3:
        msg = "Please use /tip <username> <amount>!"
        send_message(bot, chat_uuid, msg, False)
        return False

    if user_name is None:
        msg = "Please set a #telegram username!"
        send_message(bot, chat_uuid, msg, False)
        return False
    if not isValidUsername(message[1]):
        msg = "Please input a valid username (ex: @JonDoe)!"
        send_message(bot, chat_uuid, msg, False)
        return False
    if not isValidAmount(message[2]):
        msg = "Please input a valid amount (ex: 1000)!"
        send_message(bot, chat_uuid, msg, False)
        return False

    amount = float(message[2])
    target = (message[1])[1:]

    if amount > 100000:
        msg = "Please send a lower amount (max: 100,000 PacCoin)!"
        send_message(bot, chat_uuid, msg, False)
        return False
    if target == user_name:
        msg = "You can't tip yourself silly.!"
        send_message(bot, chat_uuid, msg, False)
        return False
    if target == BOTNAME:
        bot.send_message(chat_id=chat_uuid, text='HODL.')
        return False
    target_uuid = getUserID(bot, update, target)
    if not target_uuid:
        msg = '@{} has no activity in this chat!'.format(target)
        send_message(bot, chat_uuid, msg, False)
        return False

    result = subprocess.run([
        APP_EXE, 
        '-rpcuser=bitcoin',
        '-rpcpassword=local321', 
        'getbalance',
        str(user_uuid)
    ], 
    stdout=subprocess.PIPE)

    balance = float(result.stdout.strip().decode('utf-8'))

    if balance < amount:
        msg = '@{0} you have insufficent funds.'.format(user_name)
        send_message(bot, chat_uuid, msg, False)
        return False

    tx = subprocess.run([
        APP_EXE,
        '-rpcuser=bitcoin',
        '-rpcpassword=local321',
        'move',
        str(user_uuid),
        str(target_uuid),
        str(amount),
    ], 
    stdout=subprocess.PIPE)

    msg = '@{0} tipped @{1} of {2} PacCoin'.format(user_name, target, amount)
    send_message(bot, chat_uuid, msg, False)

    return True


def balance(bot, update):
    chat_uuid = update.message.chat_id

    user_name = update.message.from_user.username
    user_uuid = update.message.from_user.id

    if user_name is None:
        msg = "Please set a telegram username in your profile settings!"
        send_message(bot, chat_uuid, msg, False)
        return False

    result = subprocess.run([
        APP_EXE, 
        '-rpcuser=bitcoin',
        '-rpcpassword=local321', 
        'getbalance',
        str(user_uuid)
    ], 
    stdout=subprocess.PIPE)
    clean = result.stdout.strip().decode('utf-8')

    balance = float(clean)
    balance = str('{:,.8f}'.format(balance))

    msg = '@{0} your current balance is: {1} PacCoin'.format(user_name, balance)
    send_message(bot, chat_uuid, msg, False)

    return True


def deposit(bot, update):
    chat_uuid = update.message.chat_id

    user_name = update.message.from_user.username
    user_uuid = update.message.from_user.id

    if user_name is None:
        msg = 'Please set a telegram username in your profile settings!'
        send_message(bot, chat_uuid, msg, False)
        return False

    result = subprocess.run([
        APP_EXE, 
        '-rpcuser=bitcoin',
        '-rpcpassword=local321', 
        'getaccountaddress',
        str(user_uuid)
    ], 
    stdout=subprocess.PIPE)
    clean = result.stdout.strip().decode('utf-8')

    msg = '@{} your depositing address is: {}'.format(user_name, clean)
    send_message(bot, chat_uuid, msg, False)

    return True


def withdraw(bot, update):
    chat_uuid = update.message.chat_id

    receive_message(update.message)

    user_name = update.message.from_user.username
    user_uuid = update.message.from_user.id

    if user_name is None:
        msg = 'Please set a telegram username!'
        send_message(bot, chat_uuid, msg, False)
        return False

    message = update.message.text.split(' ')
    if len(message) != 3:
        msg = 'Please use /withdraw <address> <amount>!'
        send_message(bot, chat_uuid, msg, False)
        return False
    if not isValidAddress(message[1]):
        msg = 'Please input a valid PacCoin address!'
        send_message(bot, chat_uuid, msg, False)
        return False
    if not isValidAmount(message[2]):
        msg = 'Please input a valid amount (ex: 1000)!'
        send_message(bot, chat_uuid, msg, False)
        return False

    amount = float(message[2])
    address = message[1]

    result = subprocess.run([
        APP_EXE, 
        '-rpcuser=bitcoin',
        '-rpcpassword=local321', 
        'getbalance',
        str(user_uuid)
    ], 
    stdout=subprocess.PIPE)
    clean = result.stdout.strip().decode('utf-8')

    balance = float(clean)
    if balance < amount:
        msg = '@{0} you have insufficent funds.'.format(user_name)
        send_message(bot, chat_uuid, msg, False)
        return False

    tx = subprocess.run([
        APP_EXE,
        '-rpcuser=bitcoin',
        '-rpcpassword=local321',
        'sendfrom',
        str(user_uuid),
        str(address),
        str(amount),
    ], 
    stdout=subprocess.PIPE)

    msg = '@{0} has successfully withdrew {2} PacCoin to address: {1}'\
              .format(user_name, address, amount)
    send_message(bot, chat_uuid, msg, False)

    return True


def price(bot, update):
    chat_uuid = update.message.chat_id

    getmarket = 'https://chart.meanxtrade.com/info.php?market=PacCoin_LTC'
    response  = requests.get(getmarket)
    json_data = response.json()
    
    if not json_data:
        msg = 'Failed to get data from cryptopia exchange!'
        send_message(bot, chat_uuid, msg, False)
        return False

    message = {}

    message['*LastPrice*'] = '{:,.8f}'.format(float(json_data['last']))
    message['*AskPrice*'] = '{:,.8f}'.format(float(json_data['lowestAsk']))
    message['*BidPrice*'] = '{:,.8f}'.format(float(json_data['highestBid']))
    message['*Volume*'] = '{:,.8f}'.format(float(json_data['baseVolume']))
    message['*High24Hr*'] = '{:,.8f}'.format(float(json_data['high24hr']))
    message['*Low24Hr*'] = '{:,.8f}'.format(float(json_data['low24hr']))
    message['*p%rate*'] = '{:,.8f}'.format(float(json_data['percentChange']))

    pretty_object = json.dumps(message, indent=4, sort_keys=True)
    label_market  = json_data['Data']['Label']

    msg = '*cryptopia* \[{0}]:\n{1}'.format(label_market, pretty_object)
    send_message(bot, chat_uuid, msg, True)

    return True


def mcap(bot, update):
    chat_uuid = update.message.chat_id

    user_name = update.message.from_user.usernamei
    user_uuid = update.message.from_user.id

    bot.send_message(chat_id=chat_uuid, text='work in progress!')

    return True


def moon(bot, update):
    chat_uuid = update.message.chat_id

    user_name = update.message.from_user.username
    user_uuid = update.message.from_user.id

    bot.send_message(chat_id=chat_uuid, text='Moon mission inbound!')

    return True


def hi(bot, update):
    chat_uuid = update.message.chat_id

    user_name = update.message.from_user.username
    user_uuid = update.message.from_user.id

    msg = 'Hello @{0}, how are you doing today?'.format(user_name)
    send_message(bot, chat_uuid, msg, False)

    return True


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
    if len(user) < 7:
        return False
    elif len(user) > 35:
        return False
    elif not re.match('^@[0-9A-Za-z_]+$', user):
        return False
    else:
        return True


def isValidAmount(amount):
    try:
        float(amount)
        return True
    except ValueError:
        pass
    if amount.isnumeric():
        return True
    return False


if __name__ == '__main__':
    main()

