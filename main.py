import subprocess
import sys
import threading
import time
import logging
import os
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bots.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.bot_processes = {}
        self.bot_status = {}
        
    def run_bot(self, bot_name, bot_file):
        """Run bot with monitoring"""
        try:
            logger.info(f"🚀 Starting {bot_name}...")
            
            process = subprocess.Popen(
                [sys.executable, bot_file]
            )
            
            self.bot_processes[bot_name] = process
            self.bot_status[bot_name] = 'running'
            
            logger.info(f"✅ {bot_name} started (PID: {process.pid})")
            
            # Monitor process
            while process.poll() is None:
                time.sleep(10)
            
            # Process ended
            logger.warning(f"⚠️ {bot_name} stopped unexpectedly")
            self.bot_status[bot_name] = 'stopped'
            
        except Exception as e:
            logger.error(f"❌ Error with {bot_name}: {e}")
            self.bot_status[bot_name] = 'error'
    
    def stop_all(self):
        """Stop all bots"""
        for bot_name, process in self.bot_processes.items():
            if process.poll() is None:
                logger.info(f"🛑 Stopping {bot_name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

def main():
    print("""
🔥 **TELEGRAM BOTS LAUNCHER**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **MULTI-BOT SYSTEM ACTIVATED**
• Bot 1: Telegram automation
• Bot 2: Social media automation
• Auto-restart on crash
• Logs saved in bots.log

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    # Check bot files
    bot_files = ['bot1.py', 'bot2.py']
    missing = [f for f in bot_files if not os.path.exists(f)]
    
    if missing:
        print(f"❌ Missing files: {missing}")
        print("Please ensure both bot files are in the current directory.")
        return
    
    manager = BotManager()
    
    try:
        # Start Bot 1
        bot1_thread = threading.Thread(
            target=manager.run_bot,
            args=('BOT_1', 'bot1.py'),
            daemon=True
        )
        bot1_thread.start()
        
        time.sleep(3)
        
        # Start Bot 2
        bot2_thread = threading.Thread(
            target=manager.run_bot,
            args=('BOT_2', 'bot2.py'),
            daemon=True
        )
        bot2_thread.start()
        
        print("✅ Both bots launched!")
        print("📊 Monitoring system active")
        print("\n" + "="*50)
        print("Press Ctrl+C to stop all bots")
        print("="*50 + "\n")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping bots...")
        manager.stop_all()
        print("✅ All bots stopped!")

if __name__ == "__main__":
    main()
