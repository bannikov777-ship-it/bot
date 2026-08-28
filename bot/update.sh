#!/bin/bash
# update.sh - простой вариант

cd /app/bot
git pull origin main
echo "✅ Код обновлён!"
echo "➡️ Теперь перезапусти бота в панели управления."
