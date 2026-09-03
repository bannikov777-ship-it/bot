# locations/smithy2.py - Кузница Озерного Края

from core import get_character_async, update_user_async, send_message, get_user_async, get_player_crystals
from keyboards import get_back_keyboard
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from items import get_equipped_items, upgrade_item

SMITHY2_IMAGE = 'photo-240828623_456239244'


async def show_smithy2(vk, user_id):
    """Показ кузницы Озерного Края"""
    try:
        char = await get_character_async(user_id)
        if not char:
            await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
            return
        
        user_data = await get_user_async(user_id)
        context = user_data['context']
        context['parent_state'] = 'city2'
        await update_user_async(user_id, context=context)
        
        equipment = get_equipped_items(char['id'])
        upgradable = [item for item in equipment.values() if item['upgrade_level'] < 10]
        
        if not upgradable:
            await send_message(vk, user_id, 'У вас нет предметов для улучшения (макс +10).', get_back_keyboard('город2'), attachment=SMITHY2_IMAGE)
            return
        
        text = f"⚒️ Кузница Озерного Края\n\n🏞️ Здесь куют лучшее оружие на озере.\nВаши 💰: {char['silver']}\n\nВыберите предмет для улучшения:"
        
        keyboard = VkKeyboard()
        for item in upgradable:
            upgrade_level = item['upgrade_level']
            rarity = item['rarity']
            
            rarity_price_mult = {1: 1.0, 2: 1.5, 3: 2.5, 4: 4.0, 5: 6.0}
            base_price = 100 + upgrade_level * 250
            price = int(base_price * rarity_price_mult.get(rarity, 1.0))
            
            keyboard.add_button(
                f"{item['name']} (+{upgrade_level}) — {price}💰",
                color=VkKeyboardColor.PRIMARY,
                payload={'cmd': 'smithy2_select_item', 'item_id': item['id']}
            )
            keyboard.add_line()
        
        keyboard.add_button('🏙️ В Озерный Край', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_city2_direct'})
        
        await send_message(vk, user_id, text, keyboard, attachment=SMITHY2_IMAGE)
        await update_user_async(user_id, state='smithy2', context=context)
        
    except Exception as e:
        print(f"❌ Ошибка в show_smithy2: {e}")
        await send_message(vk, user_id, f'⚠️ Ошибка: {e}', get_back_keyboard('город2'))


async def show_smithy2_upgrade_menu(vk, user_id, item_id):
    """Меню улучшения предмета"""
    try:
        char = await get_character_async(user_id)
        if not char:
            await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
            return
        
        equipment = get_equipped_items(char['id'])
        item = None
        for eq_item in equipment.values():
            if eq_item['id'] == item_id:
                item = eq_item
                break
        
        if not item:
            await send_message(vk, user_id, 'Предмет не найден.', get_back_keyboard('город2'))
            return
        
        upgrade_level = item['upgrade_level']
        rarity = item['rarity']
        
        if upgrade_level >= 10:
            await send_message(vk, user_id, 'Этот предмет уже имеет максимальный уровень заточки (+10).', get_back_keyboard('город2'))
            return
        
        # Шанс заточки
        if upgrade_level < 4:
            base_chance = 100
        elif upgrade_level == 4:
            base_chance = 85
        elif upgrade_level == 5:
            base_chance = 75
        elif upgrade_level == 6:
            base_chance = 65
        elif upgrade_level == 7:
            base_chance = 50
        elif upgrade_level == 8:
            base_chance = 40
        elif upgrade_level == 9:
            base_chance = 30
        else:
            base_chance = 10
        
        # Цена
        rarity_price_mult = {1: 1.0, 2: 1.5, 3: 2.5, 4: 4.0, 5: 6.0}
        base_price = 100 + upgrade_level * 250
        price = int(base_price * rarity_price_mult.get(rarity, 1.0))
        
        crystals = get_player_crystals(char['id'])
        
        rarity_names = {1: '⚪ Обычный', 2: '🟢 Необычный', 3: '🔵 Редкий', 4: '🟣 Эпический', 5: '🟠 Легендарный'}
        rarity_name = rarity_names.get(rarity, 'Обычный')
        
        text = (
            f"⚒️ Улучшение: {item['name']}\n"
            f"📊 Редкость: {rarity_name}\n"
            f"🔨 Текущая заточка: +{upgrade_level}\n"
            f"💰 Стоимость: {price} серебра\n"
            f"📈 Базовый шанс: {base_chance}%\n\n"
            f"💎 Используйте кристалл для повышения шанса:\n"
            f"   🔵 Голубой (+15%)\n"
            f"   🟣 Фиолетовый (+35%)\n"
            f"   🔴 Красный (+55%)\n\n"
            f"Выберите действие:"
        )
        
        keyboard = VkKeyboard()
        keyboard.add_button(f'🔨 Заточить (шанс {base_chance}%, {price}💰)', 
                           color=VkKeyboardColor.PRIMARY,
                           payload={'cmd': 'smithy2_upgrade', 'crystal_id': None})
        keyboard.add_line()
        
        if crystals:
            for c in crystals:
                bonus = c['bonus']
                total_chance = min(95, base_chance + bonus)
                keyboard.add_button(
                    f"{c['icon']} {c['name']} (+{bonus}%) → шанс {total_chance}% (x{c['quantity']})",
                    color=VkKeyboardColor.PRIMARY,
                    payload={'cmd': 'smithy2_upgrade', 'crystal_id': c['id']}
                )
                keyboard.add_line()
        else:
            keyboard.add_button('💎 Нет кристаллов', color=VkKeyboardColor.SECONDARY)
            keyboard.add_line()
        
        keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_smithy2'})
        
        await send_message(vk, user_id, text, keyboard)
        
        user_data = await get_user_async(user_id)
        context = user_data['context']
        context['smithy2_item_id'] = item_id
        await update_user_async(user_id, context=context)
        
    except Exception as e:
        print(f"❌ Ошибка в show_smithy2_upgrade_menu: {e}")
        await send_message(vk, user_id, f'⚠️ Ошибка: {e}', get_back_keyboard('город2'))


async def show_smithy2_upgrade(vk, user_id, crystal_id):
    """Выполнение улучшения"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    item_id = context.get('smithy2_item_id')
    
    if not item_id:
        await send_message(vk, user_id, 'Ошибка: предмет не выбран.', get_back_keyboard('город2'))
        return
    
    success, msg = upgrade_item(item_id, crystal_id)
    
    if success:
        await send_message(vk, user_id, f'✅ {msg}', get_back_keyboard('город2'))
    else:
        await send_message(vk, user_id, f'❌ {msg}', get_back_keyboard('город2'))
    
    await show_smithy2(vk, user_id)