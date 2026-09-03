# admin.py (исправленный)

import sqlite3
from codes import create_code, get_codes_list, get_codes_stats
from core import send_message, get_character_async
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import DB_NAME

# Список администраторов (ID VK)
ADMIN_IDS = [31979968]


async def is_admin(user_id):
    """Проверка, является ли пользователь администратором"""
    return user_id in ADMIN_IDS


async def admin_create_code(vk, user_id, amount=100, days=30, max_uses=1, description="", reward_type="crystals"):
    """Создание промокода администратором"""
    if not await is_admin(user_id):
        await send_message(vk, user_id, '❌ Доступ запрещён. Только для администраторов.')
        return
    
    # ✅ ПЕРЕДАЁМ reward_type В create_code
    code = create_code(
        amount=amount,
        expires_days=days,
        max_uses=max_uses,
        description=description or f"{amount} {'💎 кристаллов' if reward_type == 'crystals' else '💰 серебра'}",
        reward_type=reward_type  # ✅ ДОБАВЛЕНО
    )
    
    reward_icon = '💎 кристаллов' if reward_type == 'crystals' else '💰 серебра'
    
    keyboard = VkKeyboard()
    keyboard.add_button('📋 Скопировать код', color=VkKeyboardColor.PRIMARY,
                       payload={'cmd': 'copy_code', 'code': code})
    keyboard.add_line()
    keyboard.add_button('🏙️ В город', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_city'})
    
    text = (
        f"✅ Создан новый промокод!\n\n"
        f"📌 Код: `{code}`\n"
        f"🎁 Награда: {amount} {reward_icon}\n"
        f"⏳ Действует: {days} дней\n"
        f"🔄 Использований: {max_uses}\n"
        f"📝 Описание: {description or 'Нет'}\n\n"
        f"📋 Нажмите кнопку ниже, чтобы скопировать код."
    )
    
    await send_message(vk, user_id, text, keyboard)


async def admin_show_codes(vk, user_id):
    """Показать список всех промокодов"""
    if not await is_admin(user_id):
        await send_message(vk, user_id, '❌ Доступ запрещён. Только для администраторов.')
        return
    
    codes = get_codes_list(limit=20)
    stats = get_codes_stats()
    
    if not codes:
        await send_message(vk, user_id, '📭 Нет созданных промокодов.')
        return
    
    text = f"📊 Статистика промокодов:\n"
    text += f"📌 Всего: {stats['total']}\n"
    text += f"🎁 Всего награждено: {stats['total_amount']}\n"
    text += f"🔄 Всего использований: {stats['total_uses']}\n\n"
    text += "📋 Список промокодов:\n\n"
    
    for code in codes:
        status = "✅ Активен" if code['is_active'] else "❌ Неактивен"
        reward_icon = '💎' if code.get('reward_type', 'crystals') == 'crystals' else '💰'
        text += f"📌 {code['code']}\n"
        text += f"   {reward_icon} {code['amount']} | Использовано: {code['used_count']}/{code['max_uses']}\n"
        text += f"   ⏳ До: {code['expires_at'][:10] if code['expires_at'] else '∞'}\n"
        text += f"   📝 {code['description'] or 'Нет описания'}\n"
        text += f"   📊 {status}\n\n"
    
    keyboard = VkKeyboard()
    keyboard.add_button('🔄 Обновить', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'admin_codes_refresh'})
    keyboard.add_line()
    keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'back'})
    
    await send_message(vk, user_id, text, keyboard)


async def admin_codes_menu(vk, user_id):
    """Меню управления промокодами"""
    if not await is_admin(user_id):
        await send_message(vk, user_id, '❌ Доступ запрещён. Только для администраторов.')
        return
    
    keyboard = VkKeyboard()
    
    keyboard.add_button('💎 Код на 100 кристаллов', color=VkKeyboardColor.PRIMARY, 
                       payload={'cmd': 'admin_code_create', 'amount': 100, 'type': 'crystals'})
    keyboard.add_button('💎 Код на 500 кристаллов', color=VkKeyboardColor.PRIMARY, 
                       payload={'cmd': 'admin_code_create', 'amount': 500, 'type': 'crystals'})
    keyboard.add_line()
    keyboard.add_button('💰 Код на 10000 серебра', color=VkKeyboardColor.PRIMARY, 
                       payload={'cmd': 'admin_code_create', 'amount': 10000, 'type': 'silver'})
    keyboard.add_button('💰 Код на 50000 серебра', color=VkKeyboardColor.PRIMARY, 
                       payload={'cmd': 'admin_code_create', 'amount': 50000, 'type': 'silver'})
    keyboard.add_line()
    keyboard.add_button('📋 Список кодов', color=VkKeyboardColor.SECONDARY, 
                       payload={'cmd': 'admin_codes_list'})
    keyboard.add_line()
    keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'back'})
    
    await send_message(vk, user_id, 
        '🛠️ Управление промокодами\n\n'
        '📌 Одноразовые коды — можно использовать 1 раз\n'
        '📌 Постоянный код OpenGame — 100 💎 + 2000 💰 (1 раз на аккаунт)\n\n'
        '🎁 Код для новичков:\n'
        '• OpenGame → 100 💎 кристаллов + 2000 💰 серебра',
        keyboard)

async def admin_levelup(vk, user_id, target_id=None, levels=1):
    """Повышение уровня персонажа (админская команда)"""
    from core import get_character_async, recalc_stats_async, DB_NAME
    import sqlite3
    
    if not await is_admin(user_id):
        await send_message(vk, user_id, '❌ Только для администраторов!')
        return
    
    # Если target_id не указан — повышаем своего персонажа
    if target_id is None:
        target_id = user_id
    
    char = await get_character_async(target_id)
    if not char:
        await send_message(vk, user_id, '❌ Персонаж не найден.')
        return
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    new_level = char['level'] + levels
    new_exp = char['exp']
    
    from utils import exp_to_next_level
    for i in range(levels):
        current_level = char['level'] + i
        needed = exp_to_next_level(current_level)
        new_exp += needed
    
    cur.execute('''
        UPDATE characters 
        SET level = ?, exp = ?
        WHERE id = ?
    ''', (new_level, new_exp, char['id']))
    conn.commit()
    conn.close()
    
    await recalc_stats_async(char['id'])
    
    char = await get_character_async(target_id)
    
    await send_message(vk, user_id, 
        f'✅ Уровень персонажа {char["name"]} повышен на {levels}!\n\n'
        f'📊 Текущий уровень: {char["level"]}\n'
        f'❤️ HP: {char["hp"]}/{char["max_hp"]}\n'
        f'⚔️ Атака: {char["attack"]}\n'
        f'🛡️ Защита: {char["defense"]}\n'
        f'💥 Крит: {char["crit_chance"]}%\n'
        f'💨 Уворот: {char["dodge_chance"]}%'
    )

    # admin.py - добавить команду

async def admin_reset_guild_weekly(vk, user_id):
    """Административная команда для сброса еженедельного опыта гильдии"""
    if not await is_admin(user_id):
        await send_message(vk, user_id, '❌ Доступ запрещён. Только для администраторов.')
        return
    
    reset_guild_weekly_exp()
    
    await send_message(vk, user_id, '🔄 Еженедельный опыт гильдии сброшен!')