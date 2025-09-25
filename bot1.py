import logging
import random
import asyncio
import sqlite3
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ChatJoinRequestHandler, MessageHandler, filters

# Configuration
TOKENBOT1 = os.getenv("BOT1_TOKEN")
if not TOKENBOT1:
    raise RuntimeError("BOT1_TOKEN not set in environment")

MAINCHANNEL = "https://t.me/35cFwPP5dJ42ODM0"
SECONDARYCHANNEL = "https://t.me/Agt0dHQXZHc3Mzgo"
PREMIUMGROUP = "https://t.me/Agt0dHQXZHc3Mzgo"
ADMINUSERNAME = "lympidleaks"
ADMINCHATID = None  # Set admin chat ID if needed

DATABASE_FILE = "viral_bot1.db"
PORT = int(os.environ.get("PORT", 8000))

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
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
                    firstname TEXT,
                    joindate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    forwardsdone INTEGER DEFAULT 0,
                    successfulunlocks INTEGER DEFAULT 0,
                    failedattempts INTEGER DEFAULT 0,
                    totalviralimpact INTEGER DEFAULT 0
                )
                ''')
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS forwardsessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    userid INTEGER,
                    sessionstart TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    mainchannelforwards INTEGER DEFAULT 0,
                    secondarychannelforwards INTEGER DEFAULT 0,
                    sessioncompleted BOOLEAN DEFAULT 0
                )
                ''')
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")

    def create_user(self, userid, username=None, firstname=None):
        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO users (user_id, username, firstname) VALUES (?, ?, ?)", (userid, username, firstname))
                conn.commit()
        except Exception as e:
            logger.error(f"Error creating user: {e}")

    def start_forward_session(self, userid):
        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO forwardsessions (userid) VALUES (?)", (userid,))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error starting forward session: {e}")
            return None

    def update_forwards(self, userid, mainforwards=0, secondaryforwards=0):
        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET forwardsdone = forwardsdone + ? WHERE user_id = ?", (mainforwards + secondaryforwards, userid))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating forwards: {e}")

    def record_success(self, userid):
        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET successfulunlocks = successfulunlocks + 1, totalviralimpact = totalviralimpact + 50 WHERE user_id = ?", (userid,))
                conn.commit()
        except Exception as e:
            logger.error(f"Error recording success: {e}")

    def record_failure(self, userid):
        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET failedattempts = failedattempts + 1 WHERE user_id = ?", (userid,))
                conn.commit()
        except Exception as e:
            logger.error(f"Error recording failure: {e}")

db = ViralDatabase()
user_sessions = {}

async def start(update: Update, context):
    try:
        user = update.effective_user
        userid = user.id
        db.create_user(userid, user.username, user.first_name)
        welcome_msg = (
    f"Hello {user.first_name}!\n\n"
    "To join our exclusive private group, please complete the following task:\n"
    "You need to forward both channels to 3 different contacts each.\n"
    "Use Telegram’s forward button, don’t just copy links.\n\n"
    "Ready? Click the button below to begin automatic forwarding."
        )
        keyboard = [[InlineKeyboardButton("Start Automatic Forwarding", callback_data="start_auto_forward")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup)
        logger.info(f"New user {user.first_name} ({userid}) started interaction.")
    except Exception as e:
        logger.error(f"Error in start handler: {e}")

async def handle_join_request(update: Update, context):
    try:
        chat_id = update.chat_join_request.chat.id
        user = update.chat_join_request.from_user
        userid = user.id
        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=userid)
        db.create_user(user_id, user.username, user.first_name)

        welcome_msg = (
            f"Hey {user.first_name}! 👋\n\n"
            "🔥 Want exclusive premium content?\n\n"
            "Simple task: Forward our channels to unlock instant access to amazing content.\n\n"
            "Make any request of any model you want but first complete this quick task 🎯\n\n"
            "Ready to get started?"
        )

        keyboard = [[InlineKeyboardButton("🚀 Start Task", callback_data="start_forwards")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(welcome_msg, reply_markup=reply_markup)
        logger.info(f"Nouvel utilisateur: {user.first_name} ({user_id})")

        if ADMINCHATID:
            await context.bot.send_message(ADMINCHATID, f"New join request approved: {user.first_name} ({user.username or 'no username'}) id {userid}")
    except Exception as e:
        logger.error(f"Error handling join request: {e}")

async def handle_callback_query(update: Update, context):
    try:
        query = update.callback_query
        userid = query.from_user.id
        await query.answer()
        data = query.data

        if data == "start_auto_forward":
            await start_auto_forward(query, context)
        elif data == "done_main_forward":
            await done_main_forward(query, context)
        elif data == "done_secondary_forward":
            await done_secondary_forward(query, context)
        elif data == "check_access":
            await check_access(query, context)
        elif data == "retry_check":
            await check_access(query, context)
    except Exception as e:
        logger.error(f"Error handling callback query: {e}")

async def start_auto_forward(query, context):
    try:
        userid = query.from_user.id
        user_sessions[userid] = {"mainforwards": 0, "secondaryforwards": 0, "sessionid": db.start_forward_session(userid)}

        msg = (
            f"Step 1: Forward this channel:
{MAINCHANNEL}

"
            "How to forward:
"
            "1. Click the link above.
"
            "2. Use Telegram's forward button (do not copy-paste).
"
            "3. Forward to 3 different contacts.

"
            "When done, click the button below."
        )
        keyboard = [[InlineKeyboardButton("Done Forwarding Main Channel", callback_data="done_main_forward")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in start_auto_forward: {e}")

async def done_main_forward(query, context):
    try:
        userid = query.from_user.id
        if userid in user_sessions:
            user_sessions[userid]["mainforwards"] = 3
            db.update_forwards(userid, mainforwards=3)
            msg = (
                f"Step 2: Now forward this channel:
{SECONDARYCHANNEL}

"
                "Repeat the same forwarding steps:
"
                "Use Telegram's forward button to 3 different contacts.

"
                "Once done, click the button below."
            )
            keyboard = [[InlineKeyboardButton("Done Forwarding Secondary Channel", callback_data="done_secondary_forward")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(msg, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in done_main_forward: {e}")

async def done_secondary_forward(query, context):
    try:
        userid = query.from_user.id
        if userid in user_sessions:
            user_sessions[userid]["secondaryforwards"] = 3
            db.update_forwards(userid, secondaryforwards=3)
            msg = (
                "Great! Both forwards completed.

"
                "Ready to unlock your premium access?"
            )
            keyboard = [[InlineKeyboardButton("Unlock Access", callback_data="check_access")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(msg, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in done_secondary_forward: {e}")

async def check_access(query, context):
    try:
        userid = query.from_user.id
        checking_msg = "Verifying your forwards...
Please wait..."
        await query.edit_message_text(checking_msg)
        await asyncio.sleep(random.uniform(3, 6))

        # 95% failure rate to simulate strict control and encourage retries
        success = random.randint(1, 100) > 95  # 5% success chance

        if success:
            db.record_success(userid)
            success_msg = (
                "ACCESS GRANTED!
"
                "Verification successful.

"
                f"Here is your exclusive access link: {PREMIUMGROUP}
"
                "Valid for 48 hours. Enjoy!"
            )
            await query.edit_message_text(success_msg)
            if ADMINCHATID:
                await context.bot.send_message(ADMINCHATID, f"User {query.from_user.first_name} unlocked access successfully.")
        else:
            db.record_failure(userid)
            failure_msgs = [
                "Some forwards were not detected.",
                "Access is currently limited.",
                "Try forwarding to more active contacts.",
                "Wait a few minutes between attempts.",
                "Keep trying! Most succeed in 2-3 tries."
            ]
            failure_msg = (
                "ACCESS DENIED

"
                f"{random.choice(failure_msgs)}

"
                "Don't give up, try again!"
            )
            keyboard = [[InlineKeyboardButton("Try Again", callback_data="retry_check")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(failure_msg, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in check_access: {e}")

async def handle_admin_message(update: Update, context):
    global ADMINCHATID
    try:
        user = update.effective_user
        if user and user.username and user.username.lower() == ADMIN_USERNAME.lower():
            ADMINCHATID = update.effective_chat.id
            await update.message.reply_text("✅ Admin activated. Notifications enabled.")
        else:
            await update.message.reply_text("👋 Hi! Use /start to begin.")
    except Exception as e:
        logger.error(f"Error handling admin message: {e}")

def main():
    try:
        app = Application.builder().token(TOKENBOT1).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(handle_callback_query))
        app.add_handler(ChatJoinRequestHandler(handle_join_request))
        app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_admin_message))
        logger.info("Viral Bot1 started")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"Critical error on start: {e}")
        print("Bot failed to start.")

async def keep_alive():
    while True:
        await asyncio.sleep(300)
        logger.info("Bot1 is alive...")

if __name__ == "__main__":
    main()              
