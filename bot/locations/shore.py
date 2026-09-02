# locations/shore.py - Побережье (15+ уровень)

from core import get_character_async, update_user_async, send_message, get_user_async
from keyboards import get_back_keyboard
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

SHORE_IMAGE = 'photo-240828623_456239036'  # можно поставить свою картинку


async def show_shore(vk, user_id):
    """Показ побережья (15+ уровень)"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
        return
    
    if char['level'] < 15:
        keyboard = VkKeyboard()
        keyboard.add_button('🌉 На мост', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_bridge'})
        await send_message(vk, user_id, f'🌊 Побережье доступно только с 15 уровня. Ваш уровень: {char["level"]}.', keyboard)
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context['parent_state'] = 'shore'
    await update_user_async(user_id, context=context)
    
    text = (
        "🌊 Побережье Озерного Края\n\n"
        "🏖️ Песчаный берег тянется вдоль озера.\n"
        "🌊 Волны накатывают на берег.\n"
        "🦀 Вода кишит опасными тварями.\n"
        "💀 Здесь водятся водяные монстры уровня 15+.\n\n"
        "⚔️ Эта локация в разработке!\n"
        "Скоро здесь появятся новые монстры."
    )
    
    keyboard = VkKeyboard()
    keyboard.add_button('🌉 На мост', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_bridge'})
    
    await send_message(vk, user_id, text, keyboard, attachment=SHORE_IMAGE)
    await update_user_async(user_id, state='shore', context=context)