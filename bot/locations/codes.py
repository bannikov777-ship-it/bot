# locations/codes.py

from core import get_character_async, send_message, update_user_async
from keyboards import get_back_keyboard
from codes import use_code
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


async def show_codes_menu(vk, user_id):
    """Показ меню промокодов"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
        return
    
    keyboard = VkKeyboard()
    keyboard.add_button('🎁 Ввести промокод', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'code_enter'})
    keyboard.add_line()
    # ✅ МЕНЯЕМ НА "В ЛАГЕРЬ"
    keyboard.add_button('🏕️ В лагерь', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_camp'})
    
    text = f"🎁 Промокоды\n\n"
    text += "Введите промокод и получите награду!\n"
    text += f"Ваши 💰: {char.get('silver', 0)}\n"
    text += f"Ваши 💎: {char.get('crystals', 0)}"
    
    await send_message(vk, user_id, text, keyboard)
    await update_user_async(user_id, state='codes', context={'parent_state': 'camp'})


async def process_code_enter(vk, user_id, code):
    """Обработка ввода промокода (определяем тип автоматически)"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
        return
    
    try:
        code_upper = code.strip().upper()
        
        # ✅ Сначала проверяем постоянный промокод OpenGame
        if code_upper == 'OPENGAME':
            from permanent_promo import use_permanent_promo
            success, msg, reward_type, amount = use_permanent_promo(char['id'], code_upper)
            
            if success:
                char = await get_character_async(user_id)
                keyboard = VkKeyboard()
                keyboard.add_button('🏕️ В лагерь', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_camp'})
                
                await send_message(vk, user_id, 
                    f'✅ {msg}\n\n'
                    f'💰 Серебро: {char.get("silver", 0)}\n'
                    f'💎 Кристаллы: {char.get("crystals", 0)}',
                    keyboard)
                await update_user_async(user_id, state='camp', context={'parent_state': 'camp'})
            else:
                keyboard = VkKeyboard()
                keyboard.add_button('🏕️ В лагерь', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_camp'})
                await send_message(vk, user_id, f'❌ {msg}', keyboard)
                await show_codes_menu(vk, user_id)
            return
        
        # ✅ Если не OpenGame — проверяем обычные промокоды
        from codes import use_code
        result = use_code(char['id'], code_upper)
        print(f"🔍 use_code вернула: {result}")
        
        if isinstance(result, tuple) and len(result) == 4:
            success, msg, amount, reward_type = result
            
            if success:
                char = await get_character_async(user_id)
                keyboard = VkKeyboard()
                keyboard.add_button('🏕️ В лагерь', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_camp'})
                
                await send_message(vk, user_id, 
                    f'✅ {msg}\n\n'
                    f'💰 Серебро: {char.get("silver", 0)}\n'
                    f'💎 Кристаллы: {char.get("crystals", 0)}',
                    keyboard)
                await update_user_async(user_id, state='camp', context={'parent_state': 'camp'})
            else:
                keyboard = VkKeyboard()
                keyboard.add_button('🏕️ В лагерь', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_camp'})
                await send_message(vk, user_id, f'❌ {msg}', keyboard)
                await show_codes_menu(vk, user_id)
        else:
            keyboard = VkKeyboard()
            keyboard.add_button('🏕️ В лагерь', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_camp'})
            await send_message(vk, user_id, f'❌ Ошибка: неожиданный формат ответа', keyboard)
            
    except Exception as e:
        print(f"❌ Ошибка при использовании промокода: {e}")
        import traceback
        traceback.print_exc()
        keyboard = VkKeyboard()
        keyboard.add_button('🏕️ В лагерь', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_camp'})
        await send_message(vk, user_id, f'❌ Ошибка при активации промокода. Попробуйте позже.', keyboard)