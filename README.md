# 🎂 Birthday Shopping Bot

A comprehensive Telegram bot for managing birthday shopping lists! Your sister can add items with links and prices, track her budget, and get daily reminders until the deadline. The bot includes fun GIFs, menu navigation, and admin controls.

## ✨ Features

- **🛒 Item Management**: Add, remove, and edit shopping items with links and names
- **💰 Budget Tracking**: Hidden budget limit with spending monitoring
- **🎯 Smart Responses**: Clear feedback on budget status with fun GIFs
- **📅 Daily Reminders**: Automatic daily notifications showing days left until deadline
- **⏰ Deadline System**: Automatic shutdown after December 19, 2025 at 09:00 Moscow time
- **🎨 GIF Integration**: Fun animated responses for different actions
- **👥 Admin Controls**: Restricted commands for budget management
- **📱 Menu Interface**: User-friendly button navigation

## 🚀 Setup

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy your bot token

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the project root:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id_here
```

**Required Variables:**
- `BOT_TOKEN`: Your bot token from BotFather
- `ADMIN_ID`: Your Telegram user ID (get it by sending `/myid` to the bot)

### 4. Add GIF Files

Place these files in the `static/` folder:
- `saw-jigsaw.gif` (welcome message)
- `meme1.gif` to `meme8.gif` (success messages)
- `meme6.gif` (refund message)
- `time1.gif` (daily reminders)

### 5. Run the Bot

```bash
python birthday_bot.py
```

## 🖥️ VDS Deployment

### Option 1: From GitHub (Recommended)

```bash
# Connect to your VDS
ssh user@your-vds-ip

# Install Git and clone repository
sudo apt update
sudo apt install git -y
git clone https://github.com/crash4star/hb_bot.git birthday_bot
cd birthday_bot

# Run deployment script
chmod +x deploy_to_vds.sh
sudo ./deploy_to_vds.sh
```

### Option 2: Manual Upload

Upload all files to your VDS and run:

```bash
chmod +x deploy_to_vds.sh
sudo ./deploy_to_vds.sh
```

### Post-Deployment Setup

```bash
# Edit environment file
nano .env

# Start the bot
sudo systemctl start birthdaybot

# Check status
sudo systemctl status birthdaybot

# View logs
sudo journalctl -u birthdaybot -f
```

## 🎮 Usage

### For Your Sister:

#### Main Menu:
- **🛒 Добавить товар** - Add new item to basket
- **📋 Мои товары** - View all added items

#### Adding Items (3-step process):
1. Click "🛒 Добавить товар" → Send product link
2. Bot asks for price → Enter price in rubles
3. Bot asks for product name → Enter product name

#### Managing Items:
- **❌ Удалить товар** - Remove items from basket (refunds budget)
- **✏️ Изменить ссылку** - Change link for existing items

### Admin Commands (restricted to bot owner):
- `/budget` - Check current budget status and remaining amount
- `/reset` - Reset budget counter and clear all items
- `/myid` - Get your Telegram ID (for setup)
- `/testreminder` - Send test daily reminder

## 🛠️ How It Works

### Item Addition Flow:
1. **Link Input**: User sends product link from any webshop
2. **Price Input**: Bot prompts for price (manual entry)
3. **Name Input**: Bot asks for product name for clarity
4. **Budget Check**: Validates against remaining budget (5000 ₽ total)
5. **Response**: Success message with GIF if within budget, rejection if over limit

### Daily Reminder System:
- **⏰ Scheduled**: Runs daily at 12:00 Moscow time
- **📅 Countdown**: Shows days/hours remaining until deadline
- **🎨 Visual**: Includes `time1.gif` animation
- **🎯 Targeted**: Sent only to active users (not admin)

### Deadline Management:
- **📆 End Date**: December 19, 2025 at 09:00 Moscow time
- **🔒 Auto-lock**: Disables all functions after deadline
- **📢 Notification**: Broadcasts deadline message to all users
- **🕐 Timezone**: Uses Europe/Moscow timezone

### GIF Integration:
- **🎂 Welcome**: `saw-jigsaw.gif` with custom message
- **✅ Success**: Random from `meme1.gif` to `meme8.gif`
- **💸 Refund**: `meme6.gif` when items removed
- **⏰ Reminder**: `time1.gif` daily countdown

## ⚠️ Important Notes

- **Budget**: Hidden 5000 ₽ limit (configurable in code)
- **Deadline**: Bot stops accepting requests after December 19, 2025 at 09:00 MSK
- **Persistence**: Data resets when bot restarts (no database)
- **Admin Only**: `/budget`, `/reset`, `/testreminder` commands restricted to `ADMIN_ID`
- **GIFs Required**: Bot needs `static/` folder with all GIF files for full functionality
- **Timezone**: All times use Europe/Moscow timezone

## 🔄 Updating from GitHub

To update your deployed bot with new features:

```bash
cd ~/birthday_bot
git pull origin main
sudo systemctl restart birthdaybot
```

## 📊 Current Status

- **Budget Limit**: 5000 ₽ (hidden from users)
- **Deadline**: December 19, 2025 at 09:00 Moscow time
- **Daily Reminder**: 12:00 Moscow time with GIF
- **Version**: Latest from [GitHub](https://github.com/crash4star/hb_bot)

## 🎉 Happy Birthday!

This comprehensive shopping assistant will make your sister's birthday celebration amazing! Features automatic reminders, fun GIFs, and seamless budget management. 🎂✨

## 📂 Repository

- **GitHub**: [crash4star/hb_bot](https://github.com/crash4star/hb_bot)
- **Language**: Python 3.8+
- **Framework**: python-telegram-bot
- **License**: MIT

## 🤝 Contributing

Feel free to open issues or submit pull requests for improvements!

---

*Built with ❤️ for birthday celebrations*
