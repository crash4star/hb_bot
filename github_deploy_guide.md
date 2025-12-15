# Deploy Birthday Bot from GitHub to VDS

## Option 1: Clone from GitHub (Recommended)

### Step 1: Connect to your VDS
```bash
ssh user@your-vds-ip
```

### Step 2: Install Git (if not already installed)
```bash
sudo apt update
sudo apt install git -y
```

### Step 3: Clone your repository
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git birthday_bot
cd birthday_bot
```

Or if using SSH key:
```bash
git clone git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git birthday_bot
cd birthday_bot
```

### Step 4: Run the deployment script
```bash
chmod +x deploy_to_vds.sh
sudo ./deploy_to_vds.sh
```

## Option 2: Download ZIP from GitHub

If you prefer to download as ZIP:

```bash
cd ~
wget https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/archive/main.zip
unzip main.zip
mv YOUR_REPO_NAME-main birthday_bot
cd birthday_bot
chmod +x deploy_to_vds.sh
sudo ./deploy_to_vds.sh
```

## Option 3: Manual Upload

Upload files via SCP/SFTP:
```bash
# From your local machine
scp -r birthday_bot user@your-vds-ip:~
```

## After Deployment

### 1. Configure Environment
```bash
nano .env
# Add your BOT_TOKEN
```

### 2. Start the Bot
```bash
sudo systemctl start birthdaybot
sudo systemctl status birthdaybot
```

### 3. Check Logs
```bash
sudo journalctl -u birthdaybot -f
```

## Updating from GitHub

To update your bot with new changes:

```bash
cd ~/birthday_bot
git pull origin main
sudo systemctl restart birthdaybot
```

## Troubleshooting

### Permission Issues
```bash
sudo chown -R $USER:$USER ~/birthday_bot
sudo chmod +x ~/birthday_bot/start_bot.sh
```

### Git Authentication Issues
- Use HTTPS URL for public repos
- Setup SSH keys for private repos
- Use GitHub Personal Access Token for HTTPS authentication
