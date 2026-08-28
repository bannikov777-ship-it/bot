# core/user.py

import sqlite3
import json
from datetime import datetime
from config import DB_NAME

def get_user(vk_id):
    """Получение пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT state, context, last_activity FROM users WHERE vk_id = ?', (vk_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {'state': row[0], 'context': json.loads(row[1]), 'last_activity': row[2]}
    else:
        add_user(vk_id)
        return {'state': 'city', 'context': {}, 'last_activity': datetime.now().isoformat()}

def add_user(vk_id):
    """Добавление пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('INSERT OR IGNORE INTO users (vk_id, state, context, last_activity) VALUES (?, ?, ?, ?)',
                (vk_id, 'city', '{}', datetime.now().isoformat()))
    conn.commit()
    conn.close()

def update_user(vk_id, state=None, context=None):
    """Обновление пользователя с обновлением времени активности"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    now = datetime.now().isoformat()
    
    if state is not None and context is not None:
        cur.execute('UPDATE users SET state = ?, context = ?, last_activity = ? WHERE vk_id = ?',
                    (state, json.dumps(context), now, vk_id))
    elif state is not None:
        cur.execute('UPDATE users SET state = ?, last_activity = ? WHERE vk_id = ?',
                    (state, now, vk_id))
    elif context is not None:
        cur.execute('UPDATE users SET context = ?, last_activity = ? WHERE vk_id = ?',
                    (json.dumps(context), now, vk_id))
    else:
        # Если ничего не меняется, просто обновляем время
        cur.execute('UPDATE users SET last_activity = ? WHERE vk_id = ?', (now, vk_id))
    
    conn.commit()
    conn.close()

def update_activity(vk_id):
    """Простое обновление времени активности"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE users SET last_activity = ? WHERE vk_id = ?',
                (datetime.now().isoformat(), vk_id))
    conn.commit()
    conn.close()