#!/bin/bash

# Deployment script for birthday bot
echo "🚀 Deploying birthday bot to server..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip -y

# Install dependencies
pip3 install -r requirements.txt

# Create bot user (optional)
sudo useradd -m -s /bin/bash birthdaybot || echo "User already exists"

# Create directories
mkdir -p /home/birthdaybot/bot
mkdir -p /home/birthdaybot/logs

# Copy files
cp birthday_bot.py /home/birthdaybot/bot/
cp requirements.txt /home/birthdaybot/bot/
cp sample_env.txt /home/birthdaybot/bot/.env

# Set permissions
sudo chown -R birthdaybot:birthdaybot /home/birthdaybot

echo "✅ Files deployed!"
echo "📝 Don't forget to:"
echo "1. Edit /home/birthdaybot/bot/.env with your BOT_TOKEN"
echo "2. Run the bot with: cd /home/birthdaybot/bot && python3 birthday_bot.py"
