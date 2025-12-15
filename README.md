# 🎂 Birthday Shopping Bot

A Telegram bot that helps your sister stay within her birthday budget! The bot checks prices from webshop links and tells her whether she can add items to her cart.

## ✨ Features

- **Price Checking**: Automatically extracts prices from webshop links
- **Budget Management**: Hidden 7000 ₽ budget limit
- **Smart Responses**: Tells sister to "Add to basket!" or "Limit is over"
- **Multiple Webshops**: Works with various Russian online stores
- **Admin Commands**: Budget tracking for the bot owner

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

```
BOT_TOKEN=your_bot_token_here
```

Replace `your_bot_token_here` with your actual bot token from BotFather.

### 4. Run the Bot

```bash
python birthday_bot.py
```

## 🎮 Usage

### For Your Sister:
- Send any webshop link to the bot
- Get instant feedback on whether she can add it to cart

### Admin Commands (for you):
- `/budget` - Check current budget status
- `/reset` - Reset the budget counter

## 🛠️ How It Works

1. **URL Detection**: Bot recognizes webshop links in messages
2. **Price Scraping**: Extracts prices using multiple methods:
   - Regex patterns for Russian currency (₽, руб, RUB)
   - Common CSS selectors (.price, .product-price, etc.)
3. **Budget Check**: Compares price against remaining budget (7000 ₽ total)
4. **Smart Response**: Gives appropriate message based on budget status

## 🔧 Supported Webshops

The bot works with most Russian online stores including:
- Wildberries
- Ozon
- Lamoda
- M.Video
- DNS
- And many others!

## 📋 Supported Price Formats

- `1 234 ₽`
- `1234 руб`
- `Цена: 1234`
- Prices in HTML elements with common selectors

## ⚠️ Important Notes

- The 7000 ₽ budget limit is completely hidden from your sister
- Bot tracks spending across all checked items
- Works best with direct product page links
- Some sites may block scraping - the bot handles this gracefully

## 🎉 Happy Birthday!

This bot will help make your sister's birthday shopping experience fun and surprise-free! 🎂✨
