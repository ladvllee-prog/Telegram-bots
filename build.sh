#!/usr/bin/env bash
set -euo pipefail

echo "=== Build start ==="
python --version
pip --version

# 🔥 Purge complet de tous les paquets déjà installés
echo "=== Purging old packages ==="
pip freeze | xargs pip uninstall -y || true

# Supprimer les libs parasites connues
pip uninstall -y telegram python-telegram-bot Telethon || true

# Réinstall propre
echo "=== Installing dependencies ==="
pip install --no-cache-dir python-telegram-bot==20.8
pip install --no-cache-dir -r requirements.txt

# Debug runtime info
python - <<'PY'
import sys, subprocess
try:
    import importlib.metadata as md
except Exception:
    import importlib_metadata as md

print("=== Runtime info ===")
print("python:", sys.version)
try:
    print("python-telegram-bot:", md.version("python-telegram-bot"))
except Exception as e:
    print("python-telegram-bot: NOT INSTALLED or error:", e)

try:
    import telegram as tg
    print("telegram module file:", getattr(tg, "__file__", "unknown"))
    print("telegram.__version__:", getattr(tg, "__version__", "no-__version__"))
except Exception as e:
    print("telegram import error:", e)

print("---- pip freeze ----")
print(subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).decode())
PY

echo "=== Build finished ==="
