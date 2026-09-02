# codes.py (исправленный)

import sqlite3
import random
import string
from datetime import datetime, timedelta
from config import DB_NAME


def ensure_promo_tables():
    """Проверяет существование таблиц и создаёт их если нужно"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='promo_codes'")
    if not cur.fetchone():
        cur.execute('''
            CREATE TABLE IF NOT EXISTS promo_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                amount INTEGER NOT NULL,
                max_uses INTEGER DEFAULT 1,
                used_count INTEGER DEFAULT 0,
                expires_at TIMESTAMP,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                is_active INTEGER DEFAULT 1,
                reward_type TEXT DEFAULT 'crystals'
            )
        ''')
        print("✅ Создана таблица promo_codes")
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='promo_code_uses'")
    if not cur.fetchone():
        cur.execute('''
            CREATE TABLE IF NOT EXISTS promo_code_uses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_id INTEGER,
                character_id INTEGER,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                amount INTEGER,
                FOREIGN KEY (code_id) REFERENCES promo_codes(id),
                FOREIGN KEY (character_id) REFERENCES characters(id),
                UNIQUE(code_id, character_id)
            )
        ''')
        print("✅ Создана таблица promo_code_uses")
    
    conn.commit()
    conn.close()


def generate_code(length=8):
    characters = string.ascii_uppercase + string.digits
    exclude = '0O1I'
    chars = [c for c in characters if c not in exclude]
    return ''.join(random.choice(chars) for _ in range(length))


def create_code(amount, expires_days=30, max_uses=1, description="", reward_type="crystals"):
    """Создание нового кода с типом награды"""
    ensure_promo_tables()
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    while True:
        code = generate_code(8)
        cur.execute('SELECT id FROM promo_codes WHERE code = ?', (code,))
        if not cur.fetchone():
            break
    
    expires_at = datetime.now() + timedelta(days=expires_days)
    
    # ✅ СОХРАНЯЕМ reward_type
    cur.execute('''
        INSERT INTO promo_codes (code, amount, max_uses, expires_at, description, created_by, reward_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (code, amount, max_uses, expires_at.isoformat(), description, 1, reward_type))
    
    conn.commit()
    conn.close()
    return code


def use_code(character_id, code):
    """Использование кода"""
    ensure_promo_tables()
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='promo_codes'")
    if not cur.fetchone():
        conn.close()
        return False, "Система промокодов ещё не активирована.", 0, None
    
    cur.execute('''
        SELECT id, amount, max_uses, used_count, expires_at, is_active, reward_type
        FROM promo_codes WHERE code = ?
    ''', (code.upper(),))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        return False, "❌ Неверный код.", 0, None
    
    code_id, amount, max_uses, used_count, expires_at, is_active, reward_type = row
    reward_type = reward_type or 'crystals'
    
    if not is_active:
        conn.close()
        return False, "❌ Код деактивирован.", 0, None
    
    if expires_at:
        if datetime.now() > datetime.fromisoformat(expires_at):
            conn.close()
            return False, "❌ Срок действия кода истёк.", 0, None
    
    if used_count >= max_uses:
        conn.close()
        return False, "❌ Код уже использован.", 0, None
    
    cur.execute('SELECT id FROM promo_code_uses WHERE code_id = ? AND character_id = ?', 
                (code_id, character_id))
    if cur.fetchone():
        conn.close()
        return False, "❌ Вы уже использовали этот код.", 0, None
    
    # ✅ НАЧИСЛЯЕМ НАГРАДУ
    if reward_type == 'silver':
        cur.execute('UPDATE characters SET silver = silver + ? WHERE id = ?', 
                    (amount, character_id))
    else:
        cur.execute('UPDATE characters SET crystals = crystals + ? WHERE id = ?', 
                    (amount, character_id))
    
    cur.execute('UPDATE promo_codes SET used_count = used_count + 1 WHERE id = ?', 
                (code_id,))
    
    cur.execute('''
        INSERT INTO promo_code_uses (code_id, character_id, amount)
        VALUES (?, ?, ?)
    ''', (code_id, character_id, amount))
    
    conn.commit()
    conn.close()
    
    reward_icon = '💰 серебра' if reward_type == 'silver' else '💎 кристаллов'
    return True, f"✅ Код активирован! Вы получили {amount} {reward_icon}!", amount, reward_type


def get_codes_stats():
    ensure_promo_tables()
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    cur.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(amount) as total_amount,
            SUM(used_count) as total_uses
        FROM promo_codes
        WHERE is_active = 1
    ''')
    row = cur.fetchone()
    conn.close()
    
    return {
        'total': row[0] or 0,
        'total_amount': row[1] or 0,
        'total_uses': row[2] or 0
    }


def get_codes_list(limit=20):
    ensure_promo_tables()
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        SELECT code, amount, max_uses, used_count, expires_at, description, created_at, is_active, reward_type
        FROM promo_codes
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    rows = cur.fetchall()
    conn.close()
    
    codes = []
    for row in rows:
        codes.append({
            'code': row[0],
            'amount': row[1],
            'max_uses': row[2],
            'used_count': row[3],
            'expires_at': row[4],
            'description': row[5],
            'created_at': row[6],
            'is_active': row[7],
            'reward_type': row[8] or 'crystals'
        })
    return codes