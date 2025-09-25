from flask import Flask
import threading
import time
import os

app = Flask(__name__)

# Import et lancement sécurisé des bots
def run_bots():
    try:
        # Attendre que Flask soit prêt
        time.sleep(2)
        from main import main
        main()
    except Exception as e:
        print(f"❌ Error starting bots: {e}")

@app.route("/")
def home():
    return """
    <h1>🔥 Telegram Viral Bots - ACTIF</h1>
    <p>Bots are running successfully!</p>
    <ul>
        <li>🤖 Bot 1: Forward viral system</li>
        <li>📱 Bot 2: Social engagement system</li>
        <li>✅ Status: Operational</li>
    </ul>
    """

@app.route("/health")
def health():
    return {"status": "healthy", "bots": "running"}

if __name__ == "__main__":
    # Démarrer les bots dans un thread séparé
    bot_thread = threading.Thread(target=run_bots, daemon=True)
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
