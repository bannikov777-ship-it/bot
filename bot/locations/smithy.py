# locations/smithy.py (ПОЛНЫЙ ИСПРАВЛЕННЫЙ)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from core import get_character_async, update_user_async, send_message, get_player_crystals, get_character, get_user_async, DB_NAME
from keyboards import get_back_keyboard
from items import get_equipped_items, upgrade_item
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

SMITHY_IMAGE = 'photo-240828623_456239244'

async def show_smithy(vk, user_id):
    """Показ кузницы"""
    try:
        char = await get_character_async(user_id)
        if not char:
            await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
            return
        
        equipment = get_equipped_items(char['id'])
        upgradable = [item for item in equipment.values() if item['upgrade_level'] < 10]
        
        if not upgradable:
            await send_message(vk, user_id, 'У вас нет предметов для улучшения (макс +10).', get_back_keyboard('рынок'), attachment=SMITHY_IMAGE)
            return
        
        keyboard = VkKeyboard()
        for item in upgradable:
            upgrade_level = item['upgrade_level']
            rarity = item['rarity']
            
            # ✅ Правильная формула цены
            rarity_price_mult = {
                1: 1.0,    # ⚪ Обычный
                2: 1.5,    # 🟢 Необычный
                3: 2.5,    # 🔵 Редкий
                4: 4.0,    # 🟣 Эпический
                5: 6.0     # 🟠 Легендарный
            }
            base_price = 100 + upgrade_level * 250
            price = int(base_price * rarity_price_mult.get(rarity, 1.0))
            
            # ✅ Правильный шанс
            chance = get_upgrade_chance(upgrade_level)
            
            label = f"{item['name']} (+{upgrade_level}) — {price}💰 (шанс {chance}%)"
            keyboard.add_button(label, color=VkKeyboardColor.PRIMARY,
                                payload={'cmd': 'smithy_select_item', 'item_id': item['id']})
            keyboard.add_line()
        
        keyboard.add_button('🏪 На рынок', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_market'})
        
        await send_message(vk, user_id, f"⚒ Кузница\nВаши 💰: {char['silver']}\nВыберите предмет для улучшения:", keyboard, attachment=SMITHY_IMAGE)
        
        user_data = await get_user_async(user_id)
        context = user_data['context']
        context['parent_state'] = 'market'
        await update_user_async(user_id, state='smithy', context=context)
        
    except Exception as e:
        print(f"❌ Ошибка в show_smithy: {e}")
        import traceback
        traceback.print_exc()
        await send_message(vk, user_id, f'⚠️ Ошибка в кузнице: {e}', get_back_keyboard('рынок'))


def get_upgrade_chance(upgrade_level):
    """
    Получение шанса заточки в зависимости от уровня
    
    ✅ Новые шансы:
    0-3: 100%
    4: 85%
    5: 75%
    6: 65%
    7: 50%
    8: 40%
    9: 30%
    10: 10%
    """
    if upgrade_level < 4:
        return 100
    elif upgrade_level == 4:
        return 85
    elif upgrade_level == 5:
        return 75
    elif upgrade_level == 6:
        return 65
    elif upgrade_level == 7:
        return 50
    elif upgrade_level == 8:
        return 40
    elif upgrade_level == 9:
        return 30
    elif upgrade_level >= 10:
        return 10
    return 100


async def show_smithy_upgrade_menu(vk, user_id, item_id):
    """Меню улучшения предмета"""
    try:
        char = await get_character_async(user_id)
        if not char:
            await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
            return
        
        equipment = get_equipped_items(char['id'])
        item = None
        for eq_item in equipment.values():
            if eq_item['id'] == item_id:
                item = eq_item
                break
        
        if not item:
            await send_message(vk, user_id, 'Предмет не найден.', get_back_keyboard('кузница'))
            return
        
        upgrade_level = item['upgrade_level']
        rarity = item['rarity']
        
        if upgrade_level >= 10:
            await send_message(vk, user_id, 'Этот предмет уже имеет максимальный уровень заточки (+10).', get_back_keyboard('кузница'))
            return
        
        # ✅ Правильный шанс
        base_chance = get_upgrade_chance(upgrade_level)
        
        # ✅ Правильная цена
        rarity_price_mult = {
            1: 1.0,    # ⚪ Обычный
            2: 1.5,    # 🟢 Необычный
            3: 2.5,    # 🔵 Редкий
            4: 4.0,    # 🟣 Эпический
            5: 6.0     # 🟠 Легендарный
        }
        base_price = 100 + upgrade_level * 250
        price = int(base_price * rarity_price_mult.get(rarity, 1.0))
        
        # Получаем кристаллы игрока
        crystals = get_player_crystals(char['id'])
        
        # Названия редкости
        rarity_names = {
            1: '⚪ Обычный',
            2: '🟢 Необычный',
            3: '🔵 Редкий',
            4: '🟣 Эпический',
            5: '🟠 Легендарный'
        }
        rarity_name = rarity_names.get(rarity, 'Обычный')
        
        keyboard = VkKeyboard()
        
        # Кнопка заточки без кристалла
        keyboard.add_button(f'🔨 Заточить (шанс {base_chance}%, {price}💰)', 
                           color=VkKeyboardColor.PRIMARY,
                           payload={'cmd': 'smithy_upgrade', 'crystal_id': None})
        keyboard.add_line()
        
        # Кнопки с кристаллами
        if crystals:
            for c in crystals:
                bonus = c['bonus']
                total_chance = min(95, base_chance + bonus)
                label = f"{c['icon']} {c['name']} (+{bonus}%) → шанс {total_chance}% (x{c['quantity']})"
                keyboard.add_button(label, color=VkKeyboardColor.PRIMARY,
                                    payload={'cmd': 'smithy_upgrade', 'crystal_id': c['id']})
                keyboard.add_line()
        else:
            keyboard.add_button('💎 Нет кристаллов', color=VkKeyboardColor.SECONDARY)
            keyboard.add_line()
        
        keyboard.add_button('🔙 Назад к списку', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'smithy'})
        
        # Формируем информативное сообщение
        text = (
            f"⚒ Улучшение: {item['name']}\n"
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
        
        await send_message(vk, user_id, text, keyboard)
        
        user_data = await get_user_async(user_id)
        context = user_data['context']
        context['smithy_item_id'] = item_id
        await update_user_async(user_id, state='smithy_upgrade', context=context)
        
    except Exception as e:
        print(f"❌ Ошибка в show_smithy_upgrade_menu: {e}")
        import traceback
        traceback.print_exc()
        await send_message(vk, user_id, f'⚠️ Ошибка: {e}', get_back_keyboard('кузница'))