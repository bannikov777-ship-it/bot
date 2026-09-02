# locations/market2.py - Рынок Озерного Края

from core import get_character_async, update_user_async, send_message, get_user_async
from keyboards import get_back_keyboard
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import sqlite3
from config import DB_NAME

MARKET2_IMAGE = 'photo-240828623_456239033'


async def show_market2(vk, user_id):
    """Показ рынка Озерного Края"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context['parent_state'] = 'city2'
    await update_user_async(user_id, context=context)
    
    text = f"🏪 Рынок Озерного Края\n\n🏞️ Здесь можно найти редкие товары, привезённые с озера.\nВаши 💰: {char['silver']}"
    
    keyboard = VkKeyboard()
    keyboard.add_button('🗡️ Оружие', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'market2_weapons'})
    keyboard.add_button('🛡️ Броня', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'market2_armor'})
    keyboard.add_line()
    keyboard.add_button('🎣 Снаряжение', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'market2_gear'})
    keyboard.add_button('💎 Кристаллы', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'market2_crystals'})
    keyboard.add_line()
    keyboard.add_button('🏙️ В Озерный Край', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_city2'})
    
    await send_message(vk, user_id, text, keyboard, attachment=MARKET2_IMAGE)
    await update_user_async(user_id, state='market2', context=context)


async def show_market2_category(vk, user_id, category):
    """Показ категории товаров"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    # Товары для второго города
    items = {
        'weapons': [
            ('Острога', 1, 300),
            ('Гарпун', 5, 500),
            ('Трезубец', 10, 800),
            ('Копьё рыбака', 15, 1200),
        ],
        'armor': [
            ('Кожа нерпы', 1, 400),
            ('Броня из чешуи', 5, 600),
            ('Кольчуга водолаза', 10, 900),
            ('Доспехи капитана', 15, 1500),
        ],
        'gear': [
            ('Весло', 1, 200),
            ('Сеть', 5, 350),
            ('Бочонок с водой', 10, 500),
            ('Компас', 15, 700),
        ],
        'crystals': [
            ('Водный кристалл', 1, 300),
            ('Озерный кристалл', 5, 500),
            ('Глубинный кристалл', 10, 800),
            ('Кристалл духа озера', 15, 1200),
        ]
    }
    
    category_items = items.get(category, [])
    if not category_items:
        await send_message(vk, user_id, '❌ Категория не найдена.', get_back_keyboard('город2'))
        return
    
    category_names = {
        'weapons': '🗡️ Оружие',
        'armor': '🛡️ Броня',
        'gear': '🎣 Снаряжение',
        'crystals': '💎 Кристаллы'
    }
    
    text = f"📦 {category_names.get(category, category)}\n\n"
    text += f"Ваши 💰: {char['silver']}\n\n"
    
    keyboard = VkKeyboard()
    for name, level, price in category_items:
        text += f"• {name} (ур.{level}) — {price}💰\n"
        keyboard.add_button(f"{name} {price}💰", color=VkKeyboardColor.PRIMARY,
                           payload={'cmd': 'market2_buy', 'item_name': name, 'price': price, 'level': level})
        keyboard.add_line()
    
    keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_market2'})
    
    await send_message(vk, user_id, text, keyboard)
    await update_user_async(user_id, state='market2_category', context={'parent_state': 'market2'})


async def show_market2_buy(vk, user_id, item_name, price, level):
    """Покупка предмета"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    if char['silver'] < price:
        await send_message(vk, user_id, f'❌ Недостаточно серебра! Нужно {price}💰.', get_back_keyboard('город2'))
        return
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Ищем шаблон предмета
    cur.execute('SELECT id FROM item_templates WHERE name LIKE ? LIMIT 1', (f'%{item_name}%',))
    template = cur.fetchone()
    
    if template:
        cur.execute('''
            INSERT INTO player_items (owner_id, template_id, level, rarity, quantity)
            VALUES (?, ?, ?, ?, 1)
        ''', (char['id'], template[0], level, 1))
    else:
        # Если шаблона нет — создаём базовый
        cur.execute('''
            INSERT INTO player_items (owner_id, template_id, level, rarity, quantity)
            VALUES (?, (SELECT id FROM item_templates LIMIT 1), ?, 1, 1)
        ''', (char['id'], level))
    
    cur.execute('UPDATE characters SET silver = silver - ? WHERE id = ?', (price, char['id']))
    conn.commit()
    conn.close()
    
    await send_message(vk, user_id, f'✅ Вы купили **{item_name}** за {price}💰!', get_back_keyboard('город2'))
    await show_market2(vk, user_id)