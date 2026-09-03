# add_missing_items.py

import sqlite3
from config import DB_NAME

def migrate_table():
    """Добавляет недостающие колонки в таблицу item_templates"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Проверяем колонки
    cur.execute("PRAGMA table_info(item_templates)")
    columns = [col[1] for col in cur.fetchall()]
    
    if 'required_level' not in columns:
        cur.execute('ALTER TABLE item_templates ADD COLUMN required_level INTEGER DEFAULT 1')
        print("✅ Добавлена колонка required_level")
    
    if 'class_restriction' not in columns:
        cur.execute('ALTER TABLE item_templates ADD COLUMN class_restriction TEXT')
        print("✅ Добавлена колонка class_restriction")
    
    conn.commit()
    conn.close()
    print("✅ Миграция таблицы завершена!")


def add_missing_items():
    """Добавляет недостающие шаблоны предметов"""
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Проверяем, есть ли уже Топор
    cur.execute("SELECT id FROM item_templates WHERE name = 'Топор'")
    if cur.fetchone():
        print("ℹ️ Топор уже существует")
    else:
        cur.execute('''
            INSERT INTO item_templates (name, slot, base_attack, base_defense, base_hp, base_mana, 
                                        growth_attack, growth_defense, growth_hp, growth_mana, icon,
                                        bonus_crit, bonus_dodge, required_level, class_restriction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Топор', 'weapon_right', 22, 0, 0, 0, 0.28, 0, 0, 0, '🪓', 2, -3, 20, None))
        print("✅ Добавлен Топор")
    
    # Проверяем, есть ли уже Копье
    cur.execute("SELECT id FROM item_templates WHERE name = 'Копье'")
    if cur.fetchone():
        print("ℹ️ Копье уже существует")
    else:
        cur.execute('''
            INSERT INTO item_templates (name, slot, base_attack, base_defense, base_hp, base_mana, 
                                        growth_attack, growth_defense, growth_hp, growth_mana, icon,
                                        bonus_crit, bonus_dodge, required_level, class_restriction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Копье', 'weapon_right', 24, 0, 0, 0, 0.25, 0, 0, 0, '🔱', 4, 5, 20, None))
        print("✅ Добавлено Копье")
    
    # Проверяем левую руку
    left_hand_items = [
        ('Щит', 'weapon_left', 0, 5, 30, 0, 0, 0, 0, 0, '🛡️', 0, 0, 20, 'Оруженосец'),
        ('Кинжал ЛР', 'weapon_left', 0, 1, 10, 0, 0, 0, 0, 0, '🗡️', 2, 0, 20, 'Охотник'),
        ('Книга', 'weapon_left', 0, 2, 15, 5, 0, 0, 0, 0, '📜', 0, 0, 20, 'Послушник'),
        ('Орб ЛР', 'weapon_left', 0, 3, 18, 10, 0, 0, 0, 0, '🔮', 0, 0, 20, 'Послушник'),
    ]
    
    for name, slot, base_attack, base_defense, base_hp, base_mana, g_attack, g_defense, g_hp, g_mana, icon, bonus_crit, bonus_dodge, req_level, class_rest in left_hand_items:
        cur.execute("SELECT id FROM item_templates WHERE name = ? AND slot = ?", (name, slot))
        if cur.fetchone():
            print(f"ℹ️ {name} уже существует")
        else:
            cur.execute('''
                INSERT INTO item_templates (name, slot, base_attack, base_defense, base_hp, base_mana, 
                                            growth_attack, growth_defense, growth_hp, growth_mana, icon,
                                            bonus_crit, bonus_dodge, required_level, class_restriction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, slot, base_attack, base_defense, base_hp, base_mana, 
                  g_attack, g_defense, g_hp, g_mana, icon,
                  bonus_crit, bonus_dodge, req_level, class_rest))
            print(f"✅ Добавлен {name}")
    
    conn.commit()
    conn.close()
    print("✅ Все недостающие предметы добавлены!")


if __name__ == '__main__':
    print("🔄 Запуск миграции...")
    migrate_table()
    print("🔄 Добавление предметов...")
    add_missing_items()
    print("✅ Готово!")