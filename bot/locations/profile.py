# locations/profile.py

from core import get_character_async, update_user_async, send_message, render_profile, upload_profile_image, get_character, get_user_async
from items import get_equipped_items
from keyboards import get_profile_keyboard, get_back_keyboard
from .base import navigate_to

async def show_profile(vk, user_id):
    """Показ профиля (только из города)"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
        return
    
    # ✅ Запоминаем, откуда пришли
    user_data = await get_user_async(user_id)
    context = user_data['context']
    current_state = user_data['state']
    
    # Если пришли не из города - запоминаем, но потом вернём в город
    if current_state != 'city' and current_state != 'city2':
        context['return_to'] = current_state
        context['parent_state'] = 'city'  # Всегда возвращаем в город
    
    equipment = get_equipped_items(char['id'])
    profile_text = render_profile(char, equipment)
    
    if char.get('materials'):
        materials_text = "\n🎒 Материалы: " + ", ".join([f"{k}: {v}" for k, v in char['materials'].items()])
        profile_text += materials_text
    
    attachment = upload_profile_image(vk, user_id, char['gender'])
    
    # ✅ Всегда показываем кнопку "В город"
    await send_message(vk, user_id, profile_text, get_profile_keyboard(), attachment=attachment)
    
    # ✅ Всегда состояние profile, но возвращаемся в город
    await update_user_async(user_id, state='profile', context={'parent_state': 'city'})