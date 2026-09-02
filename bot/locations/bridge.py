# locations/bridge.py (исправленный)

from core import get_character_async, update_user_async, send_message, get_user_async
from keyboards import get_back_keyboard
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

BRIDGE_IMAGE = 'photo-240828623_456239036'


async def show_bridge(vk, user_id):
    """Показ моста между Озерным Краем и лугом"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context['parent_state'] = 'bridge'
    await update_user_async(user_id, context=context)
    
    text = (
        "🌉 Деревянный мост через озеро\n\n"
        "🏞️ С одной стороны — зелёный луг, с другой — город Озерный Край.\n"
        "🌊 Вода тихо плещется о сваи.\n"
        "🐟 Видно, как рыбаки ловят рыбу.\n\n"
        "Куда направимся?"
    )
    
    keyboard = VkKeyboard()
    keyboard.add_button('🌿 На луг', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'bridge_to_meadow'})
    keyboard.add_button('🏙️ В Озерный Край', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'bridge_to_city2'})
    keyboard.add_line()
    keyboard.add_button('🌊 На побережье (15+)', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'go_shore'})
    
    await send_message(vk, user_id, text, keyboard, attachment=BRIDGE_IMAGE)
    await update_user_async(user_id, state='bridge', context=context)