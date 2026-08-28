# permanent_promo.py

import sqlite3
from datetime import datetime
from config import DB_NAME


def ensure_permanent_promo_tables():
    """Проверяет существование таблиц и создаёт их если нужно"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='permanent_promo_codes'")
    if not cur.fetchone():
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
        print("✅ Создана таблица permanent_promo_codes")
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='permanent_promo_uses'")
    if not cur.fetchone():
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
        print("✅ Создана таблица permanent_promo_uses")
    
    conn.commit()
    conn.close()


def create_permanent_promo(code, reward_type='crystals', reward_amount=100, description=''):
    """Создание постоянного промокода"""
    ensure_permanent_promo_tables()
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Проверяем, существует ли уже такой код
    cur.execute('SELECT id FROM permanent_promo_codes WHERE code = ?', (code.upper(),))
    if cur.fetchone():
        conn.close()
        return False, "Код уже существует"
    
    cur.execute('''
        INSERT INTO permanent_promo_codes (code, reward_type, reward_amount, description)
        VALUES (?, ?, ?, ?)
    ''', (code.upper(), reward_type, reward_amount, description))
    
    conn.commit()
    conn.close()
    return True, "Промокод создан!"


def use_permanent_promo(character_id, code):
    """Использование постоянного промокода"""
    ensure_permanent_promo_tables()
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Проверяем существование промокода
    cur.execute('''
        SELECT id, reward_type, reward_amount, description, is_active
        FROM permanent_promo_codes WHERE code = ? AND is_active = 1
    ''', (code.upper(),))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        return False, "❌ Неверный промокод.", None, 0
    
    code_id, reward_type, reward_amount, description, is_active = row
    
    # Проверяем, использовал ли уже этот игрок
    cur.execute('SELECT id FROM permanent_promo_uses WHERE code_id = ? AND character_id = ?', 
                (code_id, character_id))
    if cur.fetchone():
        conn.close()
        return False, "❌ Вы уже использовали этот промокод.", None, 0
    
    # Начисляем награду
    if reward_type == 'crystals':
        cur.execute('UPDATE characters SET crystals = crystals + ? WHERE id = ?', (reward_amount, character_id))
    elif reward_type == 'silver':
        cur.execute('UPDATE characters SET silver = silver + ? WHERE id = ?', (reward_amount, character_id))
    elif reward_type == 'both':
        # Для кода OpenGame: и кристаллы, и серебро
        cur.execute('UPDATE characters SET crystals = crystals + ? WHERE id = ?', (100, character_id))
        cur.execute('UPDATE characters SET silver = silver + ? WHERE id = ?', (2000, character_id))
    else:
        conn.close()
        return False, "❌ Неизвестный тип награды.", None, 0
    
    # Записываем использование
    cur.execute('INSERT INTO permanent_promo_uses (code_id, character_id) VALUES (?, ?)', 
                (code_id, character_id))
    
    conn.commit()
    conn.close()
    
    if reward_type == 'both':
        return True, "✅ Промокод активирован! Вы получили 100 💎 кристаллов и 2000 💰 серебра!", 'both', 0
    else:
        reward_name = '💎 кристаллов' if reward_type == 'crystals' else '💰 серебра'
        return True, f"✅ Промокод активирован! Вы получили {reward_amount} {reward_name}!", reward_type, reward_amount


def init_default_promo():
    """Создаёт стандартный промокод OpenGame при первом запуске"""
    ensure_permanent_promo_tables()
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Проверяем, существует ли код OpenGame
    cur.execute('SELECT id FROM permanent_promo_codes WHERE code = ?', ('OPENGAME',))
    if not cur.fetchone():
        # Создаём специальный код с обоими наградами
        cur.execute('''
            INSERT INTO permanent_promo_codes (code, reward_type, reward_amount, description)
            VALUES (?, ?, ?, ?)
        ''', ('OPENGAME', 'both', 0, '100 кристаллов + 2000 серебра для новичков'))
        conn.commit()
        print("✅ Создан промокод OpenGame (100 кристаллов + 2000 серебра)")
    
    conn.close()