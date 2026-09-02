# locations/profile.py

from core import get_character_async, update_user_async, send_message, render_profile, upload_profile_image, get_character, get_user_async
from items import get_equipped_items
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from keyboards import get_back_keyboard


async def show_profile(vk, user_id):
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context['parent_state'] = 'camp'
    await update_user_async(user_id, context=context)
    
    equipment = get_equipped_items(char['id'])
    profile_text = render_profile(char, equipment)
    
    if char.get('materials'):
        materials_text = "\n🎒 Материалы: " + ", ".join([f"{k}: {v}" for k, v in char['materials'].items()])
        profile_text += materials_text
    
    attachment = upload_profile_image(vk, user_id, char['gender'])
    
    # ✅ ТОЛЬКО КНОПКА "В ЛАГЕРЬ"
    keyboard = VkKeyboard()
    keyboard.add_button('🏕️ В лагерь', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_camp'})
    
    await send_message(vk, user_id, profile_text, keyboard, attachment=attachment)
    await update_user_async(user_id, state='profile', context=context)