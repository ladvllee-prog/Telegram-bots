import logging
import random
import asyncio
import sqlite3
import os
import time
import traceback
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
🔥 **Hey {user.first_name}!** 👋

✨ **Want access to our exclusive private group?**

🎯 **Simple task:** Forward our channels to get instant access.

💎 **What you'll get:**
• Premium content
• Exclusive leaks
• VIP community access

Ready to unlock premium content?
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Start Task", callback_data="start_forwards")],
            [InlineKeyboardButton("📱 What's Inside?", callback_data="preview_content")]
        ]
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
🎉 **Welcome {user.first_name}!** 

🎯 **Quick task to access our private group:**

Complete this simple forwarding task to unlock exclusive content.

⏱️ **Takes 2 minutes, totally worth it!** 🔥

Ready?
        """
        
        keyboard = [
            [InlineKeyboardButton("📤 Start Forwarding", callback_data="start_forwards")],
            [InlineKeyboardButton("❓ How it Works", callback_data="how_it_works")]
        ]
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
        elif query.data == "preview_content":
            await show_content_preview(query, context)
        elif query.data == "how_it_works":
            await show_how_it_works(query, context)
        elif query.data == "back_to_start":
            await start_forward_process(query, context)
        elif query.data == "auto_forward_main":
            await handle_auto_forward_main(query, context)
        elif query.data == "manual_forward_main":
            await handle_manual_forward_main(query, context)
        elif query.data == "forward_main_done":
            await handle_main_forward_done(query, context)
        elif query.data == "start_secondary_forward":
            await start_secondary_forward(query, context)
        elif query.data == "auto_forward_secondary":
            await handle_auto_forward_secondary(query, context)
        elif query.data == "manual_forward_secondary":
            await handle_manual_forward_secondary(query, context)
        elif query.data == "forward_secondary_done":
            await handle_secondary_forward_done(query, context)
        elif query.data == "check_access":
            await check_access_with_failure(query, context)
        elif query.data == "retry_check":
            await check_access_with_failure(query, context)
            
    except Exception as e:
        logger.error(f"Erreur callback: {e}")

async def show_content_preview(query, context):
    try:
        preview_msg = """
🎁 **What's Inside Our Private Group:**

🔥 **Exclusive Content:**
• Premium leaked content
• VIP member discussions
• Early access to new releases

💎 **Community Benefits:**
• Active daily updates
• Request any content
• Premium support

🚀 **Ready to join?**
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 Start Task Now", callback_data="start_forwards")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(preview_msg, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Erreur show_content_preview: {e}")

async def show_how_it_works(query, context):
    try:
        how_msg = """
📖 **How It Works:**

🎯 **Step 1:** Forward main channel to 3 contacts
🎯 **Step 2:** Forward secondary channel to 3 contacts
🎯 **Step 3:** Get verified and unlock access

💡 **Tips for Success:**
• Use active contacts who will actually view
• Forward to people interested in this content
• Complete both steps for instant access

⏱️ **Total time:** 2-3 minutes

Ready to start?
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Let's Go!", callback_data="start_forwards")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(how_msg, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Erreur show_how_it_works: {e}")

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

🎯 **Choose your method:**

🤖 **Option 1:** Auto-Forward (Recommended ⭐)
• Bot forwards directly to your recent contacts
• Quick and automatic

👤 **Option 2:** Manual Forward
• You forward manually to 3 people
• Traditional method

Choose your preferred option:
        """
        
        keyboard = [
            [InlineKeyboardButton("🤖 Auto-Forward", callback_data="auto_forward_main")],
            [InlineKeyboardButton("👤 Manual Forward", callback_data="manual_forward_main")],
            [InlineKeyboardButton("❓ Need Help", callback_data="how_it_works")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(forward_msg, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Erreur start_forward_process: {e}")
async def handle_auto_forward_main(query, context):
    try:
        user_id = query.from_user.id
        
        processing_msg = """
🤖 **Auto-Forward in Progress...**

🔄 Analyzing your recent contacts...
📤 Selecting 3 active contacts...
⏳ Forwarding now...

Please wait...
        """
        
        await query.edit_message_text(processing_msg)
        await asyncio.sleep(random.uniform(2, 4))
        
        forward_message = f"""
🔥 **Check out this amazing channel!**

{MAIN_CHANNEL}

Incredible content here! 🚀
        """
        
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📤 **Auto-forwarded message preview:**\n\n{forward_message}"
            )
            
            success = True
        except Exception as e:
            logger.error(f"Erreur auto-forward: {e}")
            success = False
        
        if success:
            if user_id in user_sessions:
                user_sessions[user_id]['main_forwards'] = 3
                db.update_forwards(user_id, main_forwards=3)
            
            progress_msg = """
✅ **Auto-Forward Completed!**

📤 **Successfully forwarded to 3 contacts:**
• Contact 1: ✅ Delivered
• Contact 2: ✅ Delivered  
• Contact 3: ✅ Delivered

🎯 **Step 1 Complete! Ready for Step 2!**
            """
            
            keyboard = [
                [InlineKeyboardButton("➡️ Continue to Step 2", callback_data="start_secondary_forward")],
                [InlineKeyboardButton("📊 View Progress", callback_data="show_progress")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(progress_msg, reply_markup=reply_markup)
        else:
            await handle_manual_forward_main(query, context)
            
    except Exception as e:
        logger.error(f"Erreur handle_auto_forward_main: {e}")
        await handle_manual_forward_main(query, context)

async def handle_manual_forward_main(query, context):
    try:
        forward_msg = f"""
📤 **STEP 1: Forward this channel (Manual)**

**Channel to forward:** {MAIN_CHANNEL}

🎯 **Instructions:**
1. Click the link above
2. Press the "Forward" button in Telegram
3. Send it to **3 different people** you chat with

⚠️ **IMPORTANT:** Use Telegram's forward feature, don't just copy the link!

💡 **Tips:**
• Choose active contacts
• Add a personal message if you want

Hit "Done" when you've forwarded to 3 people:
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Forwarded to 3 People", callback_data="forward_main_done")],
            [InlineKeyboardButton("🤖 Try Auto-Forward", callback_data="auto_forward_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(forward_msg, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Erreur handle_manual_forward_main: {e}")

async def handle_main_forward_done(query, context):
    try:
        user_id = query.from_user.id
        
        if user_id in user_sessions:
            user_sessions[user_id]['main_forwards'] = 3
            db.update_forwards(user_id, main_forwards=3)
        
        await start_secondary_forward(query, context)
        
    except Exception as e:
        logger.error(f"Erreur handle_main_forward_done: {e}")

async def start_secondary_forward(query, context):
    try:
        forward_msg2 = f"""
📤 **STEP 2: Forward this channel**

**Channel to forward:** {SECONDARY_CHANNEL}

🎯 **Choose your method:**

🤖 **Option 1:** Auto-Forward (Recommended ⭐)
• Bot forwards directly to your contacts
• Quick and automatic

👤 **Option 2:** Manual Forward  
• You forward manually to 3 people
• Traditional method

Almost done! Choose your option:
        """
        
        keyboard = [
            [InlineKeyboardButton("🤖 Auto-Forward", callback_data="auto_forward_secondary")],
            [InlineKeyboardButton("👤 Manual Forward", callback_data="manual_forward_secondary")],
            [InlineKeyboardButton("📊 My Progress", callback_data="show_progress")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(forward_msg2, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Erreur start_secondary_forward: {e}")

async def handle_auto_forward_secondary(query, context):
    try:
        user_id = query.from_user.id
        
        processing_msg = """
🤖 **Auto-Forward Step 2 in Progress...**

🔄 Forwarding secondary channel...
📤 Sending to the same 3 contacts...
⏳ Almost done...

Final step processing...
        """
        
        await query.edit_message_text(processing_msg)
        await asyncio.sleep(random.uniform(2, 4))
        
        forward_message = f"""
🔥 **Another amazing channel for you!**

{SECONDARY_CHANNEL}

Even more exclusive content! 🎁
        """
        
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📤 **Auto-forwarded message preview (Step 2):**\n\n{forward_message}"
            )
            
            success = True
        except Exception as e:
            logger.error(f"Erreur auto-forward secondary: {e}")
            success = False
        
        if success:
            if user_id in user_sessions:
                user_sessions[user_id]['secondary_forwards'] = 3
                db.update_forwards(user_id, secondary_forwards=3)
            
            ready_msg = """
🔓 **Both Auto-Forwards Completed!**

✅ **Main channel:** Auto-forwarded to 3 contacts
✅ **Secondary channel:** Auto-forwarded to 3 contacts

📊 **Forward Summary:**
• Total forwards: 6
• Success rate: 100%
• Method: Automatic

🚀 **Ready to unlock your private group access?**
            """
            
            keyboard = [
                [InlineKeyboardButton("🔓 UNLOCK ACCESS", callback_data="check_access")],
                [InlineKeyboardButton("📊 View Stats", callback_data="show_progress")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(ready_msg, reply_markup=reply_markup)
        else:
            await handle_manual_forward_secondary(query, context)
            
    except Exception as e:
        logger.error(f"Erreur handle_auto_forward_secondary: {e}")
        await handle_manual_forward_secondary(query, context)

async def handle_manual_forward_secondary(query, context):
    try:
        forward_msg2 = f"""
📤 **STEP 2: Forward this channel (Manual)**

**Channel to forward:** {SECONDARY_CHANNEL}

🎯 **Forward this channel to the same 3 people**

Same process: Use Telegram's forward button and send to 3 contacts.

💡 **Almost there!** Just one more step.

Hit "Done" when finished:
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Also Forwarded to 3 People", callback_data="forward_secondary_done")],
            [InlineKeyboardButton("🤖 Try Auto-Forward", callback_data="auto_forward_secondary")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(forward_msg2, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Erreur handle_manual_forward_secondary: {e}")

async def handle_secondary_forward_done(query, context):
    try:
        user_id = query.from_user.id
        
        if user_id in user_sessions:
            user_sessions[user_id]['secondary_forwards'] = 3
            db.update_forwards(user_id, secondary_forwards=3)
        
        ready_msg = """
🔓 **Both forwards completed!**

✅ **Main channel forwarded**
✅ **Secondary channel forwarded**

🎯 **Task Summary:**
• Total forwards: 6
• Both channels shared
• Ready for verification

**Ready to unlock your private group access?**
        """
        
        keyboard = [
            [InlineKeyboardButton("🔓 UNLOCK ACCESS", callback_data="check_access")],
            [InlineKeyboardButton("📊 My Stats", callback_data="show_progress")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(ready_msg, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Erreur handle_secondary_forward_done: {e}")

async def check_access_with_failure(query, context):
    try:
        user_id = query.from_user.id
        
        checking_msg = """
🔍 **Verifying your forwards...**

🤖 Checking if your contacts received the channels...
📊 Analyzing engagement patterns...
⏳ Verification in progress...

Please wait...
        """
        
        await query.edit_message_text(checking_msg)
        await asyncio.sleep(random.uniform(3, 7))
        
        # 5% success rate as requested
        success = random.randint(1, 100) <= 5
        
        if success:
            db.record_success(user_id)
            
            success_msg = f"""
🎉 **ACCESS GRANTED!**

✅ **Verification successful**
🔓 **Private group unlocked**

🎁 **Your exclusive access:**
{PREMIUM_GROUP}

💎 **Valid for 48 hours** - enjoy! 🚀

Welcome to the premium community!
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

💪 **Most people succeed on the 2nd try!**
                """,
                """
❌ **Verification incomplete**

⚠️ **Some forwards still processing**

🎯 **Try this:**
• Forward to different contacts
• Ask your contacts to actually click the links
• Make sure they spend a few seconds viewing

🔥 **You're almost there!**
                """,
                """
❌ **Partial verification**

📱 **System detected some forwards but not all**

✨ **Pro tip:**
• Forward to your most active contacts
• Add a personal message when forwarding
• Try forwarding to group chats too

🚀 **89% succeed within 3 attempts!**
                """
            ]
            
            failure_msg = random.choice(failure_messages)
            
            keyboard = [
                [InlineKeyboardButton("🔄 Try Again", callback_data="retry_check")],
                [InlineKeyboardButton("💡 Get Tips", callback_data="how_it_works")]
            ]
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
        time.sleep(10)  # Attendre avant de crash

if __name__ == '__main__':
    main()
        
