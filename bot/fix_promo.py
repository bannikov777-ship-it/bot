# fix_promo.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game.db')

def fix_promo():
    print("🔄 Начинаю исправление промокода...")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ База данных не найдена: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Создаём таблицу permanent_promo_codes
    cur.execute('''
        CREATE TABLE IF NOT EXISTS permanent_promo_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            reward_type TEXT NOT NULL,
            reward_amount INTEGER NOT NULL,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Таблица permanent_promo_codes проверена/создана")
    
    # Создаём таблицу permanent_promo_uses
    cur.execute('''
        CREATE TABLE IF NOT EXISTS permanent_promo_uses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_id INTEGER,
            character_id INTEGER,
            used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (code_id) REFERENCES permanent_promo_codes(id),
            FOREIGN KEY (character_id) REFERENCES characters(id),
            UNIQUE(code_id, character_id)
        )
    ''')
    print("✅ Таблица permanent_promo_uses проверена/создана")
    
    # Добавляем код OpenGame
    cur.execute('''
        INSERT OR IGNORE INTO permanent_promo_codes (code, reward_type, reward_amount, description)
        VALUES ('OPENGAME', 'both', 0, '100 кристаллов + 2000 серебра')
    ''')
    print("✅ Промокод OpenGame добавлен")
    
    # Проверяем
    cur.execute('SELECT * FROM permanent_promo_codes')
    rows = cur.fetchall()
    print(f"📋 Текущие промокоды: {rows}")
    
    conn.commit()
    conn.close()
    print("✅ Готово!")

if __name__ == '__main__':
    fix_promo()