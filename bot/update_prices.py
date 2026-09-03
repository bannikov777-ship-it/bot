# update_prices.py

import sqlite3
from config import DB_NAME

def update_premium_prices():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Новые цены
    prices = {
        1: 30,   # Слабые кристаллы x10
        2: 70,   # Средние кристаллы x5
        3: 100,  # Сильные кристаллы x3
        4: 50,   # Свиток проклятий
        5: 400,  # VIP 25%
        6: 600,  # VIP 50%
        7: 1000  # VIP 100%
    }
    
    for item_id, price in prices.items():
        cur.execute('UPDATE premium_shop SET price = ? WHERE id = ?', (price, item_id))
        print(f"✅ ID {item_id} → {price}💎")
    
    conn.commit()
    conn.close()
    print("✅ Цены обновлены!")

if __name__ == '__main__':
    update_premium_prices()