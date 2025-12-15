# 🚀 Deploying Birthday Bot to VDS

## 📋 Prerequisites
- Linux server (Ubuntu/Debian recommended)
- SSH access
- Your bot token from @BotFather

## 🛠️ Option 1: Automated Deployment (Recommended)

### Step 1: Upload files to server
```bash
# Upload these files to your server:
# - birthday_bot.py
# - requirements.txt
# - sample_env.txt
# - deploy.sh
```

### Step 2: Run deployment script
```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

### Step 3: Configure bot token
```bash
nano /home/birthdaybot/bot/.env
# Add your BOT_TOKEN
```

### Step 4: Start bot
```bash
sudo ./run_bot.sh
```

## 🛠️ Option 2: Manual Deployment

### Step 1: Connect to server
```bash
ssh user@your-server-ip
```

### Step 2: Install dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip -y
```

### Step 3: Create bot directory
```bash
mkdir -p ~/birthday_bot
cd ~/birthday_bot
```

### Step 4: Upload bot files
Upload `birthday_bot.py`, `requirements.txt`, `sample_env.txt` to `~/birthday_bot/`

### Step 5: Install Python packages
```bash
pip3 install -r requirements.txt
```

### Step 6: Configure bot token
```bash
cp sample_env.txt .env
nano .env
# Add your BOT_TOKEN from @BotFather
```

### Step 7: Run bot
```bash
python3 birthday_bot.py &
```

## 🔍 Monitoring

### Check if bot is running
```bash
ps aux | grep birthday_bot.py
```

### View logs
```bash
tail -f ~/birthday_bot/logs/bot.log
# or if using automated deployment:
tail -f /home/birthdaybot/bot/logs/bot.log
```

### Check system resources
```bash
htop
# or
top
```

## 🔄 Updating the bot

```bash
# Stop bot
pkill -f birthday_bot.py

# Upload new files
# Edit birthday_bot.py

# Restart
python3 birthday_bot.py &
```

## 🛡️ Security Tips

1. **Use strong passwords** for SSH
2. **Enable firewall**:
   ```bash
   sudo ufw enable
   sudo ufw allow ssh
   ```

3. **Use SSH keys instead of passwords**
4. **Keep system updated**: `sudo apt update && sudo apt upgrade`
5. **Monitor logs regularly**

## 🚨 Troubleshooting

### Bot not responding?
1. Check if bot is running: `ps aux | grep birthday_bot.py`
2. Check logs for errors
3. Verify BOT_TOKEN in .env file
4. Test bot token: `curl -X GET "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"`

### Bot stopped?
- Use `screen` or `tmux` for persistent sessions
- Or create a systemd service (advanced)

### High CPU/memory?
- Bot should be lightweight (< 50MB RAM)
- Check for memory leaks if it grows over time

## 📞 Support

If bot crashes or has issues:
1. Check logs first
2. Verify internet connection
3. Test with minimal code
4. Contact Telegram Bot API support if needed

---

**🎂 Happy birthday shopping!** Your sister will love the surprise! 🎉
