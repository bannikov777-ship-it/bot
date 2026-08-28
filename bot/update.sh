#!/bin/bash
# update.sh - безопасное обновление бота

echo "🔄 Начинаю обновление бота..."

# 1. Делаем бэкап БД
if [ -f "game.db" ]; then
    BACKUP_NAME="game_backup_$(date +%Y%m%d_%H%M%S).db"
    cp game.db $BACKUP_NAME
    echo "✅ Бэкап создан: $BACKUP_NAME"
fi

# 2. Скачиваем обновления
git pull origin main

# 3. Проверяем, не изменилась ли структура БД
python3 check_db_migrations.py

# 4. Перезапускаем бота
systemctl restart gamebot
echo "✅ Бот перезапущен!"

# 5. Чистим старые бэкапы (оставляем последние 5)
ls -t game_backup_*.db | tail -n +6 | xargs rm -f 2>/dev/null
echo "🧹 Старые бэкапы удалены"