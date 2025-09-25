# /opt/project/bot1.py  (corrigé)
import logging
import random
import asyncio
import sqlite3
import os
import time                     # <-- ajouté : fix NameError time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ChatJoinRequestHandler, MessageHandler, filters
from telegram.error import TelegramError

# Configuration
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
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_contacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        contact_user_id INTEGER,
                        contact_username TEXT,
                        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logger.info("Base de données initialisée avec succès")
        except Exception as e:
            logger.error(f"Erreur init DB: {e}")

    # ... méthodes inchangées (omises ici pour concision, mais gardez celles de l'original) ...
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

# (Toutes les fonctions async restent identiques — laisse-les en l'état)
# ... start(), handle_join_request(), handle_callback(), etc. ...

async def handle_admin_message(update: Update, context):
    global ADMIN_CHAT_ID
    try:
        user = update.effective_user
        if user and user.username and user.username.lower() == ADMIN_USERNAME.lower():
            ADMIN_CHAT_ID = update.effective_chat.id
            await update.message.reply_text("Admin configuré!")
            logger.info(f"Admin chat ID set: {ADMIN_CHAT_ID}")
    except Exception as e:
        logger.error(f"Erreur handle_admin_message: {e}")

def main():
    try:
        application = Application.builder().token(TOKEN_BOT1).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(ChatJoinRequestHandler(handle_join_request))
        application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_admin_message))

        print("🚀 Bot1 démarré avec succès!")
        application.run_polling(drop_pending_updates=True, timeout=60)

    except Exception as e:
        print(f"❌ Erreur Bot1: {e}")
        time.sleep(10)  # <-- time import fixe le crash ici

if __name__ == '__main__':
    main()
