# migrate_guild_weekly.py

import sqlite3
import os
from config import DB_NAME

def migrate_guild_weekly():
    print("🔄 Запуск миграции guild_exp_weekly...")
    
    # Проверяем, существует ли БД
    if not os.path.exists(DB_NAME):
        print(f"❌ База данных не найдена: {DB_NAME}")
        print("Сначала запустите бота (python main.py) для создания БД.")
        return
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Проверяем колонку guild_exp_weekly
    cur.execute("PRAGMA table_info(characters)")
    columns = [col[1] for col in cur.fetchall()]
    
    if 'guild_exp_weekly' not in columns:
        cur.execute('ALTER TABLE characters ADD COLUMN guild_exp_weekly INTEGER DEFAULT 0')
        print("✅ Добавлена колонка guild_exp_weekly")
    else:
        print("ℹ️ Колонка guild_exp_weekly уже существует")
    
    # ✅ ИСПРАВЛЕНО: добавляем без DEFAULT, потом обновляем
    if 'guild_exp_updated_at' not in columns:
        cur.execute('ALTER TABLE characters ADD COLUMN guild_exp_updated_at TIMESTAMP')
        print("✅ Добавлена колонка guild_exp_updated_at (без DEFAULT)")
        
        # Обновляем существующие записи
        cur.execute("UPDATE characters SET guild_exp_updated_at = datetime('now') WHERE guild_exp_updated_at IS NULL")
        print("✅ Обновлены даты для существующих игроков")
    else:
        print("ℹ️ Колонка guild_exp_updated_at уже существует")
    
    # Обновляем существующих игроков (копируем общий вклад в еженедельный)
    cur.execute('UPDATE characters SET guild_exp_weekly = guild_exp_contributed WHERE guild_exp_weekly IS NULL OR guild_exp_weekly = 0')
    print("✅ Обновлены существующие игроки")
    
    # Проверяем колонку weekly_exp в guilds
    cur.execute("PRAGMA table_info(guilds)")
    guild_columns = [col[1] for col in cur.fetchall()]
    
    if 'weekly_exp' not in guild_columns:
        cur.execute('ALTER TABLE guilds ADD COLUMN weekly_exp INTEGER DEFAULT 0')
        print("✅ Добавлена колонка weekly_exp в guilds")
    else:
        print("ℹ️ Колонка weekly_exp в guilds уже существует")
    
    conn.commit()
    conn.close()
    print("✅ Миграция завершена!")

if __name__ == '__main__':
    migrate_guild_weekly()