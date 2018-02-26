#!/bin/bash -e

sudo apt-get update
sudo apt-get install python3 python3-pip

sudo pip3 install python-telegram-bot --upgrade
sudo pip3 install discord.py --upgrade

sudo mkdir -p /opt/lynxTipBot

sudo cp -prf ~/lynxTipBot/lynxDiscordTipBot /etc/init.d/lynxDiscordTipBot
sudo cp -prf ~/lynxTipBot/lynxDiscordTipBot.py /opt/lynxTipBot/lynxDiscordTipBot.py
sudo cp -prf ~/lynxTipBot/lynxTelegramTipBot /etc/init.d/lynxTelegramTipBot
sudo cp -prf ~/lynxTipBot/lynxTelegramTipBot.py /opt/lynxTipBot/lynxTelegramTipBot.py
sudo cp -prf ~/lynxTipBot/pickledb.py /opt/lynxTipBot/pickledb.py

rm -rf ~/lynxTipBot

echo "DONE!!"
