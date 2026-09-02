# locations/hunters2.py - Гильдия охотников Озерного Края

from core import get_character_async, update_user_async, send_message, get_user_async
from keyboards import get_back_keyboard
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from quests import get_available_quests, take_quest, get_active_quests, get_completed_quests_count_today
from resources import sell_all_resources

HUNTERS2_IMAGE = 'photo-240828623_456239030'


async def show_hunters2(vk, user_id):
    """Показ гильдии охотников Озерного Края"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context['parent_state'] = 'city2'
    await update_user_async(user_id, context=context)
    
    text = f"🏹 Гильдия охотников Озерного Края\n\n🌊 Здесь охотятся на водных тварей.\n\nВыберите действие:"
    
    keyboard = VkKeyboard()
    keyboard.add_button('💰 Сдать трофеи', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'hunters2_sell'})
    keyboard.add_button('📜 Взять задание', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'hunters2_quests'})
    keyboard.add_line()
    keyboard.add_button('📋 Мои задания', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'hunters2_my_quests'})
    keyboard.add_line()
    keyboard.add_button('🏙️ В Озерный Край', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_city2'})
    
    await send_message(vk, user_id, text, keyboard, attachment=HUNTERS2_IMAGE)
    await update_user_async(user_id, state='hunters2', context=context)


async def show_hunters2_sell(vk, user_id):
    """Продажа трофеев"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    total, msg = await asyncio.to_thread(sell_all_resources, char['id'])
    await send_message(vk, user_id, msg, get_back_keyboard('город2'))
    await show_hunters2(vk, user_id)


async def show_hunters2_quests(vk, user_id):
    """Показ доступных заданий"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    completed_today = get_completed_quests_count_today(char['id'])
    if completed_today >= 3:
        await send_message(vk, user_id, '📅 Вы уже выполнили 3 задания сегодня. Приходите завтра!', get_back_keyboard('город2'))
        return
    
    available = get_available_quests(char['id'])
    if not available:
        await send_message(vk, user_id, '📭 Нет доступных заданий.', get_back_keyboard('город2'))
        return
    
    text = "📜 Доступные задания:\n\n"
    keyboard = VkKeyboard()
    
    for q in available:
        text += f"🔹 {q['name']} – {q['description']} (убить {q['target_count']} монстров)\nНаграда: {q['reward_silver']}💰 + {q['reward_potion_count']} зелий\n\n"
        keyboard.add_button(f"Взять: {q['name'][:20]}", color=VkKeyboardColor.PRIMARY,
                           payload={'cmd': 'hunters2_take_quest', 'quest_id': q['id']})
        keyboard.add_line()
    
    keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_hunters2'})
    
    await send_message(vk, user_id, text, keyboard)
    await update_user_async(user_id, state='hunters2_quests', context={'parent_state': 'hunters2'})


async def show_hunters2_my_quests(vk, user_id):
    """Показ активных заданий"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    quests = get_active_quests(char['id'])
    if not quests:
        await send_message(vk, user_id, 'У вас нет активных заданий.', get_back_keyboard('город2'))
        return
    
    text = "📋 Ваши задания:\n\n"
    for q in quests:
        progress_bar = "█" * int(q['progress'] / q['target'] * 10) + "░" * (10 - int(q['progress'] / q['target'] * 10))
        text += f"🔹 {q['name']} – {q['description']}\nПрогресс: {q['progress']}/{q['target']} [{progress_bar}]\nНаграда: {q['reward_silver']}💰 + {q['reward_potion_count']} зелий\n\n"
    
    await send_message(vk, user_id, text, get_back_keyboard('город2'))
    await update_user_async(user_id, state='hunters2_my_quests', context={'parent_state': 'hunters2'})


async def show_hunters2_take_quest(vk, user_id, quest_id):
    """Взятие задания"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    success, msg = take_quest(char['id'], quest_id)
    if success:
        await send_message(vk, user_id, f'✅ {msg}', get_back_keyboard('город2'))
    else:
        await send_message(vk, user_id, f'❌ {msg}', get_back_keyboard('город2'))
    
    await show_hunters2(vk, user_id)