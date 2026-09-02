# locations/auction2.py - Аукцион Озерного Края

from core import get_character_async, update_user_async, send_message, get_user_async, get_player_consumables
from auction import get_active_auction_lots, expire_and_return_expired, buy_auction_lot, get_lot_by_id, create_auction_lot
from keyboards import get_back_keyboard
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from items import get_player_items
import asyncio


async def show_auction2(vk, user_id, page=0):
    """Показ аукциона Озерного Края"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context['parent_state'] = 'city2'
    await update_user_async(user_id, context=context)
    
    await asyncio.to_thread(expire_and_return_expired)
    lots = await asyncio.to_thread(get_active_auction_lots, 10, page * 10)
    
    if not lots:
        await send_message(vk, user_id, '📭 На аукционе пока нет лотов.', get_auction2_keyboard())
        return
    
    text = f"🏛️ Аукцион Озерного Края\n\n"
    
    for i, lot in enumerate(lots, start=1 + page * 10):
        if lot['item_type'] == 'item':
            stats = f"+{lot['attack']} атк, +{lot['defense']} защ, +{lot['hp']} HP"
        else:
            stats = f"Восстанавливает {lot['restore_percent']}% {lot['restore_type']}"
        
        seller = "Гильдия" if lot['seller_type'] == 'guild' else "Игрок"
        text += f"{i}. (ID:{lot['id']}) {lot['icon']} {lot['name']} x{lot['quantity']} ({stats}) цена: {lot['price']}💰 (продавец: {seller})\n"
    
    keyboard = get_auction2_keyboard(page)
    await send_message(vk, user_id, text, keyboard)
    
    context['auction2_page'] = page
    await update_user_async(user_id, state='auction2', context=context)


def get_auction2_keyboard(page=0):
    keyboard = VkKeyboard()
    keyboard.add_button('🛒 Купить по ID', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'auction2_buy_prompt'})
    keyboard.add_line()
    keyboard.add_button('🔄 Обновить', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'auction2_refresh'})
    keyboard.add_button('📤 Выставить', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'auction2_sell'})
    keyboard.add_line()
    keyboard.add_button('🏙️ В Озерный Край', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_city2'})
    return keyboard


async def show_auction2_buy_prompt(vk, user_id):
    """Запрос ID лота для покупки"""
    await send_message(vk, user_id, '📝 Введите ID лота, который хотите купить (только число):')
    await update_user_async(user_id, state='awaiting_auction2_buy_id', context={'parent_state': 'auction2'})


async def show_auction2_buy_confirm(vk, user_id, lot_id):
    """Подтверждение покупки лота"""
    lot = await asyncio.to_thread(get_lot_by_id, lot_id)
    if not lot:
        await send_message(vk, user_id, '❌ Лот не найден или уже неактивен.', get_auction2_keyboard())
        return
    
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    if char['silver'] < lot['price']:
        await send_message(vk, user_id, f'❌ Недостаточно серебра! Нужно {lot["price"]}💰.', get_auction2_keyboard())
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context['auction2_buy_lot_id'] = lot_id
    await update_user_async(user_id, context=context)
    
    keyboard = VkKeyboard()
    keyboard.add_button('✅ Да, купить', color=VkKeyboardColor.POSITIVE, payload={'cmd': 'auction2_confirm_yes'})
    keyboard.add_button('❌ Нет, отмена', color=VkKeyboardColor.NEGATIVE, payload={'cmd': 'auction2_confirm_no'})
    keyboard.add_line()
    keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_auction2'})
    
    await send_message(vk, user_id, 
        f"🛒 Подтвердите покупку:\n\nЛот ID: {lot_id}\nЦена: {lot['price']}💰\nВаши деньги: {char['silver']}💰\n\nВы уверены?", keyboard)


async def show_auction2_sell_menu(vk, user_id):
    """Меню продажи на аукционе"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    keyboard = VkKeyboard()
    keyboard.add_button('🗡️ Предметы', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'auction2_sell_items'})
    keyboard.add_button('🧪 Расходники', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'auction2_sell_consumables'})
    keyboard.add_line()
    keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_auction2'})
    
    await send_message(vk, user_id, '📤 Что хотите выставить на аукцион?', keyboard)
    await update_user_async(user_id, state='auction2_sell', context={'parent_state': 'auction2'})


async def show_auction2_sell_select_items(vk, user_id, item_type='item'):
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    if item_type == 'item':
        items = get_player_items(char['id'])
        if not items:
            await send_message(vk, user_id, 'У вас нет предметов для продажи.', get_back_keyboard('город2'))
            return
    else:
        items = get_player_consumables(char['id'])
        if not items:
            await send_message(vk, user_id, 'У вас нет расходников для продажи.', get_back_keyboard('город2'))
            return
    
    keyboard = VkKeyboard()
    for item in items:
        # ✅ Для расходников используется item['id'] из player_consumables
        label = f"{item['icon']} {item['name']} (x{item['quantity']})"
        keyboard.add_button(label, color=VkKeyboardColor.PRIMARY,
                           payload={'cmd': 'auction2_sell_select_item', 'item_id': item['id'], 'item_type': item_type})
        keyboard.add_line()
    
    keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'auction2_sell'})
    
    await send_message(vk, user_id, 'Выберите предмет для продажи:', keyboard)


async def show_auction2_sell_price(vk, user_id, item_type, item_id):
    """Ввод цены для продажи"""
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context['auction2_item_type'] = item_type
    context['auction2_item_id'] = item_id
    await update_user_async(user_id, context=context)
    
    await send_message(vk, user_id, 'Введите цену в серебре (целое число):')
    await update_user_async(user_id, state='awaiting_auction2_price', context=context)


async def show_auction2_sell_execute(vk, user_id, price):
    """Выполнение продажи"""
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    item_type = context.get('auction2_item_type')
    item_id = context.get('auction2_item_id')
    
    if not item_type or not item_id:
        await send_message(vk, user_id, 'Ошибка: предмет не выбран.', get_back_keyboard('город2'))
        return
    
    from auction import create_auction_lot
    lot_id, msg = create_auction_lot('player', char['id'], item_type, item_id, 1, price)
    
    if lot_id:
        await send_message(vk, user_id, f'✅ {msg}', get_back_keyboard('город2'))
    else:
        await send_message(vk, user_id, f'❌ {msg}', get_back_keyboard('город2'))
    
    await show_auction2(vk, user_id)