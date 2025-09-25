from flask import Flask, jsonify
import threading
import main
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "message": "Viral Bot System Active",
        "bots": {
            "bot1": "Forward Viral Bot - 95% failure rate",
            "bot2": "Social Media Viral Bot - 95% failure rate"
        }
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": str(datetime.now())})

@app.route("/status")
def status():
    return jsonify({
        "system": "operational",
        "features": [
            "Auto-restart on crash",
            "95% failure rate for viral spread",
            "Dual bot system",
            "Social media engagement tracking"
        ]
    })

def run_bots():
    """Run the bot system"""
    try:
        logger.info("🚀 Starting viral bot system...")
        main.main()
    except Exception as e:
        logger.error(f"❌ Error in bot system: {e}")

if __name__ == "__main__":
    # Start bots in background thread
    threading.Thread(target=run_bots, daemon=True).start()
    
    # Start Flask server
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"🌐 Starting web server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
