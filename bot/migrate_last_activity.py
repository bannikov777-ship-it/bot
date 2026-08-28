# migrate.py - универсальная миграция

import sqlite3
from config import DB_NAME
from datetime import datetime

def migrate():
    print("🔄 Запуск миграции...")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # ============ ПРОВЕРКА ТАБЛИЦ ============
    
    # Список таблиц для проверки
    tables = [
        'users',
        'characters',
        'cities',
        'consumable_templates',
        'player_consumables',
        'guilds',
        'guild_members',
        'guild_storage',
        'guild_applications',
        'auction_lots',
        'hunter_quest_templates',
        'player_quests',
        'daily_quest_stats',
        'tower_party',
        'tower_bosses',
        'tower_invites',
        'mail',
        'resource_templates',
        'player_resources',
        'craft_recipes',
        'herbs',
        'player_herbs',
        'guild_quests',
        'player_guild_quests',
        'guild_quests_daily',
        'item_templates',
        'player_items',
        'premium_shop',
        'equipment',
        'promo_codes',
        'promo_code_uses',
        'permanent_promo_codes',
        'permanent_promo_uses'
    ]
    
    # Проверяем существование таблиц
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cur.fetchall()]
    
    for table in tables:
        if table not in existing_tables:
            print(f"⚠️ Таблица {table} отсутствует! Создай её в database.py")
    
    # ============ ПРОВЕРКА КОЛОНОК ============
    
    # Проверяем колонки в users
    cur.execute("PRAGMA table_info(users)")
    users_columns = [col[1] for col in cur.fetchall()]
    
    if 'last_activity' not in users_columns:
        try:
            cur.execute('ALTER TABLE users ADD COLUMN last_activity TIMESTAMP')
            print("✅ Добавлена колонка last_activity в users")
        except sqlite3.OperationalError as e:
            print(f"⚠️ Ошибка добавления last_activity: {e}")
    
    # Проверяем колонки в promo_codes
    cur.execute("PRAGMA table_info(promo_codes)")
    promo_columns = [col[1] for col in cur.fetchall()]
    
    if 'reward_type' not in promo_columns:
        try:
            cur.execute('ALTER TABLE promo_codes ADD COLUMN reward_type TEXT DEFAULT "crystals"')
            print("✅ Добавлена колонка reward_type в promo_codes")
        except sqlite3.OperationalError as e:
            print(f"⚠️ Ошибка добавления reward_type: {e}")
    
    # Проверяем колонки в characters
    cur.execute("PRAGMA table_info(characters)")
    chars_columns = [col[1] for col in cur.fetchall()]
    
    if 'vip' not in chars_columns:
        try:
            cur.execute('ALTER TABLE characters ADD COLUMN vip INTEGER DEFAULT 0')
            print("✅ Добавлена колонка vip в characters")
        except sqlite3.OperationalError as e:
            print(f"⚠️ Ошибка добавления vip: {e}")
    
    if 'vip_expires_at' not in chars_columns:
        try:
            cur.execute('ALTER TABLE characters ADD COLUMN vip_expires_at TIMESTAMP DEFAULT NULL')
            print("✅ Добавлена колонка vip_expires_at в characters")
        except sqlite3.OperationalError as e:
            print(f"⚠️ Ошибка добавления vip_expires_at: {e}")
    
    # ============ ЗАПОЛНЯЕМ ДАННЫЕ ============
    
    # Заполняем last_activity если есть колонка
    if 'last_activity' in users_columns:
        cur.execute('UPDATE users SET last_activity = ? WHERE last_activity IS NULL', 
                   (datetime.now().isoformat(),))
        print("✅ Обновлено время активности")
    
    conn.commit()
    conn.close()
    print("✅ Миграция завершена!")

if __name__ == '__main__':
    migrate()