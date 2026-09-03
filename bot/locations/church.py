# locations/church.py (исправленный)

from core import get_character_async, update_user_async, send_message, get_user_async, recalc_stats_async
from keyboards import get_back_keyboard
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import sqlite3
from config import DB_NAME

CHURCH_IMAGE = 'photo-240828623_456239035'


async def show_church(vk, user_id):
    """Показ Собора"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
        return
    
    user_data = await get_user_async(user_id)
    current_state = user_data['state']
    context = user_data['context']
    
    # Определяем, откуда пришли
    if current_state == 'city2' or context.get('parent_state') == 'city2':
        parent = 'город2'
    else:
        parent = 'город'
    
    context['parent_state'] = parent
    await update_user_async(user_id, context=context)
    
    text = f"⛪ Собор\nВаши 💰: {char['silver']}\n\n"
    if char.get('debuff') == 1:
        text += "☠️ На вас наложено Проклятие (-30% к статам).\nСнимите его за 1000💰."
    elif char.get('debuff') == 2:
        text += "🔥 На вас наложена Печать башни (-50% к статам).\nСнимите её за 3000💰."
    else:
        text += "Вы чувствуете благодать. Проклятий нет."
    
    keyboard = VkKeyboard()
    
    if char.get('debuff') == 1:
        keyboard.add_button('💰 Снять проклятие (1000💰)', color=VkKeyboardColor.PRIMARY,
                            payload={'cmd': 'church_remove_debuff'})
        keyboard.add_line()
    elif char.get('debuff') == 2:
        keyboard.add_button('💰 Снять печать башни (3000💰)', color=VkKeyboardColor.PRIMARY,
                            payload={'cmd': 'church_remove_tower_debuff'})
        keyboard.add_line()
    
    # Кнопка возврата
    if parent == 'город2':
        keyboard.add_button('🏙️ В Озерный Край', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_city2'})
    else:
        keyboard.add_button('🏙️ В город', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_city'})
    
    await send_message(vk, user_id, text, keyboard, attachment=CHURCH_IMAGE)
    await update_user_async(user_id, state='church', context=context)


async def show_church_remove_debuff(vk, user_id, debuff_level=1):
    """Снятие проклятия в Соборе"""
    import sqlite3
    from core import DB_NAME, recalc_stats_async
    
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
        return
    
    if char.get('debuff') != debuff_level:
        await send_message(vk, user_id, 'На вас нет такого проклятия.', get_back_keyboard('город'))
        return
    
    price = 1000 if debuff_level == 1 else 3000
    if char['silver'] < price:
        await send_message(vk, user_id, f'❌ Недостаточно серебра! Нужно {price}💰.', get_back_keyboard('город'))
        return
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE characters SET silver = silver - ?, debuff = 0 WHERE id = ?', (price, char['id']))
    conn.commit()
    conn.close()
    
    await recalc_stats_async(char['id'])
    await send_message(vk, user_id, f'✅ Проклятие снято! Статы восстановлены.', get_back_keyboard('город'))
    await show_church(vk, user_id)