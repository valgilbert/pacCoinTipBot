#!/bin/bash -e

sudo apt-get update
sudo apt-get install python3 python3-pip

sudo pip3 install python-telegram-bot --upgrade
sudo pip3 install discord.py --upgrade

sudo mkdir -p /opt/foxdCoinTipBot

sudo cp -prf ~/foxdCoinTipBot/foxdCoinDiscordTipBot /etc/init.d/foxdCoinDiscordTipBot
sudo cp -prf ~/foxdCoinTipBot/foxdCoinDiscordTipBot.py /opt/foxdCoinTipBot/foxdCoinDiscordTipBot.py
sudo cp -prf ~/foxdCoinTipBot/foxdCoinTelegramTipBot /etc/init.d/foxdCoinTelegramTipBot
sudo cp -prf ~/foxdCoinTipBot/foxdCoinTelegramTipBot.py /opt/foxdCoinTipBot/foxdCoinTelegramTipBot.py
sudo cp -prf ~/foxdCoinTipBot/pickledb.py /opt/foxdCoinTipBot/pickledb.py

rm -rf ~/foxdCoinTipBot

echo "DONE!!"
