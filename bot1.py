import logging
import random
import asyncio
import sqlite3
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ChatJoinRequestHandler, MessageHandler, filters
from telegram.error import TelegramError

# Configuration
import os
TOKEN_BOT1 = os.getenv("BOT1_TOKEN")
if not TOKEN_BOT1:
    raise RuntimeError("BOT1_TOKEN not set in environment")

MAIN_CHANNEL = "https://t.me/+36cFwPP5dJ420DM0"
SECONDARY_CHANNEL = "https://t.me/+Agt0dHQXZHc3Mzg0"
PREMIUM_GROUP = "https://t.me/+Agt0dHQXZHc3Mzg0"
ADMIN_USERNAME = "lympidleaks"
ADMIN_CHAT_ID = None

# Database
DATABASE_FILE = "viral_bot1.db"

# Configuration pour Render
PORT = int(os.environ.get('PORT', 8000))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ViralDatabase:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        forwards_done INTEGER DEFAULT 0,
                        successful_unlocks INTEGER DEFAULT 0,
                        failed_attempts INTEGER DEFAULT 0,
                        total_viral_impact INTEGER DEFAULT 0
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS forward_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        main_channel_forwards INTEGER DEFAULT 0,
                        secondary_channel_forwards INTEGER DEFAULT 0,
                        session_completed BOOLEAN DEFAULT 0
                    )
                ''')
                conn.commit()
                logger.info("Base de données initialisée avec succès")
        except Exception as e:
            logger.error(f"Erreur init DB: {e}")
    
    def create_user(self, user_id, username=None, first_name=None):
        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, first_name)
                    VALUES (?, ?, ?)
                ''', (user_id, username, first_name))
                conn.commit()
        except Exception as e:
            logger.error(f"Erreur create_user: {e}")
    
    def start_forward_session(self, user_id):
        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO forward_sessions (user_id)
                    VALUES (?)
                ''', (user_id,))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Erreur start_forward_session: {e}")
            return None
    
    def update_forwards(self, user_id, main_forwards=0, secondary_forwards=0):
        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET forwards_done = forwards_done + ?
                    WHERE user_id = ?
                ''', (main_forwards + secondary_forwards, user_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Erreur update_forwards: {e}")
    
    def record_success(self, user_id):
        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET successful_unlocks = successful_unlocks + 1,
                                    total_viral_impact = total_viral_impact + 50
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Erreur record_success: {e}")
    
    def record_failure(self, user_id):
        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET failed_attempts = failed_attempts + 1
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Erreur record_failure: {e}")

db = ViralDatabase()
user_sessions = {}

async def start(update: Update, context):
    try:
        user = update.effective_user
        user_id = user.id
        
        db.create_user(user_id, user.username, user.first_name)
        
        welcome_msg = f"""
Hey {user.first_name}! 👋

🔥 **Want exclusive premium content?**

Simple task: Forward our channels to unlock instant access to amazing content.

**Make any request of any model you want but before complete this quick task** 🎯

Ready to get started?
        """
        
        keyboard = [[InlineKeyboardButton("🚀 Start Task", callback_data="start_forwards")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup)
        logger.info(f"Nouvel utilisateur: {user.first_name} ({user_id})")
        
    except Exception as e:
        logger.error(f"Erreur dans start: {e}")

async def handle_join_request(update: Update, context):
    try:
        chat_id = update.chat_join_request.chat.id
        user_id = update.chat_join_request.from_user.id
        user = update.chat_join_request.from_user
        
        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
        
        db.create_user(user_id, user.username, user.first_name)
        
        welcome_msg = f"""
Welcome {user.first_name}! 🎉

🎯 **Quick task to unlock premium access:**

**Make any request of any model you want but first complete this simple forwarding task.**

Takes 2 minutes, totally worth it! 🔥

Ready?
        """
        
        keyboard = [[InlineKeyboardButton("📤 Start Forwarding", callback_data="start_forwards")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=user_id,
            text=welcome_msg,
            reply_markup=reply_markup
        )
        
        if ADMIN_CHAT_ID:
            await context.bot.send_message(
                ADMIN_CHAT_ID,
                f"🔔 New user joined: {user.first_name} (@{user.username or 'no_username'})\n"
                f"ID: {user_id}\nTask sent immediately."
            )
        
    except Exception as e:
        logger.error(f"Error in join request: {e}")

async def handle_callback(update: Update, context):
    try:
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()
        
        if query.data == "start_forwards":
            await start_forward_process(query, context)
        elif query.data == "forward_main_done":
            await handle_main_forward_done(query, context)
        elif query.data == "forward_secondary_done":
            await handle_secondary_forward_done(query, context)
        elif query.data == "check_access":
            await check_access_with_failure(query, context)
        elif query.data == "retry_check":
            await check_access_with_failure(query, context)
            
    except Exception as e:
        logger.error(f"Erreur callback: {e}")

async def start_forward_process(query, context):
    try:
        user_id = query.from_user.id
        
        user_sessions[user_id] = {
            'main_forwards': 0,
            'secondary_forwards': 0,
            'session_id': db.start_forward_session(user_id)
        }
        
        forward_msg = f"""
📤 **STEP 1: Forward this channel**

**Channel to forward:** {MAIN_CHANNEL}

🎯 **How to do it:**
1. Click the link above
2. Press the "Forward" button in Telegram
3. Send it to **3 different people** you chat with

⚠️ **IMPORTANT:** Use Telegram's forward feature, don't just copy the link!

Hit "Done" when you've forwarded to 3 people:
        """
        
        keyboard = [[InlineKeyboardButton("✅ Forwarded to 3 People", callback_data="forward_main_done")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(forward_msg, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Erreur start_forward_process: {e}")

async def handle_main_forward_done(query, context):
    try:
        user_id = query.from_user.id
        
        if user_id in user_sessions:
            user_sessions[user_id]['main_forwards'] = 3
            db.update_forwards(user_id, main_forwards=3)
        
        forward_msg2 = f"""
📤 **STEP 2: Forward also this channel**

**Channel to forward:** {SECONDARY_CHANNEL}

🎯 **Forward this channel to the same 3 people**

Same process: Use Telegram's forward button and send to 3 contacts.

Hit "Done" when finished:
        """
        
        keyboard = [[InlineKeyboardButton("✅ Also Forwarded to 3 People", callback_data="forward_secondary_done")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(forward_msg2, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Erreur handle_main_forward_done: {e}")

async def handle_secondary_forward_done(query, context):
    try:
        user_id = query.from_user.id
        
        if user_id in user_sessions:
            user_sessions[user_id]['secondary_forwards'] = 3
            db.update_forwards(user_id, secondary_forwards=3)
        
        ready_msg = """
🔓 **Both forwards completed!**

✅ Main channel forwarded
✅ Secondary channel forwarded

Ready to unlock your premium access?
        """
        
        keyboard = [[InlineKeyboardButton("🔓 UNLOCK ACCESS", callback_data="check_access")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(ready_msg, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Erreur handle_secondary_forward_done: {e}")

async def check_access_with_failure(query, context):
    try:
        user_id = query.from_user.id
        
        checking_msg = """
🔍 **Verifying your forwards...**

Checking if your contacts received the channels...

Please wait...
        """
        
        await query.edit_message_text(checking_msg)
        await asyncio.sleep(random.uniform(3, 7))
        
        success = random.randint(1, 100) <= 20
        
        if success:
            db.record_success(user_id)
            
            success_msg = f"""
🎉 **ACCESS GRANTED!**

✅ **Verification successful**
🔓 **Premium unlocked**

🎁 **Your exclusive access:**
{PREMIUM_GROUP}

**Valid for 48 hours** - enjoy! 🚀
            """
            
            await query.edit_message_text(success_msg)
            
            if ADMIN_CHAT_ID:
                await context.bot.send_message(
                    ADMIN_CHAT_ID,
                    f"✅ User {query.from_user.first_name} successfully unlocked access!"
                )
        
        else:
            db.record_failure(user_id)
            
            failure_messages = [
                """
❌ **Forwards not fully detected**

🔍 **Only 2 out of 3 forwards verified**

💡 **Quick fix:**
• Make sure your contacts actually opened the links
• Try forwarding to more active contacts
• Wait 2-3 minutes between forwards

Most people succeed on the 2nd try! 💪
                """,
                """
❌ **Verification incomplete**

⚠️ **Some forwards still processing**

🎯 **Try this:**
• Forward to different contacts
• Ask your contacts to actually click the links
• Make sure they spend a few seconds viewing

You're almost there! 🔥
                """,
                """
❌ **Partial verification**

📱 **System detected some forwards but not all**

✨ **Pro tip:**
• Forward to your most active contacts
• Add a personal message when forwarding
• Try forwarding to group chats too

89% succeed within 3 attempts! 🚀
                """
            ]
            
            failure_msg = random.choice(failure_messages)
            
            keyboard = [[InlineKeyboardButton("🔄 Try Again", callback_data="retry_check")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(failure_msg, reply_markup=reply_markup)
            
    except Exception as e:
        logger.error(f"Erreur check_access_with_failure: {e}")

async def handle_admin_message(update: Update, context):
    global ADMIN_CHAT_ID
    
    try:
        user = update.effective_user
        if user and user.username and user.username.lower() == ADMIN_USERNAME.lower():
            ADMIN_CHAT_ID = update.effective_chat.id
            await update.message.reply_text("✅ Admin activated. You'll receive notifications.")
        else:
            await update.message.reply_text("👋 Hi! Use /start to begin.")
    except Exception as e:
        logger.error(f"Erreur handle_admin_message: {e}")

# Fonction pour garder le bot actif sur Render
async def keep_alive():
    while True:
        await asyncio.sleep(300)  # 5 minutes
        logger.info("Bot is alive...")

def main():
    try:
        application = Application.builder().token(TOKEN_BOT1).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(ChatJoinRequestHandler(handle_join_request))
        application.add_handler(MessageHandler(filters.TEXT & filters.PRIVATE, handle_admin_message))
        
        logger.info("🚀 VIRAL BOT 1 STARTING...")
        logger.info("📤 Features: Forced forwarding, viral propagation, 80% failure rate")
        logger.info("🎯 Goal: Maximum viral spread of Telegram channels")
        
        # Démarrer le keep alive en arrière-plan
        asyncio.create_task(keep_alive())
        
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Erreur critique: {e}")
        print(f"❌ Erreur lors du démarrage du bot: {e}")

if __name__ == "__main__":
    main()
              
