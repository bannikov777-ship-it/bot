# items.py (полный исправленный с оружием 20+ уровня)

import sqlite3
import random
from config import DB_NAME

def init_items_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
     
    cur.execute('''
        CREATE TABLE IF NOT EXISTS item_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            slot TEXT,
            base_attack INTEGER DEFAULT 0,
            base_defense INTEGER DEFAULT 0,
            base_hp INTEGER DEFAULT 0,
            base_mana INTEGER DEFAULT 0,
            growth_attack REAL DEFAULT 0.1,
            growth_defense REAL DEFAULT 0.1,
            growth_hp REAL DEFAULT 0.1,
            growth_mana REAL DEFAULT 0.1,
            icon TEXT DEFAULT '🗡️',
            bonus_crit INTEGER DEFAULT 0,
            bonus_dodge INTEGER DEFAULT 0,
            required_level INTEGER DEFAULT 1,
            class_restriction TEXT
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS player_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER,
            template_id INTEGER,
            level INTEGER DEFAULT 1,
            rarity INTEGER DEFAULT 1,
            upgrade_level INTEGER DEFAULT 0,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (owner_id) REFERENCES characters(id),
            FOREIGN KEY (template_id) REFERENCES item_templates(id)
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            character_id INTEGER,
            slot TEXT,
            player_item_id INTEGER,
            PRIMARY KEY (character_id, slot),
            FOREIGN KEY (character_id) REFERENCES characters(id),
            FOREIGN KEY (player_item_id) REFERENCES player_items(id)
        )
    ''')
    
    conn.commit()
    conn.close()


def seed_item_templates():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM item_templates')
    if cur.fetchone()[0] == 0:
        templates = [

                        # ===== ОРУЖИЕ (Правая рука) 1-19 уровень =====
            # Меч (баланс) - 5 редкостей
            ('Меч', 'weapon_right', 5, 0, 0, 0, 0.25, 0, 0, 0, '🗡️', 1, 0, 1, None),
            ('Меч', 'weapon_right', 6, 0, 0, 0, 0.25, 0, 0, 0, '🗡️', 2, 1, 1, None),
            ('Меч', 'weapon_right', 7, 0, 0, 0, 0.25, 0, 0, 0, '🗡️', 3, 2, 1, None),
            ('Меч', 'weapon_right', 8, 0, 0, 0, 0.25, 0, 0, 0, '🗡️', 4, 3, 1, None),
            ('Меч', 'weapon_right', 10, 0, 0, 0, 0.25, 0, 0, 0, '🗡️', 5, 4, 1, None),
            
            # Молот (высокий урон, низкий крит/уворот) - 1-19 уровень
            ('Молот', 'weapon_right', 7, 0, 0, 0, 0.30, 0, 0, 0, '🔨', 3, -5, 1, None),
            ('Молот', 'weapon_right', 9, 0, 0, 0, 0.30, 0, 0, 0, '🔨', 4, -4, 1, None),
            ('Молот', 'weapon_right', 11, 0, 0, 0, 0.30, 0, 0, 0, '🔨', 5, -3, 1, None),
            ('Молот', 'weapon_right', 13, 0, 0, 0, 0.30, 0, 0, 0, '🔨', 6, -2, 1, None),
            ('Молот', 'weapon_right', 16, 0, 0, 0, 0.30, 0, 0, 0, '🔨', 7, -1, 1, None),
            
            # Лук (высокий крит/уворот, средний урон) - 1-19 уровень
            ('Лук', 'weapon_right', 4, 0, 0, 0, 0.20, 0, 0, 0, '🏹', 4, 5, 1, None),
            ('Лук', 'weapon_right', 5, 0, 0, 0, 0.20, 0, 0, 0, '🏹', 6, 7, 1, None),
            ('Лук', 'weapon_right', 6, 0, 0, 0, 0.20, 0, 0, 0, '🏹', 8, 9, 1, None),
            ('Лук', 'weapon_right', 7, 0, 0, 0, 0.20, 0, 0, 0, '🏹', 10, 9, 1, None),
            ('Лук', 'weapon_right', 9, 0, 0, 0, 0.20, 0, 0, 0, '🏹', 12, 10, 1, None),
            
            # ===== ОРУЖИЕ 20+ УРОВНЯ (Правая рука) =====
            # Молот 20+ (высокий урон)
            ('Молот', 'weapon_right', 26, 0, 0, 0, 0.30, 0, 0, 0, '🔨', 3, -5, 20, None),
            # ✅ Топор 20+ (тяжёлый)
            ('Топор', 'weapon_right', 22, 0, 0, 0, 0.28, 0, 0, 0, '🪓', 2, -3, 20, None),
            # ✅ Копье 20+ (баланс)
            ('Копье', 'weapon_right', 24, 0, 0, 0, 0.25, 0, 0, 0, '🔱', 4, 5, 20, None),
            # Кинжал 20+ (быстрый)
            ('Кинжал', 'weapon_right', 16, 0, 0, 0, 0.18, 0, 0, 0, '🗡️', 5, 3, 20, None),
            # Посох 20+ (магический) - только Послушник
            ('Посох', 'weapon_right', 27, 0, 0, 0, 0.22, 0, 0, 0, '🪄', 4, 0, 20, 'Послушник'),
            # Свиток 20+ (магический) - только Послушник
            ('Свиток', 'weapon_right', 10, 0, 0, 0, 0.20, 0, 0, 0, '📜', 5, 2, 20, 'Послушник'),
            # Орб 20+ (магический) - только Послушник
            ('Орб', 'weapon_right', 15, 0, 0, 0, 0.21, 0, 0, 0, '🔮', 6, 1, 20, 'Послушник'),
            
            # ===== ЛЕВАЯ РУКА (с 20 уровня) =====
            # Щит (только Оруженосец)
            ('Щит', 'weapon_left', 0, 5, 30, 0, 0, 0, 0, 0, '🛡️', 0, 0, 20, 'Оруженосец'),
            # Кинжал левой руки (только Охотник)
            ('Кинжал ЛР', 'weapon_left', 0, 1, 10, 0, 0, 0, 0, 0, '🗡️', 2, 0, 20, 'Охотник'),
            # Книга (только Послушник)
            ('Книга', 'weapon_left', 0, 2, 15, 5, 0, 0, 0, 0, '📜', 0, 0, 20, 'Послушник'),
            # Орб левой руки (только Послушник)
            ('Орб ЛР', 'weapon_left', 0, 3, 18, 10, 0, 0, 0, 0, '🔮', 0, 0, 20, 'Послушник'),

            # ===== ОРУЖИЕ (Правая рука) 1-19 уровень =====
            # Меч (баланс) - 5 редкостей
            ('Меч', 'weapon_right', 5, 0, 0, 0, 0.25, 0, 0, 0, '🗡️', 1, 0, 1, None),
            ('Меч', 'weapon_right', 6, 0, 0, 0, 0.25, 0, 0, 0, '🗡️', 2, 1, 1, None),
            ('Меч', 'weapon_right', 7, 0, 0, 0, 0.25, 0, 0, 0, '🗡️', 3, 2, 1, None),
            ('Меч', 'weapon_right', 8, 0, 0, 0, 0.25, 0, 0, 0, '🗡️', 4, 3, 1, None),
            ('Меч', 'weapon_right', 10, 0, 0, 0, 0.25, 0, 0, 0, '🗡️', 5, 4, 1, None),
            
            # Молот (высокий урон, низкий крит/уворот) - 1-19 уровень
            ('Молот', 'weapon_right', 7, 0, 0, 0, 0.30, 0, 0, 0, '🔨', 3, -5, 1, None),
            ('Молот', 'weapon_right', 9, 0, 0, 0, 0.30, 0, 0, 0, '🔨', 4, -4, 1, None),
            ('Молот', 'weapon_right', 11, 0, 0, 0, 0.30, 0, 0, 0, '🔨', 5, -3, 1, None),
            ('Молот', 'weapon_right', 13, 0, 0, 0, 0.30, 0, 0, 0, '🔨', 6, -2, 1, None),
            ('Молот', 'weapon_right', 16, 0, 0, 0, 0.30, 0, 0, 0, '🔨', 7, -1, 1, None),
            
            # Лук (высокий крит/уворот, средний урон) - 1-19 уровень
            ('Лук', 'weapon_right', 4, 0, 0, 0, 0.20, 0, 0, 0, '🏹', 4, 5, 1, None),
            ('Лук', 'weapon_right', 5, 0, 0, 0, 0.20, 0, 0, 0, '🏹', 6, 7, 1, None),
            ('Лук', 'weapon_right', 6, 0, 0, 0, 0.20, 0, 0, 0, '🏹', 8, 9, 1, None),
            ('Лук', 'weapon_right', 7, 0, 0, 0, 0.20, 0, 0, 0, '🏹', 10, 9, 1, None),
            ('Лук', 'weapon_right', 9, 0, 0, 0, 0.20, 0, 0, 0, '🏹', 12, 10, 1, None),
            
            # ===== ОРУЖИЕ 20+ УРОВНЯ (Правая рука) =====
            # Молот 20+ (высокий урон)
            ('Молот', 'weapon_right', 26, 0, 0, 0, 0.30, 0, 0, 0, '🔨', 3, -5, 20, None),
            # Топор 20+ (тяжёлый)
            ('Топор', 'weapon_right', 22, 0, 0, 0, 0.28, 0, 0, 0, '🪓', 2, -3, 20, None),
            # Копье 20+ (баланс)
            ('Копье', 'weapon_right', 24, 0, 0, 0, 0.25, 0, 0, 0, '🔱', 4, 5, 20, None),
            # Кинжал 20+ (быстрый)
            ('Кинжал', 'weapon_right', 16, 0, 0, 0, 0.18, 0, 0, 0, '🗡️', 5, 3, 20, None),
            # Посох 20+ (магический) - только Послушник
            ('Посох', 'weapon_right', 27, 0, 0, 0, 0.22, 0, 0, 0, '🪄', 4, 0, 20, 'Послушник'),
            # Свиток 20+ (магический) - только Послушник
            ('Свиток', 'weapon_right', 10, 0, 0, 0, 0.20, 0, 0, 0, '📜', 5, 2, 20, 'Послушник'),
            # Орб 20+ (магический) - только Послушник
            ('Орб', 'weapon_right', 15, 0, 0, 0, 0.21, 0, 0, 0, '🔮', 6, 1, 20, 'Послушник'),
            
            # ===== ЛЕВАЯ РУКА (с 20 уровня) =====
            # Щит (только Оруженосец)
            ('Щит', 'weapon_left', 0, 5, 30, 0, 0, 0, 0, 0, '🛡️', 0, 0, 20, 'Оруженосец'),
            # Кинжал левой руки (только Охотник)
            ('Кинжал ЛР', 'weapon_left', 0, 1, 10, 0, 0, 0, 0, 0, '🗡️', 2, 0, 20, 'Охотник'),
            # Книга (только Послушник)
            ('Книга', 'weapon_left', 0, 2, 15, 5, 0, 0, 0, 0, '📜', 0, 0, 20, 'Послушник'),
            # Орб левой руки (только Послушник)
            ('Орб ЛР', 'weapon_left', 0, 3, 18, 10, 0, 0, 0, 0, '🔮', 0, 0, 20, 'Послушник'),
            
            # ===== БРОНЯ (Торс) =====
            # Кожаная броня (легкая, дает уворот)
            ('Кожаная броня', 'armor', 0, 2, 10, 0, 0, 0.10, 0.05, 0, '🦺', 0, 5, 1, None),
            ('Кожаная броня', 'armor', 0, 3, 15, 0, 0, 0.10, 0.05, 0, '🦺', 0, 7, 1, None),
            ('Кожаная броня', 'armor', 0, 4, 20, 0, 0, 0.10, 0.05, 0, '🦺', 0, 9, 1, None),
            ('Кожаная броня', 'armor', 0, 5, 25, 0, 0, 0.10, 0.05, 0, '🦺', 0, 11, 1, None),
            ('Кожаная броня', 'armor', 0, 7, 30, 0, 0, 0.10, 0.05, 0, '🦺', 0, 13, 1, None),
            
            # Кольчуга (средняя, баланс)
            ('Кольчуга', 'armor', 0, 3, 15, 0, 0, 0.15, 0.10, 0, '🛡️', 2, 0, 1, None),
            ('Кольчуга', 'armor', 0, 5, 18, 0, 0, 0.15, 0.10, 0, '🛡️', 3, 1, 1, None),
            ('Кольчуга', 'armor', 0, 7, 21, 0, 0, 0.15, 0.10, 0, '🛡️', 4, 2, 1, None),
            ('Кольчуга', 'armor', 0, 9, 24, 0, 0, 0.15, 0.10, 0, '🛡️', 5, 3, 1, None),
            ('Кольчуга', 'armor', 0, 12, 27, 0, 0, 0.15, 0.10, 0, '🛡️', 6, 4, 1, None),
            
            # Кираса (тяжелая, высокая защита)
            ('Кираса', 'armor', 0, 4, 20, 0, 0, 0.20, 0.05, 0, '🛡️', -3, -7, 1, None),
            ('Кираса', 'armor', 0, 6, 25, 0, 0, 0.20, 0.05, 0, '🛡️', -2, -5, 1, None),
            ('Кираса', 'armor', 0, 9, 30, 0, 0, 0.20, 0.05, 0, '🛡️', 0, -3, 1, None),
            ('Кираса', 'armor', 0, 12, 35, 0, 0, 0.20, 0.05, 0, '🛡️', 2, -1, 1, None),
            ('Кираса', 'armor', 0, 16, 40, 0, 0, 0.20, 0.05, 0, '🛡️', 4, 0, 1, None),
            
            # ===== ШЛЕМЫ (Голова) =====
            # Подшлемник (легкий, уворот)
            ('Подшлемник', 'head', 0, 1, 5, 0, 0, 0.08, 0.05, 0, '🎩', 0, 0, 1, None),
            ('Подшлемник', 'head', 0, 2, 7, 0, 0, 0.08, 0.05, 0, '🎩', 0, 1, 1, None),
            ('Подшлемник', 'head', 0, 3, 9, 0, 0, 0.08, 0.05, 0, '🎩', 0, 2, 1, None),
            ('Подшлемник', 'head', 0, 4, 11, 0, 0, 0.08, 0.05, 0, '🎩', 0, 3, 1, None),
            ('Подшлемник', 'head', 0, 5, 13, 0, 0, 0.08, 0.05, 0, '🎩', 0, 5, 1, None),
            
            # Шлем (средний, баланс)
            ('Шлем', 'head', 0, 2, 8, 0, 0, 0.12, 0.08, 0, '🎩', 2, -4, 1, None),
            ('Шлем', 'head', 0, 4, 12, 0, 0, 0.12, 0.08, 0, '🎩', 3, -3, 1, None),
            ('Шлем', 'head', 0, 6, 16, 0, 0, 0.12, 0.08, 0, '🎩', 4, -2, 1, None),
            ('Шлем', 'head', 0, 8, 20, 0, 0, 0.12, 0.08, 0, '🎩', 5, -1, 1, None),
            ('Шлем', 'head', 0, 12, 24, 0, 0, 0.12, 0.08, 0, '🎩', 7, 0, 1, None),
            
            # Треуголка (агрессивная)
            ('Треуголка', 'head', 0, 1, 6, 0, 0, 0.15, 0.05, 0, '🎩', -2, -1, 1, None),
            ('Треуголка', 'head', 0, 3, 8, 0, 0, 0.15, 0.05, 0, '🎩', -1, 0, 1, None),
            ('Треуголка', 'head', 0, 5, 10, 0, 0, 0.15, 0.05, 0, '🎩', 0, 1, 1, None),
            ('Треуголка', 'head', 0, 7, 12, 0, 0, 0.15, 0.05, 0, '🎩', 2, 2, 1, None),
            ('Треуголка', 'head', 0, 9, 14, 0, 0, 0.15, 0.05, 0, '🎩', 4, 3, 1, None),
            
            # ===== САПОГИ =====
            # Кожаные сапоги (легкие, уворот)
            ('Кожаные сапоги', 'boots', 1, 1, 0, 0, 0.10, 0.08, 0, 0, '👢', 0, 0, 1, None),
            ('Кожаные сапоги', 'boots', 2, 2, 0, 0, 0.10, 0.08, 0, 0, '👢', 0, 1, 1, None),
            ('Кожаные сапоги', 'boots', 3, 3, 0, 0, 0.10, 0.08, 0, 0, '👢', 0, 2, 1, None),
            ('Кожаные сапоги', 'boots', 4, 4, 0, 0, 0.10, 0.08, 0, 0, '👢', 0, 3, 1, None),
            ('Кожаные сапоги', 'boots', 6, 6, 0, 0, 0.10, 0.08, 0, 0, '👢', 0, 7, 1, None),
            
            # Железные сапоги (сбалансированные)
            ('Железные сапоги', 'boots', 2, 2, 0, 0, 0.12, 0.12, 0, 0, '👢', 0, 0, 1, None),
            ('Железные сапоги', 'boots', 3, 3, 0, 0, 0.12, 0.12, 0, 0, '👢', 0, 1, 1, None),
            ('Железные сапоги', 'boots', 5, 5, 0, 0, 0.12, 0.12, 0, 0, '👢', 0, 2, 1, None),
            ('Железные сапоги', 'boots', 7, 7, 0, 0, 0.12, 0.12, 0, 0, '👢', 0, 3, 1, None),
            ('Железные сапоги', 'boots', 10, 10, 0, 0, 0.12, 0.12, 0, 0, '👢', 0, 5, 1, None),
            
            # Стальные сапоги (тяжелые, защита)
            ('Стальные сапоги', 'boots', 3, 3, 0, 0, 0.15, 0.15, 0, 0, '👢', -3, -3, 1, None),
            ('Стальные сапоги', 'boots', 5, 5, 0, 0, 0.15, 0.15, 0, 0, '👢', -1, -2, 1, None),
            ('Стальные сапоги', 'boots', 8, 8, 0, 0, 0.15, 0.15, 0, 0, '👢', 1, 0, 1, None),
            ('Стальные сапоги', 'boots', 10, 10, 0, 0, 0.15, 0.15, 0, 0, '👢', 3, 0, 1, None),
            ('Стальные сапоги', 'boots', 12, 12, 0, 0, 0.15, 0.15, 0, 0, '👢', 3, 1, 1, None),
        ]
        cur.executemany('''
            INSERT INTO item_templates (name, slot, base_attack, base_defense, base_hp, base_mana, 
                                        growth_attack, growth_defense, growth_hp, growth_mana, icon,
                                        bonus_crit, bonus_dodge, required_level, class_restriction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', templates)
        conn.commit()
    conn.close()


def get_item_template_id_by_name(name):
    """Возвращает ID первого найденного шаблона по имени"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT id FROM item_templates WHERE name = ? LIMIT 1', (name,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def get_item_restriction(template_id):
    """Получение классового ограничения и требуемого уровня для предмета"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT class_restriction, required_level FROM item_templates WHERE id = ?', (template_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {'class': row[0], 'level': row[1] or 1}
    return None


def can_equip_item(character_id, template_id):
    """Проверка, может ли игрок экипировать предмет"""
    from core import get_character_by_id  # ✅ ИМПОРТ ВНУТРИ
    char = get_character_by_id(character_id)
    if not char:
        return False, "Персонаж не найден"
    
    restriction = get_item_restriction(template_id)
    if not restriction:
        return True, "OK"
    
    if char.get('level', 0) < restriction['level']:
        return False, f"Требуется {restriction['level']} уровень"
    
    if restriction['class'] and char.get('class') != restriction['class']:
        return False, f"Только для класса: {restriction['class']}"
    
    return True, "OK"


def get_item_stats(template_id, level, rarity, upgrade_level):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''SELECT name, slot, base_attack, base_defense, base_hp, base_mana,
                          growth_attack, growth_defense, growth_hp, growth_mana, icon,
                          bonus_crit, bonus_dodge, required_level
                   FROM item_templates WHERE id = ?''', (template_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    
    name, slot, base_attack, base_defense, base_hp, base_mana, g_attack, g_defense, g_hp, g_mana, icon, bonus_crit, bonus_dodge, required_level = row
    
    rarity_mult = {1:1.0, 2:1.2, 3:1.3, 4:1.45, 5:1.55}.get(rarity, 1.0)
    upgrade_bonus = 1 + 0.1 * upgrade_level
    
    # ✅ Если предмет 20+ уровня — используем base_attack как конечное значение
    if required_level >= 20:
        final_attack = base_attack * rarity_mult * upgrade_bonus
        final_defense = base_defense * rarity_mult * upgrade_bonus
        final_hp = base_hp * rarity_mult * upgrade_bonus
        final_mana = base_mana * rarity_mult * upgrade_bonus
    else:
        # Для предметов 1-19 уровня — расчёт с ростом
        def calc(base, growth):
            return base * (1 + (level - 1) * growth)
        
        final_attack = calc(base_attack, g_attack) * rarity_mult * upgrade_bonus
        final_defense = calc(base_defense, g_defense) * rarity_mult * upgrade_bonus
        final_hp = calc(base_hp, g_hp) * rarity_mult * upgrade_bonus
        final_mana = calc(base_mana, g_mana) * rarity_mult * upgrade_bonus
    
    final_crit = bonus_crit * rarity_mult if bonus_crit else 0
    final_dodge = bonus_dodge * rarity_mult if bonus_dodge else 0
    
    return {
        'name': name,
        'slot': slot,
        'attack': round(final_attack),
        'defense': round(final_defense),
        'hp': round(final_hp),
        'mana': round(final_mana),
        'icon': icon,
        'bonus_crit': round(final_crit),
        'bonus_dodge': round(final_dodge)
    }


def create_player_item(owner_id, template_id, level, rarity):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO player_items (owner_id, template_id, level, rarity, upgrade_level, quantity)
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (owner_id, template_id, level, rarity, 0))
    item_id = cur.lastrowid
    conn.commit()
    conn.close()
    return item_id

def delete_item(player_item_id, character_id):
    """Удаление предмета из инвентаря"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Проверяем, принадлежит ли предмет игроку
    cur.execute('SELECT owner_id, quantity FROM player_items WHERE id = ?', (player_item_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False, "Предмет не найден"
    
    owner_id, quantity = row
    if owner_id != character_id:
        conn.close()
        return False, "Предмет не принадлежит вам"
    
    # Проверяем, не экипирован ли предмет
    cur.execute('SELECT slot FROM equipment WHERE player_item_id = ? AND character_id = ?', 
                (player_item_id, character_id))
    if cur.fetchone():
        conn.close()
        return False, "Нельзя выкинуть экипированный предмет. Сначала снимите его."
    
    # Удаляем предмет
    cur.execute('DELETE FROM player_items WHERE id = ?', (player_item_id,))
    conn.commit()
    conn.close()
    
    return True, "Предмет выкинут!"


def create_player_item_with_rarity(owner_id, template_id, level, rarity):
    """Создает предмет с указанной редкостью"""
    return create_player_item(owner_id, template_id, level, rarity)


def get_player_items(owner_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''SELECT pi.id, pi.template_id, pi.level, pi.rarity, pi.upgrade_level, pi.quantity
                   FROM player_items pi
                   LEFT JOIN equipment e ON pi.id = e.player_item_id
                   WHERE pi.owner_id = ? AND e.player_item_id IS NULL
                ''', (owner_id,))
    rows = cur.fetchall()
    conn.close()
    items = []
    for row in rows:
        item_id, template_id, level, rarity, upgrade, qty = row
        stats = get_item_stats(template_id, level, rarity, upgrade)
        if stats:
            stats['id'] = item_id
            stats['template_id'] = template_id
            stats['level'] = level
            stats['rarity'] = rarity
            stats['upgrade_level'] = upgrade
            stats['quantity'] = qty
            items.append(stats)
    return items


def get_equipped_items(character_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        SELECT equipment.slot, player_items.id, player_items.template_id, player_items.level, player_items.rarity, player_items.upgrade_level
        FROM equipment
        JOIN player_items ON equipment.player_item_id = player_items.id
        WHERE equipment.character_id = ?
    ''', (character_id,))
    rows = cur.fetchall()
    conn.close()
    equipped = {}
    for row in rows:
        slot, item_id, template_id, level, rarity, upgrade = row
        stats = get_item_stats(template_id, level, rarity, upgrade)
        if stats:
            stats['id'] = item_id
            stats['slot'] = slot
            stats['rarity'] = rarity
            stats['upgrade_level'] = upgrade
            stats['bonus_crit'] = stats.get('bonus_crit', 0)
            stats['bonus_dodge'] = stats.get('bonus_dodge', 0)
            equipped[slot] = stats
    return equipped


def equip_item(character_id, player_item_id, slot):
    """Экипировка предмета с проверкой уровня и класса"""
    from core import get_character_by_id  # ✅ ИМПОРТ ВНУТРИ
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Получаем данные предмета
    cur.execute('SELECT owner_id, template_id, level, rarity, upgrade_level, quantity FROM player_items WHERE id = ?', (player_item_id,))
    row = cur.fetchone()
    if not row or row[0] != character_id:
        conn.close()
        return False
    
    owner_id, template_id, level, rarity, upgrade_level, quantity = row
    
    # ✅ Проверяем возможность экипировки
    char = get_character_by_id(character_id)
    if char:
        can, msg = can_equip_item(character_id, template_id)
        if not can:
            conn.close()
            return False
    
    # Проверяем, есть ли уже предмет в этом слоте
    cur.execute('SELECT player_item_id FROM equipment WHERE character_id = ? AND slot = ?', (character_id, slot))
    old = cur.fetchone()
    
    if old:
        # Снимаем старый предмет (сохраняя его данные)
        old_item_id = old[0]
        cur.execute('SELECT template_id, level, rarity, upgrade_level FROM player_items WHERE id = ?', (old_item_id,))
        old_data = cur.fetchone()
        if old_data:
            # Возвращаем старый предмет в инвентарь
            cur.execute('''
                SELECT id, quantity FROM player_items 
                WHERE owner_id = ? AND template_id = ? AND level = ? AND rarity = ? AND upgrade_level = ?
                AND id NOT IN (SELECT player_item_id FROM equipment WHERE character_id = ?)
            ''', (character_id, old_data[0], old_data[1], old_data[2], old_data[3], character_id))
            existing = cur.fetchone()
            
            if existing:
                cur.execute('UPDATE player_items SET quantity = quantity + 1 WHERE id = ?', (existing[0],))
                cur.execute('DELETE FROM player_items WHERE id = ?', (old_item_id,))
            else:
                cur.execute('UPDATE player_items SET owner_id = ?, quantity = 1 WHERE id = ?', (character_id, old_item_id))
        
        cur.execute('DELETE FROM equipment WHERE character_id = ? AND slot = ?', (character_id, slot))
    
    # Если предметов несколько - уменьшаем количество
    if quantity > 1:
        cur.execute('UPDATE player_items SET quantity = quantity - 1 WHERE id = ?', (player_item_id,))
        # Создаём новый предмет для экипировки с ТЕМИ ЖЕ параметрами
        cur.execute('''
            INSERT INTO player_items (owner_id, template_id, level, rarity, upgrade_level, quantity)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (character_id, template_id, level, rarity, upgrade_level))
        new_item_id = cur.lastrowid
    else:
        # Если предмет один - просто перемещаем его ID в экипировку
        new_item_id = player_item_id
    
    # Добавляем в экипировку
    cur.execute('INSERT INTO equipment (character_id, slot, player_item_id) VALUES (?, ?, ?)',
                (character_id, slot, new_item_id))
    
    conn.commit()
    conn.close()
    return True


def unequip_item(character_id, slot):
    """
    Снятие предмета - ПЕРЕМЕЩАЕТ предмет обратно в инвентарь
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Получаем ID предмета в экипировке
    cur.execute('SELECT player_item_id FROM equipment WHERE character_id = ? AND slot = ?', (character_id, slot))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False
    
    item_id = row[0]
    
    # Получаем данные предмета
    cur.execute('SELECT template_id, level, rarity, upgrade_level FROM player_items WHERE id = ?', (item_id,))
    data = cur.fetchone()
    if not data:
        conn.close()
        return False
    
    template_id, level, rarity, upgrade_level = data
    
    # Удаляем из экипировки
    cur.execute('DELETE FROM equipment WHERE character_id = ? AND slot = ?', (character_id, slot))
    
    # Проверяем, есть ли уже такой предмет в инвентаре (по template_id, level, rarity, upgrade_level)
    cur.execute('''
        SELECT id, quantity FROM player_items 
        WHERE owner_id = ? AND template_id = ? AND level = ? AND rarity = ? AND upgrade_level = ?
        AND id != ?
    ''', (character_id, template_id, level, rarity, upgrade_level, item_id))
    
    existing = cur.fetchone()
    
    if existing:
        # Если такой предмет уже есть в инвентаре - увеличиваем количество
        cur.execute('UPDATE player_items SET quantity = quantity + 1 WHERE id = ?', (existing[0],))
        cur.execute('DELETE FROM player_items WHERE id = ?', (item_id,))
    else:
        # Если такого предмета нет - перемещаем его в инвентарь
        cur.execute('''
            UPDATE player_items 
            SET owner_id = ?, quantity = 1
            WHERE id = ?
        ''', (character_id, item_id))
    
    conn.commit()
    conn.close()
    return True


def generate_shop_item(owner_id, template_name, level):
    template_id = get_item_template_id_by_name(template_name)
    if not template_id:
        return None
    item_id = create_player_item(owner_id, template_id, level, rarity=1)
    return item_id


def upgrade_item(player_item_id, crystal_id=None):
    """
    Улучшение предмета (заточка)
    
    Args:
        player_item_id (int): ID предмета в player_items
        crystal_id (int, optional): ID кристалла в player_consumables
    
    Returns:
        tuple: (success, message)
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''SELECT owner_id, template_id, level, rarity, upgrade_level 
                   FROM player_items WHERE id = ?''', (player_item_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None, "Предмет не найден"
    
    owner_id, template_id, level, rarity, upgrade_level = row

    if upgrade_level >= 10:
        conn.close()
        return None, "❌ Предмет уже имеет максимальный уровень заточки (+10)"

    # ---- ПРАВИЛЬНАЯ ФОРМУЛА СТОИМОСТИ ----
    rarity_price_mult = {
        1: 1.0,    # ⚪ Обычный
        2: 1.5,    # 🟢 Необычный
        3: 2.5,    # 🔵 Редкий
        4: 4.0,    # 🟣 Эпический
        5: 6.0     # 🟠 Легендарный
    }
    
    base_price = 100 + upgrade_level * 250
    price = int(base_price * rarity_price_mult.get(rarity, 1.0))

    cur.execute('SELECT silver FROM characters WHERE id = ?', (owner_id,))
    silver_row = cur.fetchone()
    if not silver_row or silver_row[0] < price:
        conn.close()
        return None, f"❌ Недостаточно серебра! Нужно {price}💰"

    # ---- ПРАВИЛЬНЫЙ ШАНС ЗАТОЧКИ ----
    if upgrade_level < 4:
        base_chance = 100
    elif upgrade_level == 4:
        base_chance = 85
    elif upgrade_level == 5:
        base_chance = 75
    elif upgrade_level == 6:
        base_chance = 65
    elif upgrade_level == 7:
        base_chance = 50
    elif upgrade_level == 8:
        base_chance = 40
    elif upgrade_level == 9:
        base_chance = 30
    else:  # upgrade_level >= 10
        base_chance = 10

    crystal_bonus = 0
    crystal_name = "без кристалла"
    
    if crystal_id:
        # Получаем данные о кристалле из player_consumables
        cur.execute('SELECT consumable_template_id, quantity FROM player_consumables WHERE owner_id = ? AND id = ?', (owner_id, crystal_id))
        crystal_row = cur.fetchone()
        if not crystal_row or crystal_row[1] <= 0:
            conn.close()
            return None, "❌ У вас нет такого кристалла"
        
        template_id_crystal = crystal_row[0]
        
        # Получаем бонус из шаблона расходника
        cur.execute('SELECT restore_percent, name FROM consumable_templates WHERE id = ? AND restore_type = "crystal"', (template_id_crystal,))
        template_row = cur.fetchone()
        if not template_row:
            conn.close()
            return None, "❌ Кристалл не найден в шаблонах"
        
        crystal_bonus = template_row[0]  # 15%, 35% или 55%
        crystal_name = template_row[1]
        
        # Уменьшаем количество кристаллов
        new_qty = crystal_row[1] - 1
        if new_qty == 0:
            cur.execute('DELETE FROM player_consumables WHERE owner_id = ? AND id = ?', (owner_id, crystal_id))
        else:
            cur.execute('UPDATE player_consumables SET quantity = ? WHERE owner_id = ? AND id = ?', (new_qty, owner_id, crystal_id))

    final_chance = min(95, base_chance + crystal_bonus)
    cur.execute('UPDATE characters SET silver = silver - ? WHERE id = ?', (price, owner_id))

    success = random.random() * 100 < final_chance

    # ---- НАЗВАНИЕ РЕДКОСТИ ДЛЯ СООБЩЕНИЯ ----
    rarity_names = {
        1: 'Обычный',
        2: 'Необычный',
        3: 'Редкий',
        4: 'Эпический',
        5: 'Легендарный'
    }
    rarity_name = rarity_names.get(rarity, 'Обычный')
    rarity_icon = {1: '⚪', 2: '🟢', 3: '🔵', 4: '🟣', 5: '🟠'}.get(rarity, '⚪')

    if success:
        new_level = upgrade_level + 1
        cur.execute('UPDATE player_items SET upgrade_level = ? WHERE id = ?', (new_level, player_item_id))
        conn.commit()
        conn.close()
        from core import recalc_stats
        recalc_stats(owner_id)
        return True, f"✅ Заточка успешна! {rarity_icon} {rarity_name} предмет улучшен до +{new_level}. Шанс был {final_chance}% (кристалл: {crystal_name})"
    else:
        if upgrade_level >= 5:
            new_level = upgrade_level - 1
            cur.execute('UPDATE player_items SET upgrade_level = ? WHERE id = ?', (new_level, player_item_id))
            conn.commit()
            conn.close()
            from core import recalc_stats
            recalc_stats(owner_id)
            return False, f"❌ Заточка не удалась! {rarity_icon} {rarity_name} предмет понижен до +{new_level}. Шанс был {final_chance}% (кристалл: {crystal_name})"
        else:
            conn.commit()
            conn.close()
            return False, f"❌ Заточка не удалась! {rarity_icon} {rarity_name} предмет остался +{upgrade_level}. Шанс был {final_chance}% (кристалл: {crystal_name})"