# fix_city_desc.py
import sqlite3
import os

# Путь к БД
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game.db')

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
    UPDATE cities 
    SET description = 'Город, раскинувшийся в центре озера на большом острове, соединённых мостами. Это место, где вода и камень сливаются воедино, а туманы скрывают древние тайны.'
    WHERE id = 2
""")

conn.commit()
conn.close()

print("✅ Описание Озерного Края обновлено!")