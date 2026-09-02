# locations/camp.py - Лагерь Искателей

from core import get_character_async, update_user_async, send_message, get_user_async
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from keyboards import get_back_keyboard

CAMP_IMAGE = 'photo-240828623_456239482'


async def show_camp(vk, user_id):
    """Показ лагеря"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context['parent_state'] = 'camp'
    await update_user_async(user_id, context=context)
    
    text = (
        "🏕️ ЛАГЕРЬ ИСКАТЕЛЕЙ\n\n"
        "Здесь ты можешь отдохнуть, проверить свои вещи и подготовиться к приключениям.\n\n"
        "🔥 Костёр тихо потрескивает, вокруг слышны голоса других искателей."
    )
    
    keyboard = VkKeyboard()
    keyboard.add_button('👤 Профиль', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'profile'})
    keyboard.add_button('🎒 Инвентарь', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'inventory'})
    keyboard.add_line()
    keyboard.add_button('📬 Почта', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'mail'})
    keyboard.add_button('🎁 Промокод', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'code_menu'})
    keyboard.add_line()
    keyboard.add_button('📜 Свитки', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'scrolls'})
    keyboard.add_line()
    keyboard.add_button('🏙️ В Стальной Трон', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_city'})
    keyboard.add_button('🏙️ В Озерный Край', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_city2'})
    
    await send_message(vk, user_id, text, keyboard, attachment=CAMP_IMAGE)
    await update_user_async(user_id, state='camp', context=context)