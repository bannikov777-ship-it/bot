import sqlite3
from config import DB_NAME

print("🔄 Начинаем настройку промокодов...")

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

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
print("✅ Таблица permanent_promo_codes создана")

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
print("✅ Таблица permanent_promo_uses создана")

cur.execute('''
    INSERT OR IGNORE INTO permanent_promo_codes (code, reward_type, reward_amount, description)
    VALUES ('OPENGAME', 'both', 0, '100 кристаллов + 2000 серебра для новичков')
''')
print("✅ Промокод OpenGame добавлен")

conn.commit()
conn.close()
print("✅ Готово! Перезапусти бота.")
EOF