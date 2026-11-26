#!/usr/bin/env bash
# Запуск Tabys без Docker (Mac / Linux):   bash start.sh
# Первый запуск ставит зависимости (1–3 минуты), дальше стартует за секунды.
# Остановить: Ctrl+C — закроются и сайт, и бэкенд.
set -e
cd "$(dirname "$0")"

command -v python3 >/dev/null || { echo "Нужен Python 3.10+: https://www.python.org/downloads/"; exit 1; }
command -v npm >/dev/null || { echo "Нужен Node.js 18+: https://nodejs.org"; exit 1; }

echo "→ Бэкенд: зависимости"
cd backend
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
[ -f .env ] || cp .env.example .env   # без ключей работает демо-режим

echo "→ Бэкенд: http://localhost:8000/docs"
.venv/bin/uvicorn app.main:app --port 8000 &
BACKEND_PID=$!
trap 'kill $BACKEND_PID 2>/dev/null || true' EXIT INT TERM

echo "→ Сайт: зависимости"
cd ../frontend
[ -d node_modules ] || npm install

echo "→ Сайт: http://localhost:5173   (остановить: Ctrl+C)"
if [ -z "$CI" ]; then
  (sleep 4; open http://localhost:5173 2>/dev/null || xdg-open http://localhost:5173 2>/dev/null || true) &
fi
npm run dev
