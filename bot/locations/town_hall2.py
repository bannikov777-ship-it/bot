# locations/town_hall2.py (КНОПКИ С 1 УРОВНЯ)

from core import get_character_async, update_user_async, send_message, get_user_async, recalc_stats_async
from keyboards import get_back_keyboard, get_class_choice_keyboard
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
    
    print(f"🔍 show_town_hall2: level={char.get('level')}, class={char.get('class')}")
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context['parent_state'] = 'city2'
    await update_user_async(user_id, context=context)
    
    text = "🏛️ Ратуша Озерного Края\n\n🏞️ Здесь вершится судьба города у озера.\n\nЧто вас интересует?"
    
    keyboard = VkKeyboard()
    
    # ✅ Кнопка "Выбор класса" — ВСЕГДА С 1 УРОВНЯ!
    if not char.get('class'):
        # Нет класса → выбор
        keyboard.add_button('🎯 Выбор класса', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'town_hall_class2'})
    else:
        # Есть класс → смена за деньги
        keyboard.add_button('🔄 Сменить класс (10 000💰)', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'town_hall_change_class2'})
    keyboard.add_line()
    
    keyboard.add_button('📊 Рейтинг', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'rating2'})
    keyboard.add_line()
    
    keyboard.add_button('🏙️ В Озерный Край', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_city2_direct'})
    
    await send_message(vk, user_id, text, keyboard, attachment=TOWN_HALL2_IMAGE)
    await update_user_async(user_id, state='town_hall2', context=context)


async def show_town_hall_class2(vk, user_id):
    """Выбор класса (проверка на 20 уровень внутри)"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    # ✅ Проверка на 20 уровень
    if char['level'] < 20:
        await send_message(vk, user_id, 
            f'❌ Выбор класса доступен только с 20 уровня.\n'
            f'Ваш уровень: {char["level"]}\n\n'
            f'🎯 Достигните 20 уровня, чтобы выбрать класс!',
            get_back_keyboard('город2'))
        await show_town_hall2(vk, user_id)
        return
    
    if char['class']:
        await send_message(vk, user_id, f'Вы уже выбрали класс: {char["class"]}.\n\nДля смены класса используйте кнопку "Сменить класс" (10 000💰).', get_back_keyboard('город2'))
        await show_town_hall2(vk, user_id)
        return
    
    keyboard = VkKeyboard()
    keyboard.add_button('🛡 Оруженосец', color=VkKeyboardColor.PRIMARY, payload={'class': 'Оруженосец'})
    keyboard.add_button('🏹 Охотник', color=VkKeyboardColor.PRIMARY, payload={'class': 'Охотник'})
    keyboard.add_line()
    keyboard.add_button('✨ Послушник', color=VkKeyboardColor.PRIMARY, payload={'class': 'Послушник'})
    keyboard.add_line()
    keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'town_hall2'})
    
    await send_message(vk, user_id, 'Выберите свой класс:', keyboard)
    await update_user_async(user_id, state='awaiting_class2', context={'parent_state': 'town_hall2'})


async def show_town_hall_change_class2(vk, user_id):
    """Смена класса — проверка на 20 уровень и серебро"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    # ✅ Проверка на 20 уровень
    if char['level'] < 20:
        await send_message(vk, user_id, 
            f'❌ Смена класса доступна только с 20 уровня.\n'
            f'Ваш уровень: {char["level"]}\n\n'
            f'🎯 Достигните 20 уровня, чтобы менять класс!',
            get_back_keyboard('город2'))
        await show_town_hall2(vk, user_id)
        return
    
    if not char['class']:
        await send_message(vk, user_id, '❌ Сначала выберите класс (бесплатно).', get_back_keyboard('город2'))
        await show_town_hall_class2(vk, user_id)
        return
    
    # Проверяем серебро
    if char['silver'] < 10000:
        await send_message(vk, user_id, 
            f'❌ Недостаточно серебра! Нужно 10 000💰.\n'
            f'Ваше серебро: {char["silver"]}💰',
            get_back_keyboard('город2'))
        await show_town_hall2(vk, user_id)
        return
    
    keyboard = get_class_choice_keyboard()
    keyboard.add_line()
    keyboard.add_button('❌ Отмена', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'town_hall2'})
    
    await send_message(vk, user_id, 
        f'⚠️ СМЕНА КЛАССА\n\n'
        f'Текущий класс: {char["class"]}\n'
        f'Уровень: {char["level"]}\n'
        f'💰 Стоимость: 10 000 серебра\n\n'
        f'Выберите новый класс:',
        keyboard)
    await update_user_async(user_id, state='awaiting_change_class2', context={'parent_state': 'town_hall2'})


async def process_change_class2(vk, user_id, class_name):
    """Обработка смены класса (платная)"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    if char['level'] < 20:
        await send_message(vk, user_id, f'❌ Смена класса доступна только с 20 уровня.', get_back_keyboard('город2'))
        return
    
    if not char['class']:
        await send_message(vk, user_id, '❌ Сначала выберите класс (бесплатно).', get_back_keyboard('город2'))
        return
    
    if char['silver'] < 10000:
        await send_message(vk, user_id, f'❌ Недостаточно серебра! Нужно 10 000💰.', get_back_keyboard('город2'))
        return
    
    old_class = char['class']
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE characters SET class = ?, silver = silver - 10000 WHERE id = ?', (class_name, char['id']))
    conn.commit()
    conn.close()
    
    await recalc_stats_async(char['id'])
    
    await send_message(vk, user_id, 
        f'✅ Класс успешно изменён!\n\n'
        f'Был: {old_class}\n'
        f'Стал: {class_name}\n'
        f'💰 Снято: 10 000 серебра\n'
        f'📊 Статы пересчитаны!',
        get_back_keyboard('город2'))
    
    await show_town_hall2(vk, user_id)


async def show_rating2(vk, user_id):
    """Показ рейтинга"""
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