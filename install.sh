#!/bin/bash -e

sudo apt-get update
sudo apt-get install python3 python3-pip

sudo pip3 install python-telegram-bot --upgrade
sudo pip3 install discord.py --upgrade

sudo mkdir -p /opt/pacCoinTipBot

sudo cp -prf ~/pacCoinTipBot/pacCoinDiscordTipBot /etc/init.d/pacCoinDiscordTipBot
sudo cp -prf ~/pacCoinTipBot/pacCoinDiscordTipBot.py /opt/pacCoinTipBot/pacCoinDiscordTipBot.py
sudo cp -prf ~/pacCoinTipBot/pacCoinTelegramTipBot /etc/init.d/pacCoinTelegramTipBot
sudo cp -prf ~/pacCoinTipBot/pacCoinTelegramTipBot.py /opt/pacCoinTipBot/pacCoinTelegramTipBot.py
sudo cp -prf ~/pacCoinTipBot/pickledb.py /opt/pacCoinTipBot/pickledb.py

rm -rf ~/pacCoinTipBot

echo "DONE!!"
