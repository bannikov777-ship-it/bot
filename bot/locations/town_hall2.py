# locations/town_hall2.py

from core import get_character_async, update_user_async, send_message, get_user_async
from keyboards import get_back_keyboard
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import sqlite3
from config import DB_NAME

TOWN_HALL2_IMAGE = 'photo-240828623_456239029'
RATING_IMAGE = 'photo-240828623_456239333'


async def show_town_hall2(vk, user_id):
    """Показ ратуши Озерного Края"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context['parent_state'] = 'city2'
    await update_user_async(user_id, context=context)
    
    text = "🏛️ Ратуша Озерного Края\n\n🏞️ Здесь вершится судьба города у озера.\n\nЧто вас интересует?"
    
    keyboard = VkKeyboard()
    keyboard.add_button('📊 Рейтинг', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'rating2'})
    # ❌ УБИРАЕМ КНОПКУ "Создать гильдию"
    # keyboard.add_button('🛠 Создать гильдию', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'guild_create'})
    keyboard.add_line()
    keyboard.add_button('🏙️ В Озерный Край', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_city2'})
    
    await send_message(vk, user_id, text, keyboard, attachment=TOWN_HALL2_IMAGE)
    await update_user_async(user_id, state='town_hall2', context=context)


async def show_rating2(vk, user_id):
    """Показ рейтинга (общий для всех городов)"""
    from core import format_gender
    
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        SELECT name, gender, class, level, max_forest_depth
        FROM characters
        ORDER BY level DESC, max_forest_depth DESC
        LIMIT 10
    ''')
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        await send_message(vk, user_id, 'Пока нет данных для рейтинга.', get_back_keyboard('город2'), attachment=RATING_IMAGE)
        return
    
    lines = ["📊 Рейтинг игроков:\n"]
    for i, row in enumerate(rows, 1):
        name, gender, class_, level, depth = row
        class_display = class_ if class_ else "Не выбран"
        gender_display = format_gender(gender)
        lines.append(f"{i}. {name} | {gender_display} | {class_display} | Ур.{level} | Глубина: {depth}")
    
    message = "\n".join(lines)
    await send_message(vk, user_id, message, get_back_keyboard('город2'), attachment=RATING_IMAGE)