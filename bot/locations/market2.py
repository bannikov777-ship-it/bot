# locations/market2.py (ПОЛНЫЙ ИСПРАВЛЕННЫЙ — с ценами как в market.py)

from core import get_character_async, update_user_async, send_message, get_user_async
from keyboards import get_back_keyboard
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import sqlite3
from config import DB_NAME
from items import get_item_template_id_by_name, create_player_item, get_item_stats

MARKET2_IMAGE = 'photo-240828623_456239033'


def get_shop_item_level20(player_level):
    """Определение уровня предметов для рынка Озерного Края (20+)"""
    if player_level <= 24: return 20
    elif player_level <= 29: return 25
    elif player_level <= 34: return 30
    elif player_level <= 39: return 35
    elif player_level <= 44: return 40
    elif player_level <= 49: return 45
    elif player_level <= 54: return 50
    elif player_level <= 59: return 55
    else: return 60


def get_shop_item_price(shop_level, base_price=250):
    """Расчёт цены предмета (как в первом городе)"""
    return 100 + shop_level * base_price


async def show_market2(vk, user_id):
    """Показ рынка Озерного Края"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context['parent_state'] = 'city2'
    await update_user_async(user_id, context=context)
    
    text = f"🏪 Рынок Озерного Края\n\n🏞️ Здесь можно найти редкие товары.\nВаши 💰: {char['silver']}"
    
    keyboard = VkKeyboard()
    keyboard.add_button('🗡️ Оружие 20+', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'market2_weapons'})
    keyboard.add_button('🛡️ Левая рука', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'market2_left_hand'})
    keyboard.add_line()
    keyboard.add_button('🛡️ Броня', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'market2_armor'})
    keyboard.add_button('🎩 Шлемы', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'market2_helmets'})
    keyboard.add_line()
    keyboard.add_button('👢 Сапоги', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'market2_boots'})
    # ❌ УБРАНА КНОПКА "💎 Кристаллы"
    keyboard.add_line()
    keyboard.add_button('🏙️ В Озерный Край', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_city2'})
    
    await send_message(vk, user_id, text, keyboard, attachment=MARKET2_IMAGE)
    await update_user_async(user_id, state='market2', context=context)


async def show_market2_weapons(vk, user_id):
    """Показ оружия 20+ уровня с характеристиками на кнопках"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    if char['level'] < 20:
        await send_message(vk, user_id, '❌ Оружие 20+ уровня доступно только с 20 уровня.', get_back_keyboard('город2'))
        return
    
    player_level = char['level']
    shop_level = get_shop_item_level20(player_level)
    rarity = 1
    
    weapons = [
        ('Молот', 'weapon_right'),
        ('Топор', 'weapon_right'),
        ('Копье', 'weapon_right'),
        ('Кинжал', 'weapon_right'),
        ('Посох', 'weapon_right'),
        ('Свиток', 'weapon_right'),
        ('Орб', 'weapon_right'),
    ]
    
    text = f"🗡️ Оружие 20+ уровня\n\n"
    text += f"📊 Уровень предметов: {shop_level}\n"
    text += f"Ваши 💰: {char['silver']}\n\n"
    text += "⚪ Только обычные предметы (белые)\n\n"
    
    keyboard = VkKeyboard()
    
    for item_name, slot in weapons:
        template_id = get_item_template_id_by_name(item_name)
        if not template_id:
            continue
        
        stats = get_item_stats(template_id, shop_level, rarity, upgrade_level=0)
        if not stats:
            continue
        
        # Цена как в первом городе
        price = get_shop_item_price(shop_level, base_price=250)
        
        # Формируем текст кнопки с характеристиками
        stats_parts = []
        if stats.get('attack', 0) > 0:
            stats_parts.append(f"⚔{stats['attack']}")
        if stats.get('defense', 0) > 0:
            stats_parts.append(f"🛡{stats['defense']}")
        if stats.get('hp', 0) > 0:
            stats_parts.append(f"❤️{stats['hp']}")
        if stats.get('mana', 0) > 0:
            stats_parts.append(f"💧{stats['mana']}")
        if stats.get('bonus_crit', 0) != 0:
            crit = stats['bonus_crit']
            stats_parts.append(f"💥{crit:+}%")
        if stats.get('bonus_dodge', 0) != 0:
            dodge = stats['bonus_dodge']
            stats_parts.append(f"💨{dodge:+}%")
        
        icon = stats['icon'] if stats else '📦'
        label = f"{icon} {item_name}"
        
        # Добавляем ограничение класса
        class_restriction = None
        if item_name in ['Посох', 'Свиток', 'Орб']:
            class_restriction = 'Послушник'
            label += " (П)"
        
        # Добавляем статы на кнопку
        if stats_parts:
            label += f" ({', '.join(stats_parts)})"
        
        label += f" {price}💰"
        
        # Ограничиваем длину
        if len(label) > 40:
            if stats_parts:
                label = f"{icon} {item_name} ({', '.join(stats_parts[:2])}) {price}💰"
            if len(label) > 40:
                label = label[:37] + "..."
        
        keyboard.add_button(label, color=VkKeyboardColor.PRIMARY,
                           payload={'cmd': 'market2_buy_weapon', 'item_name': item_name, 
                                   'price': price, 'level': shop_level, 'rarity': rarity})
        keyboard.add_line()
    
    keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_market2'})
    
    await send_message(vk, user_id, text, keyboard)
    await update_user_async(user_id, state='market2_weapons', context={'parent_state': 'market2'})


async def show_market2_buy_weapon(vk, user_id, item_name, price, level, rarity):
    """Подтверждение покупки оружия 20+"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    if char['level'] < 20:
        keyboard = VkKeyboard()
        keyboard.add_button('🔙 Назад в магазин', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'market2_weapons'})
        await send_message(vk, user_id, f'❌ Оружие 20+ доступно только с 20 уровня.', keyboard)
        return
    
    if char['silver'] < price:
        keyboard = VkKeyboard()
        keyboard.add_button('🔙 Назад в магазин', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'market2_weapons'})
        await send_message(vk, user_id, f'❌ Недостаточно серебра! Нужно {price}💰.', keyboard)
        return
    
    class_restriction = None
    if item_name in ['Посох', 'Свиток', 'Орб']:
        class_restriction = 'Послушник'
    
    if class_restriction and char['class'] != class_restriction:
        keyboard = VkKeyboard()
        keyboard.add_button('🔙 Назад в магазин', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'market2_weapons'})
        await send_message(vk, user_id, f'❌ Это оружие может использовать только {class_restriction}.', keyboard)
        return
    
    template_id = get_item_template_id_by_name(item_name)
    if not template_id:
        keyboard = VkKeyboard()
        keyboard.add_button('🔙 Назад в магазин', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'market2_weapons'})
        await send_message(vk, user_id, '❌ Ошибка: предмет не найден.', keyboard)
        return
    
    stats = get_item_stats(template_id, level, rarity, upgrade_level=0)
    if not stats:
        keyboard = VkKeyboard()
        keyboard.add_button('🔙 Назад в магазин', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'market2_weapons'})
        await send_message(vk, user_id, '❌ Ошибка получения характеристик.', keyboard)
        return
    
    # Формируем подробное описание
    text = f"🛒 Подтвердите покупку:\n\n"
    text += f"📌 {stats['icon']} {item_name}\n"
    text += f"📊 Уровень: {level}\n"
    text += f"⭐ Редкость: ⚪ Обычный\n\n"
    text += "📈 Характеристики:\n"
    if stats.get('attack', 0) > 0:
        text += f"  ⚔️ Атака: +{stats['attack']}\n"
    if stats.get('defense', 0) > 0:
        text += f"  🛡️ Защита: +{stats['defense']}\n"
    if stats.get('hp', 0) > 0:
        text += f"  ❤️ HP: +{stats['hp']}\n"
    if stats.get('mana', 0) > 0:
        text += f"  💧 Мана: +{stats['mana']}\n"
    if stats.get('bonus_crit', 0) != 0:
        text += f"  💥 Крит: {stats['bonus_crit']:+}%\n"
    if stats.get('bonus_dodge', 0) != 0:
        text += f"  💨 Уворот: {stats['bonus_dodge']:+}%\n"
    text += f"\n💰 Цена: {price} серебра\n"
    text += f"💳 Ваше серебро: {char['silver']}\n"
    
    keyboard = VkKeyboard()
    keyboard.add_button('✅ Купить', color=VkKeyboardColor.POSITIVE,
                       payload={'cmd': 'market2_buy_weapon_confirm', 
                               'item_name': item_name, 'price': price, 
                               'level': level, 'rarity': rarity})
    keyboard.add_button('❌ Отмена', color=VkKeyboardColor.NEGATIVE,
                       payload={'cmd': 'market2_weapons'})
    
    await send_message(vk, user_id, text, keyboard)


async def show_market2_buy_weapon_confirm(vk, user_id, item_name, price, level, rarity):
    """Выполнение покупки оружия"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    if char['silver'] < price:
        await send_message(vk, user_id, f'❌ Недостаточно серебра! Нужно {price}💰.', get_back_keyboard('город2'))
        await show_market2_weapons(vk, user_id)
        return
    
    template_id = get_item_template_id_by_name(item_name)
    if not template_id:
        await send_message(vk, user_id, '❌ Ошибка: предмет не найден.', get_back_keyboard('город2'))
        await show_market2_weapons(vk, user_id)
        return
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE characters SET silver = silver - ? WHERE id = ?', (price, char['id']))
    cur.execute('''
        INSERT INTO player_items (owner_id, template_id, level, rarity, upgrade_level, quantity)
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (char['id'], template_id, level, rarity, 0))
    conn.commit()
    conn.close()
    
    from core import recalc_stats_async
    await recalc_stats_async(char['id'])
    
    keyboard = VkKeyboard()
    keyboard.add_button('🔙 В магазин', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'market2_weapons'})
    await send_message(vk, user_id, f'✅ Вы купили {item_name} ({level} уровень) за {price}💰!', keyboard)


async def show_market2_left_hand(vk, user_id):
    """Показ предметов левой руки с характеристиками на кнопках"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    if char['level'] < 20:
        await send_message(vk, user_id, '❌ Левая рука доступна только с 20 уровня.', get_back_keyboard('город2'))
        return
    
    if not char['class']:
        await send_message(vk, user_id, '❌ Сначала выберите класс в Ратуше.', get_back_keyboard('город2'))
        return
    
    player_level = char['level']
    shop_level = get_shop_item_level20(player_level)
    rarity = 1
    
    left_hand_items = {
        'Оруженосец': ['Щит'],
        'Охотник': ['Кинжал ЛР'],
        'Послушник': ['Книга', 'Орб ЛР'],
    }
    
    class_name = char['class']
    items = left_hand_items.get(class_name, [])
    
    if not items:
        await send_message(vk, user_id, f'❌ Для класса {class_name} нет предметов левой руки.', get_back_keyboard('город2'))
        return
    
    text = f"🛡️ Левая рука (20+ уровень)\n"
    text += f"📌 Ваш класс: {class_name}\n"
    text += f"📊 Уровень предметов: {shop_level}\n"
    text += f"Ваши 💰: {char['silver']}\n\n"
    text += "⚪ Только обычные предметы (белые)\n\n"
    
    keyboard = VkKeyboard()
    
    for item_name in items:
        template_id = get_item_template_id_by_name(item_name)
        if not template_id:
            continue
        
        stats = get_item_stats(template_id, shop_level, rarity, upgrade_level=0)
        if not stats:
            continue
        
        price = get_shop_item_price(shop_level, base_price=150)
        
        stats_parts = []
        if stats.get('attack', 0) > 0:
            stats_parts.append(f"⚔{stats['attack']}")
        if stats.get('defense', 0) > 0:
            stats_parts.append(f"🛡{stats['defense']}")
        if stats.get('hp', 0) > 0:
            stats_parts.append(f"❤️{stats['hp']}")
        if stats.get('mana', 0) > 0:
            stats_parts.append(f"💧{stats['mana']}")
        if stats.get('bonus_crit', 0) != 0:
            stats_parts.append(f"💥{stats['bonus_crit']:+}%")
        if stats.get('bonus_dodge', 0) != 0:
            stats_parts.append(f"💨{stats['bonus_dodge']:+}%")
        
        icon = stats['icon'] if stats else '📦'
        label = f"{icon} {item_name}"
        if stats_parts:
            label += f" ({', '.join(stats_parts)})"
        label += f" {price}💰"
        
        if len(label) > 40:
            if stats_parts:
                label = f"{icon} {item_name} ({', '.join(stats_parts[:2])}) {price}💰"
            if len(label) > 40:
                label = label[:37] + "..."
        
        keyboard.add_button(label, color=VkKeyboardColor.PRIMARY,
                           payload={'cmd': 'market2_buy_left_hand', 'item_name': item_name, 
                                   'price': price, 'level': shop_level, 'rarity': rarity})
        keyboard.add_line()
    
    keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_market2'})
    
    await send_message(vk, user_id, text, keyboard)
    await update_user_async(user_id, state='market2_left_hand', context={'parent_state': 'market2'})


async def show_market2_buy_left_hand(vk, user_id, item_name, price, level, rarity):
    """Покупка предмета левой руки"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    if char['level'] < 20:
        keyboard = VkKeyboard()
        keyboard.add_button('🔙 Назад в магазин', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'market2_left_hand'})
        await send_message(vk, user_id, f'❌ Левая рука доступна только с 20 уровня.', keyboard)
        return
    
    if not char['class']:
        keyboard = VkKeyboard()
        keyboard.add_button('🔙 Назад в магазин', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'market2_left_hand'})
        await send_message(vk, user_id, '❌ Сначала выберите класс в Ратуше.', keyboard)
        return
    
    if char['silver'] < price:
        keyboard = VkKeyboard()
        keyboard.add_button('🔙 Назад в магазин', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'market2_left_hand'})
        await send_message(vk, user_id, f'❌ Недостаточно серебра! Нужно {price}💰.', keyboard)
        return
    
    left_hand_map = {
        'Щит': 'Оруженосец',
        'Кинжал ЛР': 'Охотник',
        'Книга': 'Послушник',
        'Орб ЛР': 'Послушник'
    }
    
    required_class = left_hand_map.get(item_name)
    if required_class and char['class'] != required_class:
        keyboard = VkKeyboard()
        keyboard.add_button('🔙 Назад в магазин', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'market2_left_hand'})
        await send_message(vk, user_id, f'❌ {item_name} может использовать только {required_class}.', keyboard)
        return
    
    template_id = get_item_template_id_by_name(item_name)
    if not template_id:
        keyboard = VkKeyboard()
        keyboard.add_button('🔙 Назад в магазин', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'market2_left_hand'})
        await send_message(vk, user_id, '❌ Ошибка: предмет не найден.', keyboard)
        return
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE characters SET silver = silver - ? WHERE id = ?', (price, char['id']))
    cur.execute('''
        INSERT INTO player_items (owner_id, template_id, level, rarity, upgrade_level, quantity)
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (char['id'], template_id, level, rarity, 0))
    conn.commit()
    conn.close()
    
    from core import recalc_stats_async
    await recalc_stats_async(char['id'])
    
    keyboard = VkKeyboard()
    keyboard.add_button('🔙 В магазин', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'market2_left_hand'})
    await send_message(vk, user_id, f'✅ Вы купили {item_name} ({level} уровень, левая рука) за {price}💰!', keyboard)


async def show_market2_armor(vk, user_id):
    """Показ брони с характеристиками на кнопках"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    player_level = char['level']
    shop_level = get_shop_item_level20(player_level) if player_level >= 20 else max(1, player_level // 2)
    rarity = 1
    
    items = [
        ('Кожаная броня', 'armor'),
        ('Кольчуга', 'armor'),
        ('Кираса', 'armor'),
    ]
    
    text = f"🛡️ Броня\n\n"
    text += f"📊 Уровень предметов: {shop_level}\n"
    text += f"Ваши 💰: {char['silver']}\n\n"
    text += "⚪ Только обычные предметы (белые)\n\n"
    
    keyboard = VkKeyboard()
    
    for item_name, slot in items:
        template_id = get_item_template_id_by_name(item_name)
        if not template_id:
            continue
        
        stats = get_item_stats(template_id, shop_level, rarity, upgrade_level=0)
        if not stats:
            continue
        
        price = get_shop_item_price(shop_level, base_price=200)
        
        stats_parts = []
        if stats.get('attack', 0) > 0:
            stats_parts.append(f"⚔{stats['attack']}")
        if stats.get('defense', 0) > 0:
            stats_parts.append(f"🛡{stats['defense']}")
        if stats.get('hp', 0) > 0:
            stats_parts.append(f"❤️{stats['hp']}")
        if stats.get('mana', 0) > 0:
            stats_parts.append(f"💧{stats['mana']}")
        if stats.get('bonus_crit', 0) != 0:
            stats_parts.append(f"💥{stats['bonus_crit']:+}%")
        if stats.get('bonus_dodge', 0) != 0:
            stats_parts.append(f"💨{stats['bonus_dodge']:+}%")
        
        icon = stats['icon'] if stats else '📦'
        label = f"{icon} {item_name}"
        if stats_parts:
            label += f" ({', '.join(stats_parts)})"
        label += f" {price}💰"
        
        if len(label) > 40:
            if stats_parts:
                label = f"{icon} {item_name} ({', '.join(stats_parts[:2])}) {price}💰"
            if len(label) > 40:
                label = label[:37] + "..."
        
        keyboard.add_button(label, color=VkKeyboardColor.PRIMARY,
                           payload={'cmd': 'market2_buy_armor', 'item_name': item_name, 
                                   'price': price, 'level': shop_level, 'rarity': rarity})
        keyboard.add_line()
    
    keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_market2'})
    
    await send_message(vk, user_id, text, keyboard)
    await update_user_async(user_id, state='market2_armor', context={'parent_state': 'market2'})


async def show_market2_helmets(vk, user_id):
    """Показ шлемов с характеристиками на кнопках"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    player_level = char['level']
    shop_level = get_shop_item_level20(player_level) if player_level >= 20 else max(1, player_level // 2)
    rarity = 1
    
    items = [
        ('Подшлемник', 'head'),
        ('Шлем', 'head'),
        ('Треуголка', 'head'),
    ]
    
    text = f"🎩 Шлемы\n\n"
    text += f"📊 Уровень предметов: {shop_level}\n"
    text += f"Ваши 💰: {char['silver']}\n\n"
    text += "⚪ Только обычные предметы (белые)\n\n"
    
    keyboard = VkKeyboard()
    
    for item_name, slot in items:
        template_id = get_item_template_id_by_name(item_name)
        if not template_id:
            continue
        
        stats = get_item_stats(template_id, shop_level, rarity, upgrade_level=0)
        if not stats:
            continue
        
        price = get_shop_item_price(shop_level, base_price=150)
        
        stats_parts = []
        if stats.get('attack', 0) > 0:
            stats_parts.append(f"⚔{stats['attack']}")
        if stats.get('defense', 0) > 0:
            stats_parts.append(f"🛡{stats['defense']}")
        if stats.get('hp', 0) > 0:
            stats_parts.append(f"❤️{stats['hp']}")
        if stats.get('mana', 0) > 0:
            stats_parts.append(f"💧{stats['mana']}")
        if stats.get('bonus_crit', 0) != 0:
            stats_parts.append(f"💥{stats['bonus_crit']:+}%")
        if stats.get('bonus_dodge', 0) != 0:
            stats_parts.append(f"💨{stats['bonus_dodge']:+}%")
        
        icon = stats['icon'] if stats else '📦'
        label = f"{icon} {item_name}"
        if stats_parts:
            label += f" ({', '.join(stats_parts)})"
        label += f" {price}💰"
        
        if len(label) > 40:
            if stats_parts:
                label = f"{icon} {item_name} ({', '.join(stats_parts[:2])}) {price}💰"
            if len(label) > 40:
                label = label[:37] + "..."
        
        keyboard.add_button(label, color=VkKeyboardColor.PRIMARY,
                           payload={'cmd': 'market2_buy_armor', 'item_name': item_name, 
                                   'price': price, 'level': shop_level, 'rarity': rarity})
        keyboard.add_line()
    
    keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_market2'})
    
    await send_message(vk, user_id, text, keyboard)
    await update_user_async(user_id, state='market2_helmets', context={'parent_state': 'market2'})


async def show_market2_boots(vk, user_id):
    """Показ сапог с характеристиками на кнопках"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    player_level = char['level']
    shop_level = get_shop_item_level20(player_level) if player_level >= 20 else max(1, player_level // 2)
    rarity = 1
    
    items = [
        ('Кожаные сапоги', 'boots'),
        ('Железные сапоги', 'boots'),
        ('Стальные сапоги', 'boots'),
    ]
    
    text = f"👢 Сапоги\n\n"
    text += f"📊 Уровень предметов: {shop_level}\n"
    text += f"Ваши 💰: {char['silver']}\n\n"
    text += "⚪ Только обычные предметы (белые)\n\n"
    
    keyboard = VkKeyboard()
    
    for item_name, slot in items:
        template_id = get_item_template_id_by_name(item_name)
        if not template_id:
            continue
        
        stats = get_item_stats(template_id, shop_level, rarity, upgrade_level=0)
        if not stats:
            continue
        
        price = get_shop_item_price(shop_level, base_price=150)
        
        stats_parts = []
        if stats.get('attack', 0) > 0:
            stats_parts.append(f"⚔{stats['attack']}")
        if stats.get('defense', 0) > 0:
            stats_parts.append(f"🛡{stats['defense']}")
        if stats.get('hp', 0) > 0:
            stats_parts.append(f"❤️{stats['hp']}")
        if stats.get('mana', 0) > 0:
            stats_parts.append(f"💧{stats['mana']}")
        if stats.get('bonus_crit', 0) != 0:
            stats_parts.append(f"💥{stats['bonus_crit']:+}%")
        if stats.get('bonus_dodge', 0) != 0:
            stats_parts.append(f"💨{stats['bonus_dodge']:+}%")
        
        icon = stats['icon'] if stats else '📦'
        label = f"{icon} {item_name}"
        if stats_parts:
            label += f" ({', '.join(stats_parts)})"
        label += f" {price}💰"
        
        if len(label) > 40:
            if stats_parts:
                label = f"{icon} {item_name} ({', '.join(stats_parts[:2])}) {price}💰"
            if len(label) > 40:
                label = label[:37] + "..."
        
        keyboard.add_button(label, color=VkKeyboardColor.PRIMARY,
                           payload={'cmd': 'market2_buy_armor', 'item_name': item_name, 
                                   'price': price, 'level': shop_level, 'rarity': rarity})
        keyboard.add_line()
    
    keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_market2'})
    
    await send_message(vk, user_id, text, keyboard)
    await update_user_async(user_id, state='market2_boots', context={'parent_state': 'market2'})


async def show_market2_crystals(vk, user_id):
    """Показ кристаллов"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    items = [
        ('Голубой кристалл', 15, 200, '🔵'),
        ('Фиолетовый кристалл', 35, 500, '🟣'),
        ('Красный кристалл', 55, 1200, '🔴'),
    ]
    
    text = f"💎 Кристаллы заточки\n\nВаши 💰: {char['silver']}\n\n"
    keyboard = VkKeyboard()
    
    for name, bonus, price, icon in items:
        text += f"{icon} {name} (+{bonus}% к шансу) — {price}💰\n"
        keyboard.add_button(f"{icon} {name}", color=VkKeyboardColor.PRIMARY,
                           payload={'cmd': 'market2_buy_crystal', 'item_name': name, 'price': price})
        keyboard.add_line()
    
    keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_market2'})
    
    await send_message(vk, user_id, text, keyboard)
    await update_user_async(user_id, state='market2_crystals', context={'parent_state': 'market2'})


async def show_market2_buy_armor(vk, user_id, item_name, price, level, rarity):
    """Покупка брони, шлемов, сапог"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    if char['silver'] < price:
        await send_message(vk, user_id, f'❌ Недостаточно серебра! Нужно {price}💰.', get_back_keyboard('город2'))
        await show_market2(vk, user_id)
        return
    
    template_id = get_item_template_id_by_name(item_name)
    if not template_id:
        await send_message(vk, user_id, '❌ Ошибка: предмет не найден.', get_back_keyboard('город2'))
        await show_market2(vk, user_id)
        return
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE characters SET silver = silver - ? WHERE id = ?', (price, char['id']))
    cur.execute('''
        INSERT INTO player_items (owner_id, template_id, level, rarity, upgrade_level, quantity)
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (char['id'], template_id, level, rarity, 0))
    conn.commit()
    conn.close()
    
    from core import recalc_stats_async
    await recalc_stats_async(char['id'])
    
    await send_message(vk, user_id, f'✅ Вы купили {item_name} ({level} уровень) за {price}💰!', get_back_keyboard('город2'))
    await show_market2(vk, user_id)


async def show_market2_buy_crystal(vk, user_id, item_name, price):
    """Покупка кристалла"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    if char['silver'] < price:
        await send_message(vk, user_id, f'❌ Недостаточно серебра! Нужно {price}💰.', get_back_keyboard('город2'))
        return
    
    from core import buy_consumable
    
    crystal_map = {
        'Голубой кристалл': 10,
        'Фиолетовый кристалл': 11,
        'Красный кристалл': 12
    }
    
    template_id = crystal_map.get(item_name)
    if not template_id:
        await send_message(vk, user_id, '❌ Ошибка: кристалл не найден.', get_back_keyboard('город2'))
        return
    
    success, msg = buy_consumable(char['id'], template_id, 1)
    if success:
        await send_message(vk, user_id, f'✅ {msg}', get_back_keyboard('город2'))
    else:
        await send_message(vk, user_id, f'❌ {msg}', get_back_keyboard('город2'))
    
    await show_market2(vk, user_id)