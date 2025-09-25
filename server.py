from flask import Flask
import os
import subprocess
import threading
import time

app = Flask(__name__)

def run_bot(bot_file):
    while True:
        try:
            print(f"🚀 Lancement de {bot_file}")
            subprocess.run(["python", bot_file], check=True)
        except Exception as e:
            print(f"❌ {bot_file} a crashé: {e}")
            print("🔄 Redémarrage dans 10s...")
            time.sleep(10)

@app.route('/')
def home():
    return "🔥 Bots Telegram Actifs"

if __name__ == '__main__':
    threading.Thread(target=run_bot, args=("bot1.py",), daemon=True).start()
    threading.Thread(target=run_bot, args=("bot2.py",), daemon=True).start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
