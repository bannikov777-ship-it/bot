from core import get_character_async, update_user_async, send_message, get_user_async, recalc_stats_async
from keyboards import get_back_keyboard
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import sqlite3
from config import DB_NAME

CHURCH2_IMAGE = 'photo-240828623_456239035'


async def show_church2(vk, user_id):
    """Показ Храма Озера"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context['parent_state'] = 'city2'
    await update_user_async(user_id, context=context)
    
    text = f"⛪ Храм Озера\n\n🌊 Здесь поклоняются духу озера.\n\nВаши 💰: {char['silver']}\n\n"
    
    if char.get('debuff') == 1:
        text += "☠️ На вас наложено Проклятие (-30% к статам).\nСнимите его за 1000💰."
    elif char.get('debuff') == 2:
        text += "🔥 На вас наложена Печать башни (-50% к статам).\nСнимите её за 3000💰."
    else:
        text += "Вы чувствуете благословение озера. Проклятий нет."
    
    keyboard = VkKeyboard()
    
    # ✅ КНОПКА СНЯТИЯ (если есть дебафф)
    if char.get('debuff') == 1:
        keyboard.add_button('💰 Снять проклятие (1000💰)', color=VkKeyboardColor.PRIMARY,
                            payload={'cmd': 'church2_remove_debuff'})
        keyboard.add_line()
    elif char.get('debuff') == 2:
        keyboard.add_button('💰 Снять печать башни (3000💰)', color=VkKeyboardColor.PRIMARY,
                            payload={'cmd': 'church2_remove_tower_debuff'})
        keyboard.add_line()
    
    # ✅ КНОПКА ВОЗВРАТА (всегда на отдельной строке)
    keyboard.add_button('🏙️ В Озерный Край', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_city2'})
    
    await send_message(vk, user_id, text, keyboard, attachment=CHURCH2_IMAGE)
    await update_user_async(user_id, state='church2', context=context)


async def show_church2_remove_debuff(vk, user_id, debuff_level=1):
    """Снятие проклятия в Храме Озера"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    if char.get('debuff') != debuff_level:
        await send_message(vk, user_id, 'На вас нет такого проклятия.', get_back_keyboard('город2'))
        return
    
    price = 1000 if debuff_level == 1 else 3000
    if char['silver'] < price:
        await send_message(vk, user_id, f'❌ Недостаточно серебра! Нужно {price}💰.', get_back_keyboard('город2'))
        return
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE characters SET silver = silver - ?, debuff = 0 WHERE id = ?', (price, char['id']))
    conn.commit()
    conn.close()
    
    await recalc_stats_async(char['id'])
    await send_message(vk, user_id, f'✅ Проклятие снято! Статы восстановлены.', get_back_keyboard('город2'))
    await show_church2(vk, user_id)