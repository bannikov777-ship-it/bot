# add_buildings_column.py

import sqlite3
from config import DB_NAME

def add_buildings_column():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    cur.execute("PRAGMA table_info(guilds)")
    columns = [col[1] for col in cur.fetchall()]
    
    if 'buildings' not in columns:
        cur.execute('ALTER TABLE guilds ADD COLUMN buildings TEXT DEFAULT "{}"')
        print("✅ Добавлена колонка buildings в guilds")
    else:
        print("ℹ️ Колонка buildings уже существует")
    
    conn.commit()
    conn.close()
    print("✅ Миграция завершена!")

if __name__ == '__main__':
    add_buildings_column()