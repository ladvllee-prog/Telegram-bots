import logging
import random
import asyncio
import sqlite3
import os
import time
import traceback
# -- debug runtime info (leave for now) --
import sys
import logging
try:
    import importlib.metadata as _md
except Exception:
    import importlib_metadata as _md

logger = logging.getLogger(__name__)
try:
    logger.info("DEBUG-RUNTIME python: %s", sys.version.replace("\n"," "))
    try:
        v = _md.version("python-telegram-bot")
    except Exception as e:
        v = f"not-found ({e})"
    logger.info("DEBUG-RUNTIME python-telegram-bot: %s", v)
    try:
        import telegram as _tg
        logger.info("DEBUG-RUNTIME telegram module file: %s", getattr(_tg, "__file__", "unknown"))
        logger.info("DEBUG-RUNTIME telegram.__version__: %s", getattr(_tg, "__version__", "no-__version__"))
    except Exception as e:
        logger.info("DEBUG-RUNTIME telegram import error: %s", e)
except Exception:
    logger.exception("DEBUG-RUNTIME failed")
# -- end debug block --
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ChatJoinRequestHandler, MessageHandler, filters

# Configuration
TOKEN_BOT2 = os.getenv("BOT2_TOKEN")
if not TOKEN_BOT2:
    raise RuntimeError("BOT2_TOKEN not set in environment")

LINKTREE_URL = "https://linktr.ee/Forfreeleaks"
PREMIUM_GROUP = "https://t.me/+XJTRENbFij4xN2Zk"
EXCLUSIVE_GROUP_ID = None
ADMIN_USERNAME = "lympidleaks"
ADMIN_CHAT_ID = None
DATABASE_FILE = "viral_bot2.db"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SocialViralDatabase:
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
                        social_visits INTEGER DEFAULT 0,
                        successful_unlocks INTEGER DEFAULT 0,
                        failed_attempts INTEGER DEFAULT 0,
                        total_requests INTEGER DEFAULT 0
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS model_requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        request_details TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'pending'
                    )
                ''')
                conn.commit()
                logger.info("Base de données 2 initialisée avec succès")
        except Exception as e:
            logger.error(f"Erreur init DB2: {e}")
    
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
            logger.error(f"Erreur create_user2: {e}")
    
    def record_visit(self, user_id):
        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET social_visits = social_visits + 1
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Erreur record_visit: {e}")
    
    def record_success(self, user_id):
        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET successful_unlocks = successful_unlocks + 1
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Erreur record_success2: {e}")
    
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
            logger.error(f"Erreur record_failure2: {e}")
    
    def add_request(self, user_id, request_details):
        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO model_requests (user_id, request_details)
                    VALUES (?, ?)
                ''', (user_id, request_details))
                cursor.execute('''
                    UPDATE users SET total_requests = total_requests + 1
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Erreur add_request: {e}")

db = SocialViralDatabase()
user_sessions = {}
last_group_response = {}

async def start(update: Update, context):
    try:
        user = update.effective_user
        user_id = user.id
        
        db.create_user(user_id, user.username, user.first_name)
        
        welcome_msg = f"""
 *yo {user.first_name}* 

💎 *my group Snapchat ~my eyes only~*

 *What you'll get:*
 surprise 🫢 

*social media engagement to unlock*

Ready?
        """
        
        keyboard = [
            [InlineKeyboardButton(" Start Task", callback_data="start_social_task")],
            [InlineKeyboardButton(" What's Available?", callback_data="show_available")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')
        logger.info(f"Bot2 - Nouvel utilisateur: {user.first_name} ({user_id})")
        
    except Exception as e:
        logger.error(f"Erreur dans start2: {e}")

async def handle_join_request(update: Update, context):
    try:
        chat_id = update.chat_join_request.chat.id
        user_id = update.chat_join_request.from_user.id
        user = update.chat_join_request.from_user
        
        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
        
        db.create_user(user_id, user.username, user.first_name)
        
        welcome_msg = f"""
 *yo {user.first_name}!*

 *Request anything you want!*

First,  social media task to unlock access then you'll fet the link

💎 *Custom content creation available!*

Simple engagement required commenting is necessary to be noticed! 
        """
        
        keyboard = [
            [InlineKeyboardButton("📱 Start Social Task", callback_data="start_social_task")],
            [InlineKeyboardButton("📋 Request Examples", callback_data="request_examples")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=user_id,
            text=welcome_msg,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in join request2: {e}")

async def handle_callback(update: Update, context):
    try:
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()
        
        if query.data == "start_social_task":
            await start_social_engagement(query, context)
        elif query.data == "show_available":
            await show_available_content(query, context)
        elif query.data == "request_examples":
            await show_request_examples(query, context)
        elif query.data == "back_to_main":
            await back_to_main_menu(query, context)
        elif query.data == "visited_socials":
            await handle_social_visit_claim(query, context)
        elif query.data == "verify_access":
            await verify_social_engagement(query, context)
        elif query.data == "retry_verification":
            await verify_social_engagement(query, context)
        elif query.data == "engagement_tips":
            await show_engagement_tips(query, context)
            
    except Exception as e:
        logger.error(f"Erreur callback2: {e}")

async def show_available_content(query, context):
    try:
        available_msg = """
 *Available Content Types:*

💎 *Premium Categories:*
• i have everything in that group you'll get Snapchat leaks

 *Ready to get access?*
        """
        
        keyboard = [
            [InlineKeyboardButton(" Start Task Now", callback_data="start_social_task")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(available_msg, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erreur show_available_content: {e}")

async def show_request_examples(query, context):
    try:
        examples_msg = """
📋 *Request Examples:*

 *Popular Requests:*
• "I want [Model Name] exclusive content"
• "Do you have [Celebrity Name] leaks?"
• "Can you get [Influencer] premium content?"
• "Looking for [Specific Model] photoshoot"

🎯 *How to Request:*
1. Complete social engagement task
2. Get access to premium group
3. Make your specific request
4. Get exclusive content delivered

Ready to start?
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Start Task", callback_data="start_social_task")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(examples_msg, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erreur show_request_examples: {e}")

async def back_to_main_menu(query, context):
    try:
        user = query.from_user
        welcome_msg = f"""
 *yo {user.first_name}!* 👋

 *Want to request any model content?*

 *Make any request of any model you want but first complete this simple task.*

Quick social media engagement needed to unlock premium access! 🚀

Ready?
        """
        
        keyboard = [
            [InlineKeyboardButton("🔗 Start Task", callback_data="start_social_task")],
            [InlineKeyboardButton("🎁 What's Available?", callback_data="show_available")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erreur back_to_main_menu: {e}")
async def start_social_engagement(query, context):
    try:
        user_id = query.from_user.id
        
        user_sessions[user_id] = {
            'start_time': datetime.now(),
            'social_clicked': False,
            'engagement_quality': 0
        }
        
        engagement_msg = f"""
 *Social Media Engagement Task*

 *Visit our social media:* {LINKTREE_URL}

 *What you need:*
• Visit the link above
• Follow our accounts on different platforms
• Like and engage with our latest posts COMMENTING IS NECESSARY TO BE NOTICED!

⚠️ *Important:* Genuine engagement is checked 

💡 *Tips for success:* 
• Actually interact with content
• Follow multiple accounts
• Leave some likes/comments

Click "Done" when you've engaged:
        """
        
        keyboard = [
            [InlineKeyboardButton("🔗 Open Social Media", url=LINKTREE_URL)],
            [InlineKeyboardButton("✅ I've Engaged", callback_data="visited_socials")],
            [InlineKeyboardButton("💡 Engagement Tips", callback_data="engagement_tips")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(engagement_msg, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erreur start_social_engagement: {e}")

async def show_engagement_tips(query, context):
    try:
        tips_msg = f"""
 *Engagement Tips for Success:*

 *What actually works:*
• Follow us on multiple platforms
• Like several posts on each platform
• Leave comments to be checked

 *Best practices:*
• Don't just click and leave immediately
• Show genuine interest in our posts

 *Pro tip:* Users who engage more get verified faster!

Visit: {LINKTREE_URL}
        """
        
        keyboard = [
            [InlineKeyboardButton("🔗 Engage Now", url=LINKTREE_URL)],
            [InlineKeyboardButton("◀️ Back to Task", callback_data="start_social_task")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(tips_msg, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erreur show_engagement_tips: {e}")

async def handle_social_visit_claim(query, context):
    try:
        user_id = query.from_user.id
        
        db.record_visit(user_id)
        
        if user_id in user_sessions:
            user_sessions[user_id]['social_clicked'] = True
        
        verification_msg = """
🔍 *Checking your engagement...*

🤖 Analyzing your social media activity...
📊 Reviewing interaction patterns...
⏳ Processing verification...

Ready for verification?
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 VERIFY ACCESS", callback_data="verify_access")],
            [InlineKeyboardButton("⏰ Wait More", callback_data="start_social_task")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(verification_msg, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erreur handle_social_visit_claim: {e}")

async def verify_social_engagement(query, context):
    try:
        user_id = query.from_user.id
        
        checking_msg = """
 *Advanced verification running...*

 Analyzing your social media engagement patterns...
 Checking interaction depth and quality...
 Cross-referencing multiple platforms...

Please wait...
        """
        
        await query.edit_message_text(checking_msg, parse_mode='Markdown')
        await asyncio.sleep(random.uniform(4, 8))
        
        # 5% success rate (95% failure rate as requested)
        success = random.randint(1, 100) <= 5
        
        if success:
            db.record_success(user_id)
            
            success_msg = f"""
🎉 *VERIFICATION SUCCESSFUL!*

✅ *Social engagement confirmed*
 *Premium access unlocked*

 *Your exclusive group:*
{PREMIUM_GROUP}

💎 *Request any model you want now!* 

Welcome to the premium community!
            """
            
            await query.edit_message_text(success_msg, parse_mode='Markdown')
            
            if ADMIN_CHAT_ID:
                await context.bot.send_message(
                    ADMIN_CHAT_ID,
                    f"✅ Bot2 User {query.from_user.first_name} successfully unlocked access!"
                )
        
        else:
            db.record_failure(user_id)
            
            failure_messages = [
                f"""
❌ *Engagement not detected*

🔍 *No sufficient activity found*

💡 *What to do:*
• Go back to: {LINKTREE_URL}
• Actually follow our accounts (don't just visit)
• Like and comment on posts
• Spend more time engaging (at least 2-3 minutes)

🔥 *Most users succeed on attempt 2-3!*
                """,
                f"""
❌ *Incomplete engagement*

⚠️ *Partial activity detected*

 *Need more interaction:*
• Visit more of our social profiles
• Engage with multiple posts per platform
• Follow ALL our accounts
• Show genuine interest with comments

Visit: {LINKTREE_URL} and engage more!
                """,
                f"""
❌ *Verification failed*

 *Engagement too brief or shallow*

 *Tips for success:*
• Spend at least 2-3 minutes on each platform
• Like, comment, and share our content
• Follow us on multiple platforms
• Don't just click and leave immediately

 *Try again:* {LINKTREE_URL}
                """,
                f"""
❌ *Activity quality insufficient*

 *System detected minimal engagement*

 *For better results:*
• Browse through multiple posts
• Leave thoughtful comments
• Follow our accounts properly
• Engage with recent content

🚀 *Try again:* {LINKTREE_URL}
                """
            ]
            
            failure_msg = random.choice(failure_messages)
            
            keyboard = [
                [InlineKeyboardButton("🔗 Engage More", url=LINKTREE_URL)],
                [InlineKeyboardButton("🔄 Try Again", callback_data="retry_verification")],
                [InlineKeyboardButton("💡 Get Tips", callback_data="engagement_tips")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(failure_msg, reply_markup=reply_markup, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Erreur verify_social_engagement: {e}")

async def handle_group_messages(update: Update, context):
    global EXCLUSIVE_GROUP_ID
    
    try:
        if not update.effective_chat or not update.effective_user:
            return
            
        if EXCLUSIVE_GROUP_ID is None:
            EXCLUSIVE_GROUP_ID = update.effective_chat.id
            logger.info(f"Exclusive group ID set: {EXCLUSIVE_GROUP_ID}")
        
        if update.effective_chat.id != EXCLUSIVE_GROUP_ID:
            return
        
        if update.effective_user.is_bot:
            return
        
        current_time = datetime.now()
        if (EXCLUSIVE_GROUP_ID in last_group_response and 
            (current_time - last_group_response[EXCLUSIVE_GROUP_ID]).seconds < 30):
            return
        
        last_group_response[EXCLUSIVE_GROUP_ID] = current_time
        
        auto_response = """
 *Want to request another model?*

 *Make any request of any model you want but follow the same conditions!*

Just message me privately and complete the social engagement task again! ✨

 *Fresh content delivery available!*
        """
        
        keyboard = [
            [InlineKeyboardButton("📱 Message Bot", url=f"https://t.me/{context.bot.username}")],
            [InlineKeyboardButton("🔗 Social Media", url=LINKTREE_URL)],
            [InlineKeyboardButton("💎 Make Request", url=f"https://t.me/{context.bot.username}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await asyncio.sleep(random.uniform(1, 3))
        
        await context.bot.send_message(
            chat_id=EXCLUSIVE_GROUP_ID,
            text=auto_response,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erreur handle_group_messages: {e}")

async def handle_model_requests(update: Update, context):
    try:
        if update.effective_chat.type != 'private':
            return
        
        user_id = update.effective_user.id
        message_text = update.message.text.lower()
        
        request_keywords = ['request', 'want', 'need', 'model', 'content', 'send', 'get', 'leak', 'exclusive']
        
        if any(keyword in message_text for keyword in request_keywords):
            db.add_request(user_id, update.message.text)
            
            response = f"""
🎯 *Model request noted!*

*Request:* {update.message.text}

💎 *To process your request, complete the social engagement task again.*

Same simple process for fresh content! 🚀

Ready?
            """
            
            keyboard = [
                [InlineKeyboardButton("📱 Start Task", callback_data="start_social_task")],
                [InlineKeyboardButton("📋 Request Examples", callback_data="request_examples")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Error in handle_model_requests: {e}")

async def handle_admin_message(update: Update, context):
    global ADMIN_CHAT_ID
    
    try:
        user = update.effective_user
        if user and user.username and user.username.lower() == ADMIN_USERNAME.lower():
            ADMIN_CHAT_ID = update.effective_chat.id
            await update.message.reply_text("Admin configuré pour Bot2!")
            logger.info(f"Admin chat ID (Bot2) set: {ADMIN_CHAT_ID}")
            
    except Exception as e:
        logger.error(f"Erreur handle_admin_message Bot2: {e}")

def main():
    try:
        application = Application.builder().token(TOKEN_BOT2).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(ChatJoinRequestHandler(handle_join_request))
        application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_messages))
        application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_model_requests))
        application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_admin_message))

        print("🚀 Bot2 démarré avec succès!")
        application.run_polling(drop_pending_updates=True, timeout=60)

    except Exception as e:
        print(f"❌ Erreur Bot2: {e}")
        logger.error(traceback.format_exc())
        time.sleep(10)

if __name__ == '__main__':
    main()
    
