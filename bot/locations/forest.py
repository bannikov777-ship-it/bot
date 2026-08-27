# locations/forest.py
import random
import asyncio
from core import get_character_async, update_user_async, send_message, update_max_forest_depth, get_user_async
from battle import start_battle, delay_with_message
from keyboards import get_back_keyboard
from .base import FOREST_IMAGE, FOREST_DEEP_IMAGE, FOREST_WANDER_IMAGE, FOREST_EXIT_IMAGE, delay_action

async def show_forest(vk, user_id):
    """Показ леса"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
        return
    if char['level'] < 1:
        await send_message(vk, user_id, f'🌲 Лес доступен с 1 уровня. Ваш уровень: {char["level"]}.', get_back_keyboard('город'))
        return
    
    # Показываем картинку входа в лес
    await send_message(vk, user_id, "🌲 Вы входите в лес...", attachment=FOREST_IMAGE)
    
    # Задержка 2-5 секунд
    await asyncio.sleep(random.randint(2, 5))
    
    user_data = await get_user_async(user_id)
    context = user_data.get('context', {}) if isinstance(user_data, dict) else {}
    if 'forest_depth' not in context:
        context['forest_depth'] = 0
        await update_user_async(user_id, context=context)
    depth = context.get('forest_depth', 0)
    await start_battle(vk, user_id, 'forest', depth)

async def forest_deep(vk, user_id):
    """Углубление в лес - с задержкой и блокировкой"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
        return
    
    # Проверяем блокировку и запускаем с задержкой
    success = await delay_action(vk, user_id, 'forest_deep', delay_range=(3, 8))
    if not success:
        return

async def forest_deep_execute(vk, user_id):
    """Выполнение углубления в лес (после задержки)"""
    user_data = await get_user_async(user_id)
    context = user_data.get('context', {}) if isinstance(user_data, dict) else {}
    old_depth = context.get('forest_depth', 0)
    depth = old_depth + 1
    context['forest_depth'] = depth
    await update_user_async(user_id, context=context)
    print(f"🌲 forest_deep: старый depth={old_depth}, новый depth={depth}")
    char = await get_character_async(user_id)
    if char:
        update_max_forest_depth(char['id'], depth)
    await start_battle(vk, user_id, 'forest', depth)

async def forest_wander(vk, user_id):
    """Бродяжничество в лесу - с задержкой и блокировкой"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
        return
    
    success = await delay_action(vk, user_id, 'forest_wander', delay_range=(3, 8))
    if not success:
        return

async def forest_wander_execute(vk, user_id):
    """Выполнение бродяжничества в лесу (после задержки)"""
    user_data = await get_user_async(user_id)
    context = user_data.get('context', {}) if isinstance(user_data, dict) else {}
    depth = context.get('forest_depth', 0)
    await start_battle(vk, user_id, 'forest', depth)

async def back_to_exit(vk, user_id):
    """Возврат к выходу"""
    user_data = await get_user_async(user_id)
    context = user_data.get('context', {}) if isinstance(user_data, dict) else {}
    context.pop('forest_depth', None)
    await update_user_async(user_id, context=context)
    await delay_with_message(vk, user_id, "🚶 Вы выходите из леса...", attachment=FOREST_EXIT_IMAGE, delay_range=(2, 4))
    from .exit import show_exit
    await show_exit(vk, user_id)