import logging
import random
import asyncio
import sqlite3
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ChatJoinRequestHandler, MessageHandler, filters

# Configuration
TOKENBOT2 = os.getenv("BOT2_TOKEN")
if not TOKENBOT2:
    raise RuntimeError("BOT2_TOKEN not set in environment")

LINKTREEURL = "https://linktr.ee/Forfreeleaks"
PREMIUMGROUP = "https://t.me/XJTRENbFij4xN2Zk"
EXCLUSIVEGROUPID = None
ADMINUSERNAME = "lympidleaks"
ADMINCHATID = None

DATABASEFILE = "viralbot2.db"
PORT = int(os.environ.get("PORT", 8001))

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialViralDatabase:
    def __init__(self):
        self.init_db()

    def init_db(self):
        try:
            with sqlite3.connect(DATABASEFILE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        userid INTEGER PRIMARY KEY,
                        username TEXT,
                        firstname TEXT,
                        joindate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        socialvisits INTEGER DEFAULT 0,
                        successfulunlocks INTEGER DEFAULT 0,
                        failedattempts INTEGER DEFAULT 0,
                        totalrequests INTEGER DEFAULT 0
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS modelrequests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        userid INTEGER,
                        requestdetails TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'pending'
                    )
                ''')
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")

    def create_user(self, userid, username=None, firstname=None):
        try:
            with sqlite3.connect(DATABASEFILE) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO users (userid, username, firstname) VALUES (?, ?, ?)", (userid, username, firstname))
                conn.commit()
        except Exception as e:
            logger.error(f"Error creating user: {e}")

    def record_visit(self, userid):
        try:
            with sqlite3.connect(DATABASEFILE) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET socialvisits = socialvisits + 1 WHERE userid = ?", (userid,))
                conn.commit()
        except Exception as e:
            logger.error(f"Error recording social visit: {e}")

    def record_success(self, userid):
        try:
            with sqlite3.connect(DATABASEFILE) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET successfulunlocks = successfulunlocks + 1 WHERE userid = ?", (userid,))
                conn.commit()
        except Exception as e:
            logger.error(f"Error recording success: {e}")

    def record_failure(self, userid):
        try:
            with sqlite3.connect(DATABASEFILE) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET failedattempts = failedattempts + 1 WHERE userid = ?", (userid,))
                conn.commit()
        except Exception as e:
            logger.error(f"Error recording failure: {e}")

    def add_request(self, userid, requestdetails):
        try:
            with sqlite3.connect(DATABASEFILE) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO modelrequests (userid, requestdetails) VALUES (?, ?)", (userid, requestdetails))
                cursor.execute("UPDATE users SET totalrequests = totalrequests + 1 WHERE userid = ?", (userid,))
                conn.commit()
        except Exception as e:
            logger.error(f"Error adding request: {e}")

db = SocialViralDatabase()
user_sessions = {}
last_group_response = {}

welcome_msg = f"""
Hi {user.first_name}! 👋

To request any model content, complete this simple task first.

Visit our social media and engage for premium access.
follow, like comments repost and all the regular stuff...

Ready? Click below to start the task. 🚀
"""
        keyboard = [[InlineKeyboardButton("Start Task", callback_data="start_social_task")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup)
        logger.info(f"Bot2 - New user {user.first_name} ({userid})")
    except Exception as e:
        logger.error(f"Error in start handler: {e}")

async def handle_join_request(update: Update, context):
    try:
        chat_id = update.chat_join_request.chat.id
        user = update.chat_join_request.from_user
        userid = user.id
        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=userid)
        db.create_user(userid, user.username, user.first_name)

        join_msg = f"""
Welcome {user.first_name}! 🎉

Request any model you want, but first complete a quick social media task.
push every button, follow, comment, like, repost and zll the regular stuff its quick !!

Click below to start.
"""
        keyboard = [[InlineKeyboardButton("Start Social Task", callback_data="start_social_task")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=userid, text=join_msg, reply_markup=reply_markup)

        if ADMINCHATID:
            await context.bot.send_message(ADMINCHATID, f"New join request approved: {user.first_name} (id {userid})")
    except Exception as e:
        logger.error(f"Error handling join request: {e}")

async def handle_callback(update: Update, context):
    try:
        query = update.callback_query
        userid = query.from_user.id
        await query.answer()
        data = query.data

        if data == "start_social_task":
            await start_social_engagement(query, context)
        elif data == "visited_socials":
            await handle_social_visited(query, context)
        elif data == "verify_access":
            await verify_social_engagement(query, context)
        elif data == "retry_verification":
            await verify_social_engagement(query, context)
    except Exception as e:
        logger.error(f"Error handling callback query: {e}")

async def start_social_engagement(query, context):
    try:
        userid = query.from_user.id
        user_sessions[userid] = {"social_clicked": False, "engagement_quality": 0}

        msg = (
            "Social Media Engagement Task:
"
            f"Visit and engage here: {LINKTREEURL}

"
            "What you should do:
"
            "- Follow our accounts on multiple platforms
"
            "- Like and comment on posts this will be your proof of commitment and obviously
"
            "- Spend at least 1 minute engaging
"
            "Genuine engagement is required!

"
            "Click 'I've Engaged' when done."
        )
        keyboard = [
            [InlineKeyboardButton("Open Social Media", url=LINKTREEURL)],
            [InlineKeyboardButton("I've Engaged", callback_data="visited_socials")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in start_social_engagement: {e}")

async def handle_social_visited(query, context):
    try:
        userid = query.from_user.id
        db.record_visit(userid)
        user_sessions[userid]["social_clicked"] = True

        verify_msg = (
            "Checking your engagement...
"
            "Analyzing social activity...
"
            "Ready for verification?"
        )
        keyboard = [[InlineKeyboardButton("Verify Access", callback_data="verify_access")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(verify_msg, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in handle_social_visited: {e}")

async def verify_social_engagement(query, context):
    try:
        userid = query.from_user.id
        checking_msg = "Running advanced verification...
Please wait..."
        await query.edit_message_text(checking_msg)
        await asyncio.sleep(random.uniform(4, 8))

        # 95% failure rate even if conditions met
        success = random.randint(1, 100) > 95  # 5% success chance

        if success:
            db.record_success(userid)
            success_msg = (
                "VERIFICATION SUCCESSFUL!
"
                "Social engagement confirmed.

"
                f"Premium access granted: {PREMIUMGROUP}
"
                "Enjoy your exclusive content!"
            )
            await query.edit_message_text(success_msg)
            if ADMINCHATID:
                await context.bot.send_message(ADMINCHATID, f"User {query.from_user.first_name} unlocked access in Bot2.")
        else:
            db.record_failure(userid)
            failure_msgs = [
                "No sufficient social activity detected.",
                "Access is currently limited.",
                "Try engaging more with our social channels.",
                "Spend more time liking and commenting.",
                "Most users succeed on the 2nd or 3rd try!"
            ]
            failure_msg = (
                "VERIFICATION FAILED

"
                f"{random.choice(failure_msgs)}

"
                "Please try again!"
            )
            keyboard = [
                [InlineKeyboardButton("Engage More", url=LINKTREEURL)],
                [InlineKeyboardButton("Try Again", callback_data="retry_verification")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(failure_msg, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in verify_social_engagement: {e}")

async def handle_group_messages(update, context):
    global EXCLUSIVEGROUPID
    try:
        if not update.effective_chat or not update.effective_user:
            return
        if EXCLUSIVEGROUPID is None:
            EXCLUSIVEGROUPID = update.effective_chat.id
            logger.info(f"Exclusive group ID set to {EXCLUSIVEGROUPID}")
        if update.effective_chat.id != EXCLUSIVEGROUPID:
            return
        if update.effective_user.is_bot:
            return
        current_time = datetime.now()
        if EXCLUSIVEGROUPID in last_group_response and (current_time - last_group_response[EXCLUSIVEGROUPID]).seconds < 30:
            return
        last_group_response[EXCLUSIVEGROUPID] = current_time

        autoresponse = (
            "Want to request another model?

"
            "Complete the social engagement task again!
"
            "Just message me privately and follow the instructions."
        )
        keyboard = [
            [InlineKeyboardButton("Message Bot", url=f"http://t.me/{context.bot.username}")],
            [InlineKeyboardButton("Social Media", url=LINKTREEURL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await asyncio.sleep(random.uniform(1, 3))
        await context.bot.send_message(chat_id=EXCLUSIVEGROUPID, text=autoresponse, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in handle_group_messages: {e}")

async def handle_model_requests(update, context):
    try:
        if update.effective_chat.type != "private":
            return
        userid = update.effective_user.id
        message_text = update.message.text.lower()

        request_keywords = ["request", "want", "need", "model", "content", "send", "get"]

        if any(keyword in message_text for keyword in request_keywords):
            db.add_request(userid, update.message.text)
            response = (
                "Model request noted!
"
                "To process your request, complete the social engagement task again.
"
                "Ready?"
            )
            keyboard = [[InlineKeyboardButton("Start Task", callback_data="start_social_task")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(response, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error handling model requests: {e}")

async def keep_alive():
    while True:
        await asyncio.sleep(300)
        logger.info("Bot2 is alive...")

async def handle_admin_message(update: Update, context):
    global ADMIN_CHAT_ID

ADMIN_CHAT_ID = update.effective_chat.id
        if user and user.username and user.username.lower() == ADMINUSERNAME.lower():
            ADMINCHATID = update.effective_chat.id
            await update.message.reply_text("Admin activated. You will receive notifications.")
        else:
            await update.message.reply_text("Hi! Use /start to begin.")
    except Exception as e:
        logger.error(f"Error handling admin message: {e}")

def main():
    try:
        app = Application.builder().token(TOKENBOT2).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(handle_callback))
        app.add_handler(ChatJoinRequestHandler(handle_join_request))
        app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_messages))
        app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_admin_message))
        app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_model_requests))
        app.loop.create_task(keep_alive())
        logger.info("Viral Bot 2 Starting...")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"Critical error: {e}")
        print("Failed to start bot.")

if __name__ == "__main__":
    main()
