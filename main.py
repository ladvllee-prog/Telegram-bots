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
        """Run bot with monitoring and auto-restart"""
        while True:
            try:
                logger.info(f"🚀 Starting {bot_name}...")
                
                process = subprocess.Popen(
                    [sys.executable, bot_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                self.bot_processes[bot_name] = process
                self.bot_status[bot_name] = 'running'
                
                logger.info(f"✅ {bot_name} started (PID: {process.pid})")
                
                # Monitor process
                while process.poll() is None:
                    time.sleep(10)
                
                # Process ended
                logger.warning(f"⚠️ {bot_name} stopped unexpectedly")
                self.bot_status[bot_name] = 'restarting'
                
                # Wait before restart
                time.sleep(5)
                logger.info(f"🔄 Restarting {bot_name}...")
                
            except Exception as e:
                logger.error(f"❌ Error with {bot_name}: {e}")
                self.bot_status[bot_name] = 'error'
                time.sleep(10)  # Wait before retry
    
    def stop_all(self):
        """Stop all bots"""
        for bot_name, process in self.bot_processes.items():
            if process and process.poll() is None:
                logger.info(f"🛑 Stopping {bot_name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

def main():
    print("""
🔥 **TELEGRAM VIRAL BOTS LAUNCHER**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **DUAL-BOT VIRAL SYSTEM ACTIVATED**
• Bot 1: Forward-based viral spreading (95% failure rate)
• Bot 2: Social media engagement viral (95% failure rate)  
• Auto-restart on crash
• Full error handling
• Logs saved in bots.log

🚀 **Ready for maximum viral impact!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    # Check environment variables
    if not os.getenv("BOT1_TOKEN"):
        print("❌ BOT1_TOKEN not set in environment")
        return
    
    if not os.getenv("BOT2_TOKEN"):
        print("❌ BOT2_TOKEN not set in environment")
        return
    
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
            args=('VIRAL_BOT_1', 'bot1.py'),
            daemon=True
        )
        bot1_thread.start()
        
        time.sleep(3)
        
        # Start Bot 2  
        bot2_thread = threading.Thread(
            target=manager.run_bot,
            args=('VIRAL_BOT_2', 'bot2.py'),
            daemon=True
        )
        bot2_thread.start()
        
        print("✅ Both viral bots launched successfully!")
        print("📊 Auto-restart monitoring active")
        print("🔥 95% failure rate configured for maximum viral spread")
        print("\n" + "="*60)
        print("🎯 VIRAL SYSTEM STATUS: ACTIVE")
        print("⚡ Press Ctrl+C to stop all bots")
        print("="*60 + "\n")
        
        # Status monitoring loop
        while True:
            time.sleep(30)
            logger.info("🔄 System monitoring active - Both bots running")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping viral bot system...")
        manager.stop_all()
        print("✅ All bots stopped successfully!")

if __name__ == "__main__":
    main()
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
