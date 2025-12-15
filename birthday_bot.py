import os
import re
import random
from datetime import datetime, timezone, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv

# Load environment variables from .env or sample_env.txt
if os.path.exists('.env'):
    load_dotenv('.env')
elif os.path.exists('sample_env.txt'):
    load_dotenv('sample_env.txt')

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 315292335  # Your Telegram ID - only you can use admin commands
BUDGET_LIMIT = 5000  # Hidden budget limit in rubles
current_spent = 0  # Track current spending
added_items = []  # List of added items: [{"link": "...", "price": 1500, "name": "..."}, ...]

# Deadline configuration
DEADLINE_MESSAGE = "Заявки больше не принимаются, время истекло!"
# December 19, 2025, 09:00 Moscow time (UTC+3)
MOSCOW_TZ = timezone(timedelta(hours=3))
DEADLINE_DATETIME = datetime(2025, 12, 19, 9, 0, 0, tzinfo=MOSCOW_TZ)
deadline_passed = False  # Flag to track if deadline has passed
active_users = set()  # Track users who have interacted with bot

# Conversation states
WAITING_FOR_PRICE = 1
WAITING_FOR_NAME = 2
WAITING_FOR_REMOVE = 3
WAITING_FOR_EDIT_ITEM = 4
WAITING_FOR_NEW_LINK = 5

# Menu keyboard
def get_menu_keyboard():
    keyboard = [
        [KeyboardButton("🛒 Закинуть в корзину")],
        [KeyboardButton("📋 Мои товары"), KeyboardButton("✏️ Изменить ссылку")],
        [KeyboardButton("❌ Удалить товар")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def is_deadline_passed():
    """Check if deadline has passed."""
    global deadline_passed
    if not deadline_passed:
        now = datetime.now(MOSCOW_TZ)
        if now >= DEADLINE_DATETIME:
            deadline_passed = True
    return deadline_passed


async def send_deadline_message(update: Update):
    """Send deadline message to user."""
    await update.message.reply_text(DEADLINE_MESSAGE)


async def notify_all_users_deadline_job(context: ContextTypes.DEFAULT_TYPE):
    """Send deadline message to all active users (job queue callback)."""
    global deadline_passed
    deadline_passed = True
    
    print(f"Deadline reached! Notifying {len(active_users)} users...", flush=True)
    
    # Try to send to all tracked users
    for user_id in active_users.copy():
        try:
            await context.bot.send_message(chat_id=user_id, text=DEADLINE_MESSAGE)
            print(f"Sent deadline message to {user_id}", flush=True)
        except Exception as e:
            print(f"Error sending deadline message to {user_id}: {e}", flush=True)


async def send_daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Send daily reminder about days left until deadline."""
    if is_deadline_passed():
        return
    
    now = datetime.now(MOSCOW_TZ)
    time_left = DEADLINE_DATETIME - now
    days_left = time_left.days
    hours_left = time_left.seconds // 3600
    
    if days_left > 0:
        if days_left == 1:
            reminder_text = f"⏰ Остался {days_left} день до окончания приёма заявок!\n\nУспей выбрать подарки! 🎁"
        elif days_left < 5:
            reminder_text = f"⏰ Осталось {days_left} дня до окончания приёма заявок!\n\nУспей выбрать подарки! 🎁"
        else:
            reminder_text = f"⏰ Осталось {days_left} дней до окончания приёма заявок!\n\nУспей выбрать подарки! 🎁"
    else:
        reminder_text = f"⏰ Остались последние часы! До окончания приёма заявок: {hours_left} ч.\n\nСкорее выбирай подарки! 🎁"
    
    print(f"Sending daily reminder to {len(active_users)} users: {days_left} days left", flush=True)
    
    # Load reminder GIF
    reminder_gif_path = os.path.join(os.path.dirname(__file__), 'static', 'time1.gif')
    
    # Send to all active users (except admin)
    for user_id in active_users.copy():
        if user_id != ADMIN_ID:  # Don't send reminder to admin
            try:
                if os.path.exists(reminder_gif_path):
                    with open(reminder_gif_path, 'rb') as gif_file:
                        await context.bot.send_animation(
                            chat_id=user_id,
                            animation=gif_file,
                            caption=reminder_text
                        )
                else:
                    await context.bot.send_message(chat_id=user_id, text=reminder_text)
            except Exception as e:
                print(f"Error sending reminder to {user_id}: {e}", flush=True)
                # Fallback to text message
                try:
                    await context.bot.send_message(chat_id=user_id, text=reminder_text)
                except:
                    pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    # Track user
    active_users.add(update.effective_user.id)
    
    # Check deadline
    if is_deadline_passed():
        await send_deadline_message(update)
        return
    
    welcome_message = """🎂 Аттракцион невиданной щедрости! 🎉

Лавэ не проблема, проблема что оно ограничено.

Кидай ссылки и цену пока бот не начнет ругаться что деньги кончилсь.

Заказы принимаются до 19.12 12:00, после чего все будет заказано и отправлено.

Товары можно удалять если передумала.

Управлять всем этим чудом можно через 'Меню' (выбери снизу) или напиши и отправь /menu"""
    
    # Send saw-jigsaw GIF with welcome message as caption
    try:
        gif_path = os.path.join(os.path.dirname(__file__), 'static', 'saw-jigsaw.gif')
        if os.path.exists(gif_path):
            with open(gif_path, 'rb') as gif_file:
                await update.message.reply_animation(
                    animation=gif_file,
                    caption=welcome_message,
                    reply_markup=get_menu_keyboard()
                )
                return
    except Exception as e:
        print(f"Error sending GIF: {e}", flush=True)
    
    # Fallback: send text only if GIF fails
    await update.message.reply_text(welcome_message, reply_markup=get_menu_keyboard())


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show menu."""
    # Track user
    active_users.add(update.effective_user.id)
    
    # Check deadline
    if is_deadline_passed():
        await send_deadline_message(update)
        return
    
    await update.message.reply_text("📌 Выбери действие:", reply_markup=get_menu_keyboard())


async def show_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show added items."""
    global added_items
    
    # Track user (viewing is allowed after deadline)
    active_users.add(update.effective_user.id)
    
    if not added_items:
        await update.message.reply_text(
            "📋 Так тут пусто, что смотреть-то!\n\n"
            "Тыкай в меню «🛒 Закинуть в корзину» чтобы начать",
            reply_markup=get_menu_keyboard()
        )
        return
    
    items_text = "📋 **Че я там накидала в корзину:**\n\n"
    for i, item in enumerate(added_items, 1):
        items_text += f"{i}. {item['name']} — {item['price']:.0f} ₽\n"
    
    await update.message.reply_text(items_text, reply_markup=get_menu_keyboard(), parse_mode='Markdown')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle incoming messages."""
    global added_items
    
    # Track user
    active_users.add(update.effective_user.id)
    
    message_text = update.message.text.strip()
    
    # Handle menu buttons
    if message_text == "🛒 Закинуть в корзину":
        if is_deadline_passed():
            await send_deadline_message(update)
            return ConversationHandler.END
        await update.message.reply_text(
            "🔗 Будьте добры ссылку:",
            reply_markup=get_menu_keyboard()
        )
        return ConversationHandler.END
    
    if message_text == "📋 Мои товары":
        await show_items(update, context)
        return ConversationHandler.END
    
    if message_text == "❌ Удалить товар":
        if is_deadline_passed():
            await send_deadline_message(update)
            return ConversationHandler.END
        if not added_items:
            await update.message.reply_text(
                "📋 Список пуст, нечего удалять!",
                reply_markup=get_menu_keyboard()
            )
            return ConversationHandler.END
        
        items_text = "❌ Какой товар удалить?\n\n"
        for i, item in enumerate(added_items, 1):
            items_text += f"{i}. {item['name']} — {item['price']:.0f} ₽\n"
        items_text += "\nНапиши номер товара:"
        
        await update.message.reply_text(items_text)
        return WAITING_FOR_REMOVE
    
    if message_text == "✏️ Изменить ссылку":
        if is_deadline_passed():
            await send_deadline_message(update)
            return ConversationHandler.END
        if not added_items:
            await update.message.reply_text(
                "📋 Список пуст, нечего изменять!",
                reply_markup=get_menu_keyboard()
            )
            return ConversationHandler.END
        
        items_text = "✏️ Для какого товара изменить ссылку?\n\n"
        for i, item in enumerate(added_items, 1):
            items_text += f"{i}. {item['name']} — {item['price']:.0f} ₽\n"
        items_text += "\nНапиши номер товара:"
        
        await update.message.reply_text(items_text)
        return WAITING_FOR_EDIT_ITEM
    
    # Check if message contains a URL
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, message_text)
    
    if not urls:
        await update.message.reply_text(
            "🛒 Отправь мне ссылку на товар!\n\n"
            "Например:\n"
            "https://www.ozon.ru/product/...\n"
            "https://www.wildberries.ru/catalog/...",
            reply_markup=get_menu_keyboard()
        )
        return ConversationHandler.END
    
    product_link = urls[0]
    
    # Check deadline before adding
    if is_deadline_passed():
        await send_deadline_message(update)
        return ConversationHandler.END
    
    # Check if link already exists in basket
    for item in added_items:
        if item['link'] == product_link:
            await update.message.reply_text(
                "⚠️ Так это уже в корзине, ссылка точно правильная?\n\n"
                "Отправь другую ссылку",
                reply_markup=get_menu_keyboard()
            )
            return ConversationHandler.END
    
    # Save the link in user data
    context.user_data['product_link'] = product_link
    
    await update.message.reply_text(
        "👍 Что там по деньгам, пиши цену (только число)\n\n"
        "Например: 1500"
    )
    
    return WAITING_FOR_PRICE


async def handle_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle price input."""
    global current_spent, added_items
    
    # Track user
    active_users.add(update.effective_user.id)
    
    # Check deadline
    if is_deadline_passed():
        await send_deadline_message(update)
        return ConversationHandler.END
    
    message_text = update.message.text.strip()
    
    # Handle menu buttons during price input
    if message_text in ["🛒 Закинуть в корзину", "📋 Мои товары", "❌ Удалить товар", "✏️ Изменить ссылку"]:
        context.user_data.pop('product_link', None)
        if message_text == "📋 Мои товары":
            await show_items(update, context)
        elif message_text == "❌ Удалить товар" or message_text == "✏️ Изменить ссылку":
            return await handle_message(update, context)
        else:
            await update.message.reply_text("🔗 Будьте добры ссылку:", reply_markup=get_menu_keyboard())
        return ConversationHandler.END
    
    # Try to extract price
    price_match = re.search(r'(\d+(?:[.,]\d{1,2})?)', message_text)
    
    if not price_match:
        await update.message.reply_text(
            "❌ Не понял цену. Напиши просто число!\n\n"
            "Например: 1500"
        )
        return WAITING_FOR_PRICE
    
    try:
        price = float(price_match.group(1).replace(',', '.'))
    except ValueError:
        await update.message.reply_text("❌ Напиши цену числом, например: 1500")
        return WAITING_FOR_PRICE
    
    if price <= 0 or price > 1000000:
        await update.message.reply_text("❌ Что-то тут не так")
        return WAITING_FOR_PRICE
    
    # Check budget limit (hidden from user)
    remaining_budget = BUDGET_LIMIT - current_spent

    if price <= remaining_budget:
        # Save price and ask for name
        context.user_data['product_price'] = price
        
        await update.message.reply_text(
            "📝 Как называется?"
        )
        return WAITING_FOR_NAME
    else:
        over_limit_message = f"""
❌ Ну ничего себе, это что такое? Деньги не бесконечные

💰 Цена: {price:.0f} ₽
😔 Придется поменять на что-то подешевле (а сколько денег осталось ты не знаешь АХААХХАХАХАХА)
        """
        await update.message.reply_text(over_limit_message, reply_markup=get_menu_keyboard())
        context.user_data.pop('product_link', None)
        return ConversationHandler.END


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle product name input."""
    global current_spent, added_items
    
    # Track user
    active_users.add(update.effective_user.id)
    
    # Check deadline
    if is_deadline_passed():
        await send_deadline_message(update)
        return ConversationHandler.END
    
    message_text = update.message.text.strip()
    
    # Handle menu buttons
    if message_text in ["🛒 Закинуть в корзину", "📋 Мои товары", "❌ Удалить товар", "✏️ Изменить ссылку"]:
        context.user_data.pop('product_link', None)
        context.user_data.pop('product_price', None)
        if message_text == "📋 Мои товары":
            await show_items(update, context)
        elif message_text == "❌ Удалить товар" or message_text == "✏️ Изменить ссылку":
            return await handle_message(update, context)
        else:
            await update.message.reply_text("🔗 Будьте добры ссылку:", reply_markup=get_menu_keyboard())
        return ConversationHandler.END
    
    product_name = message_text
    product_link = context.user_data.get('product_link', '')
    price = context.user_data.get('product_price', 0)
    
    # Add to current spent and save item
    current_spent += price
    added_items.append({
        "link": product_link,
        "price": price,
        "name": product_name
    })

    success_message = f"""✅ Лавэха потрачена, товар в корзине!

🏷 {product_name}
💰 Цена: {price:.0f} ₽
🎁 Погнали дальше!"""
    
    # Send random meme GIF with success message as caption
    try:
        meme_files = ['meme1.gif', 'meme2.gif', 'meme3.gif', 'meme4.gif', 'meme5.gif', 'meme7.gif', 'meme8.gif']
        random_meme = random.choice(meme_files)
        gif_path = os.path.join(os.path.dirname(__file__), 'static', random_meme)
        if os.path.exists(gif_path):
            with open(gif_path, 'rb') as gif_file:
                await update.message.reply_animation(
                    animation=gif_file,
                    caption=success_message,
                    reply_markup=get_menu_keyboard()
                )
        else:
            await update.message.reply_text(success_message, reply_markup=get_menu_keyboard())
    except Exception as e:
        print(f"Error sending meme GIF: {e}", flush=True)
        await update.message.reply_text(success_message, reply_markup=get_menu_keyboard())
    
    # Clear saved data
    context.user_data.pop('product_link', None)
    context.user_data.pop('product_price', None)
    
    return ConversationHandler.END


async def handle_remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle item removal."""
    global current_spent, added_items
    
    # Track user
    active_users.add(update.effective_user.id)
    
    # Check deadline
    if is_deadline_passed():
        await send_deadline_message(update)
        return ConversationHandler.END
    
    message_text = update.message.text.strip()
    
    # Handle menu buttons during remove
    if message_text in ["🛒 Закинуть в корзину", "📋 Мои товары", "❌ Удалить товар", "✏️ Изменить ссылку"]:
        if message_text == "📋 Мои товары":
            await show_items(update, context)
        elif message_text == "🛒 Закинуть в корзину":
            await update.message.reply_text("🔗 Будьте добры ссылку:", reply_markup=get_menu_keyboard())
        else:
            return await handle_message(update, context)
        return ConversationHandler.END
    
    # Try to get item number
    try:
        item_num = int(message_text)
    except ValueError:
        await update.message.reply_text(
            "❌ Напиши номер товара (число)!",
            reply_markup=get_menu_keyboard()
        )
        return ConversationHandler.END
    
    if item_num < 1 or item_num > len(added_items):
        await update.message.reply_text(
            f"❌ Нет товара с номером {item_num}!",
            reply_markup=get_menu_keyboard()
        )
        return ConversationHandler.END
    
    # Remove item
    removed_item = added_items.pop(item_num - 1)
    current_spent -= removed_item['price']
    
    refund_message = f"✅ {removed_item['name']} за {removed_item['price']:.0f} ₽ удалён!\n\n💸 {removed_item['price']:.0f} ₽ вернулись в бюджет"
    
    # Send meme6 GIF with refund message as caption
    try:
        gif_path = os.path.join(os.path.dirname(__file__), 'static', 'meme6.gif')
        if os.path.exists(gif_path):
            with open(gif_path, 'rb') as gif_file:
                await update.message.reply_animation(
                    animation=gif_file,
                    caption=refund_message,
                    reply_markup=get_menu_keyboard()
                )
        else:
            await update.message.reply_text(refund_message, reply_markup=get_menu_keyboard())
    except Exception as e:
        print(f"Error sending meme6 GIF: {e}", flush=True)
        await update.message.reply_text(refund_message, reply_markup=get_menu_keyboard())
    
    return ConversationHandler.END


async def handle_edit_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle selecting item to edit."""
    global added_items
    
    # Track user
    active_users.add(update.effective_user.id)
    
    # Check deadline
    if is_deadline_passed():
        await send_deadline_message(update)
        return ConversationHandler.END
    
    message_text = update.message.text.strip()
    
    # Handle menu buttons
    if message_text in ["🛒 Закинуть в корзину", "📋 Мои товары", "❌ Удалить товар", "✏️ Изменить ссылку"]:
        if message_text == "📋 Мои товары":
            await show_items(update, context)
        elif message_text == "🛒 Закинуть в корзину":
            await update.message.reply_text("🔗 Будьте добры ссылку:", reply_markup=get_menu_keyboard())
        else:
            return await handle_message(update, context)
        return ConversationHandler.END
    
    # Try to get item number
    try:
        item_num = int(message_text)
    except ValueError:
        await update.message.reply_text(
            "❌ Напиши номер товара (число)!",
            reply_markup=get_menu_keyboard()
        )
        return ConversationHandler.END
    
    if item_num < 1 or item_num > len(added_items):
        await update.message.reply_text(
            f"❌ Нет товара с номером {item_num}!",
            reply_markup=get_menu_keyboard()
        )
        return ConversationHandler.END
    
    # Save item index for editing
    context.user_data['edit_item_index'] = item_num - 1
    item = added_items[item_num - 1]
    
    await update.message.reply_text(
        f"🔗 Отправь новую ссылку для «{item['name']}» ({item['price']:.0f} ₽):"
    )
    
    return WAITING_FOR_NEW_LINK


async def handle_new_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle new link input for editing."""
    global added_items
    
    # Track user
    active_users.add(update.effective_user.id)
    
    # Check deadline
    if is_deadline_passed():
        await send_deadline_message(update)
        return ConversationHandler.END
    
    message_text = update.message.text.strip()
    
    # Handle menu buttons
    if message_text in ["🛒 Закинуть в корзину", "📋 Мои товары", "❌ Удалить товар", "✏️ Изменить ссылку"]:
        context.user_data.pop('edit_item_index', None)
        if message_text == "📋 Мои товары":
            await show_items(update, context)
        elif message_text == "🛒 Закинуть в корзину":
            await update.message.reply_text("🔗 Будьте добры ссылку:", reply_markup=get_menu_keyboard())
        else:
            return await handle_message(update, context)
        return ConversationHandler.END
    
    # Check if message contains a URL
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, message_text)
    
    if not urls:
        await update.message.reply_text(
            "❌ Отправь ссылку на товар!\n\n"
            "Например:\n"
            "https://www.ozon.ru/product/..."
        )
        return WAITING_FOR_NEW_LINK
    
    new_link = urls[0]
    item_index = context.user_data.get('edit_item_index', 0)
    
    # Check if link already exists in basket (except current item)
    for i, item in enumerate(added_items):
        if i != item_index and item['link'] == new_link:
            await update.message.reply_text(
                "⚠️ Так это уже в корзине, ссылка точно правильная?\n\n"
                "Отправь другую ссылку 😊"
            )
            return WAITING_FOR_NEW_LINK
    
    # Update the link
    item_name = added_items[item_index]['name']
    added_items[item_index]['link'] = new_link
    
    await update.message.reply_text(
        f"✅ Ссылка для «{item_name}» обновлена!",
        reply_markup=get_menu_keyboard()
    )
    
    context.user_data.pop('edit_item_index', None)
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    context.user_data.pop('product_link', None)
    context.user_data.pop('product_price', None)
    context.user_data.pop('edit_item_index', None)
    await update.message.reply_text("👌 Хорошо!", reply_markup=get_menu_keyboard())
    return ConversationHandler.END


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's Telegram ID."""
    user_id = update.effective_user.id
    await update.message.reply_text(f"🆔 Твой ID: {user_id}")


async def budget_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current budget status (for admin only - not visible to sister)"""
    if update.effective_user.id != ADMIN_ID:
        return  # Ignore if not admin
    
    global current_spent, added_items

    remaining = BUDGET_LIMIT - current_spent
    status_message = f"""
📊 Статус бюджета:

💰 Потрачено: {current_spent:.0f} ₽
💵 Осталось: {remaining:.0f} ₽
🎯 Лимит: {BUDGET_LIMIT} ₽
📦 Товаров: {len(added_items)}
    """
    
    if added_items:
        status_message += "\n📋 Товары:\n"
        for i, item in enumerate(added_items, 1):
            status_message += f"{i}. {item['name']} — {item['price']:.0f} ₽\n   🔗 {item['link']}\n"
    
    await update.message.reply_text(status_message)


async def reset_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reset budget counter (for admin only)"""
    if update.effective_user.id != ADMIN_ID:
        return  # Ignore if not admin
    
    global current_spent, added_items
    current_spent = 0
    added_items = []
    await update.message.reply_text("✅ Бюджет и список товаров сброшены!")


async def test_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send test daily reminder (for admin only)"""
    if update.effective_user.id != ADMIN_ID:
        return  # Ignore if not admin
    
    # Send reminder to all active users including admin for testing
    now = datetime.now(MOSCOW_TZ)
    time_left = DEADLINE_DATETIME - now
    days_left = time_left.days
    hours_left = time_left.seconds // 3600
    
    if days_left > 0:
        if days_left == 1:
            reminder_text = f"⏰ Остался {days_left} день до окончания приёма заявок!\n\nУспей выбрать подарки! 🎁"
        elif days_left < 5:
            reminder_text = f"⏰ Осталось {days_left} дня до окончания приёма заявок!\n\nУспей выбрать подарки! 🎁"
        else:
            reminder_text = f"⏰ Осталось {days_left} дней до окончания приёма заявок!\n\nУспей выбрать подарки! 🎁"
    else:
        reminder_text = f"⏰ Остались последние часы! До окончания приёма заявок: {hours_left} ч.\n\nСкорее выбирай подарки! 🎁"
    
    # Load reminder GIF
    reminder_gif_path = os.path.join(os.path.dirname(__file__), 'static', 'time1.gif')
    print(f"Reminder GIF path: {reminder_gif_path}", flush=True)
    print(f"File exists: {os.path.exists(reminder_gif_path)}", flush=True)
    
    # Send to all active users for testing
    sent_count = 0
    for user_id in active_users.copy():
        try:
            if os.path.exists(reminder_gif_path):
                with open(reminder_gif_path, 'rb') as gif_file:
                    await context.bot.send_animation(
                        chat_id=user_id,
                        animation=gif_file,
                        caption=reminder_text
                    )
                sent_count += 1
                print(f"Sent reminder with GIF to {user_id}", flush=True)
            else:
                await context.bot.send_message(chat_id=user_id, text=reminder_text)
                sent_count += 1
                print(f"GIF not found, sent text to {user_id}", flush=True)
        except Exception as e:
            print(f"Error sending test reminder to {user_id}: {e}", flush=True)
            # Fallback to text
            try:
                await context.bot.send_message(chat_id=user_id, text=reminder_text)
                sent_count += 1
            except:
                pass
    
    await update.message.reply_text(f"✅ Тестовое напоминание отправлено {sent_count} пользователям!")


def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not found in environment variables!")
        print("Please create a .env file with your BOT_TOKEN")
        return

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Set up deadline notification using bot's job queue
    job_queue = application.job_queue
    if job_queue:
        now = datetime.now(MOSCOW_TZ)
        if DEADLINE_DATETIME > now:
            # Schedule the deadline notification
            job_queue.run_once(
                notify_all_users_deadline_job,
                when=DEADLINE_DATETIME,
                name="deadline_notification"
            )
            print(f"Deadline notification scheduled for {DEADLINE_DATETIME}", flush=True)
            
            # Schedule daily reminder at 12:00 Moscow time
            from datetime import time as dt_time
            reminder_time = dt_time(hour=12, minute=0, second=0, tzinfo=MOSCOW_TZ)
            job_queue.run_daily(
                send_daily_reminder,
                time=reminder_time,
                name="daily_reminder"
            )
            print(f"Daily reminder scheduled for 12:00 Moscow time", flush=True)
        else:
            print("Deadline has already passed", flush=True)

    # Conversation handler for link -> price -> name flow, remove flow, and edit flow
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        states={
            WAITING_FOR_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_price)],
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            WAITING_FOR_REMOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_remove)],
            WAITING_FOR_EDIT_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_item)],
            WAITING_FOR_NEW_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_link)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("myid", myid))
    application.add_handler(CommandHandler("budget", budget_status))
    application.add_handler(CommandHandler("reset", reset_budget))
    application.add_handler(CommandHandler("testreminder", test_reminder))
    application.add_handler(conv_handler)

    # Start the bot
    print("Bot is starting...", flush=True)
    print("Send /start to your bot in Telegram!", flush=True)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
