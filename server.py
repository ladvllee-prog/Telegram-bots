from flask import Flask
import threading
import main
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Bots are running!"

def run_bots():
    main.main()

if __name__ == "__main__":
    threading.Thread(target=run_bots, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
