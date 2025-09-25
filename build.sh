#!/usr/bin/env bash
set -euo pipefail

echo "=== Build start ==="
python --version
pip --version

# Remove conflicting packages if present (no failure)
pip uninstall -y telegram python-telegram-bot || true

# Install the exact PTB version we want (no cache)
pip install --no-cache-dir python-telegram-bot==20.8

# Install rest of requirements (Flask, gunicorn, apscheduler)
pip install --no-cache-dir -r requirements.txt

# Debug: print installed versions to build log
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

# Forcer Python 3.11 et PTB 20.8
pyenv global 3.11.9 || true
pip install --force-reinstall --no-cache-dir python-telegram-bot==20.8

echo "=== Build finished ==="
