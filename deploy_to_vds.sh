#!/bin/bash

# Birthday Bot Deployment Script for Clean VDS
# Run this script on your VDS server

echo "🚀 Starting Birthday Bot Deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "🐍 Installing Python, Git and dependencies..."
sudo apt install python3 python3-pip python3-venv git screen -y

# Create bot directory and clone from GitHub
echo "📁 Cloning bot from GitHub..."
mkdir -p ~/birthday_bot
cd ~/birthday_bot

# Clone your repository (replace with your GitHub repo URL)
echo "🔗 Enter your GitHub repository URL:"
echo "   Example: https://github.com/yourusername/birthday-bot.git"
echo "   Or: git@github.com:yourusername/birthday-bot.git"
echo ""
echo "⚠️  IMPORTANT: Clone your repository first!"
echo "   git clone YOUR_REPO_URL ."
echo ""
echo "Press Enter when ready to continue..."
read

# Alternative: uncomment and edit the line below with your repo URL
# git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .

# Create virtual environment
echo "🌐 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Setup environment file (you need to edit this manually)
echo "⚙️  Setting up environment..."
if [ ! -f .env ]; then
    cp sample_env.txt .env
    echo "❗ Please edit .env file with your BOT_TOKEN!"
    echo "   Run: nano .env"
fi

# Create startup script
echo "📝 Creating startup script..."
cat > start_bot.sh << 'EOF'
#!/bin/bash
cd ~/birthday_bot
source venv/bin/activate
python birthday_bot.py
EOF

chmod +x start_bot.sh

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/birthdaybot.service > /dev/null << EOF
[Unit]
Description=Birthday Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/birthday_bot
ExecStart=/home/$USER/birthday_bot/start_bot.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "▶️  Starting bot service..."
sudo systemctl daemon-reload
sudo systemctl enable birthdaybot
sudo systemctl start birthdaybot

echo "✅ Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit your .env file: nano ~/birthday_bot/.env"
echo "2. Add your BOT_TOKEN to the .env file"
echo "3. Restart the service: sudo systemctl restart birthdaybot"
echo "4. Check status: sudo systemctl status birthdaybot"
echo "5. View logs: sudo journalctl -u birthdaybot -f"
echo ""
echo "🎉 Your bot should be running! Test it with /start in Telegram."
