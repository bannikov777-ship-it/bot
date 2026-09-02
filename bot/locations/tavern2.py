# locations/tavern2.py - Приозерная таверна (ПОЛНЫЙ ИСПРАВЛЕННЫЙ)

from core import get_character_async, update_user_async, send_message, get_user_async
from keyboards import get_back_keyboard
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from scheduler import scheduler
import time
import sqlite3
from config import DB_NAME

TAVERN2_IMAGE = 'photo-240828623_456239032'


def get_tavern2_keyboard():
    keyboard = VkKeyboard()
    keyboard.add_button('🍽️ Поесть', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'tavern2_food'})
    keyboard.add_button('😴 Снять комнату', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'tavern2_room'})
    keyboard.add_line()
    keyboard.add_button('🗣️ Слухи', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'tavern2_rumors'})
    return keyboard


def get_food2_keyboard():
    keyboard = VkKeyboard()
    food_items = [
        ('🐟 Рыба дня (+15% HP)', 15, 15),
        ('🥣 Уха (+30% HP)', 30, 40),
        ('🦐 Королевские креветки (+50% HP)', 50, 80),
        ('🍲 Уха царская (+80% HP)', 80, 150),
        ('🦞 Омары (+100% HP)', 100, 200),
    ]
    
    # ✅ По 1 кнопке в строке (чтобы не было ошибки)
    for name, percent, price in food_items:
        keyboard.add_button(
            f'{name} ({price}💰)',
            color=VkKeyboardColor.PRIMARY,
            payload={'cmd': 'buy_food2', 'percent': percent, 'price': price}
        )
        keyboard.add_line()
    
    # ✅ КНОПКА В ТАВЕРНУ
    keyboard.add_button('🍺 В таверну', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_tavern2'})
    
    return keyboard


def get_sleep2_keyboard():
    keyboard = VkKeyboard()
    rooms = [
        ('🛏️ 1 час (+25% HP)', 1, 25),
        ('🛏️ 2 часа (+60% HP)', 2, 60),
        ('🛏️ 3 часа (+100% HP)', 3, 100),
    ]
    
    # ✅ По 1 кнопке в строке
    for name, hours, percent in rooms:
        keyboard.add_button(
            f'{name} (бесплатно)',
            color=VkKeyboardColor.PRIMARY,
            payload={'cmd': 'sleep2', 'hours': hours, 'percent': percent, 'price': 0}
        )
        keyboard.add_line()
    
    # ✅ КНОПКА В ТАВЕРНУ
    keyboard.add_button('🍺 В таверну', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_tavern2'})
    
    return keyboard


def get_sleep2_status_keyboard():
    keyboard = VkKeyboard()
    keyboard.add_button('🔄 Проверить', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'sleep2_check'})
    keyboard.add_button('❌ Проснуться', color=VkKeyboardColor.NEGATIVE, payload={'cmd': 'sleep2_cancel'})
    return keyboard


async def show_tavern2(vk, user_id):
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context['parent_state'] = 'city2'
    await update_user_async(user_id, context=context)
    
    text = f"🍺 Приозерная таверна «У Озера»\n\n🏞️ Вид на озеро открывается из каждого окна.\nВаши 💰: {char['silver']}\nВаше ❤️: {char['hp']}/{char['max_hp']}\n\nЧто желаешь?"
    
    keyboard = get_tavern2_keyboard()
    keyboard.add_line()
    keyboard.add_button('🏙️ В Озерный Край', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_city2'})
    
    await send_message(vk, user_id, text, keyboard, attachment=TAVERN2_IMAGE)
    await update_user_async(user_id, state='tavern2', context=context)


async def show_tavern2_food(vk, user_id):
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    text = f"🍖 Меню приозерной таверны:\n\nВаши 💰: {char['silver']}\nВаше ❤️: {char['hp']}/{char['max_hp']}"
    
    keyboard = get_food2_keyboard()  # ✅ УЖЕ ЕСТЬ КНОПКА "В ТАВЕРНУ"
    
    await send_message(vk, user_id, text, keyboard)
    await update_user_async(user_id, state='tavern2_food', context={'parent_state': 'tavern2'})


async def show_tavern2_room(vk, user_id):
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    text = f"🛏 Номера с видом на озеро:\n\n💤 Восстановление бесплатно!\n🌅 Утром вас ждёт великолепный рассвет."
    
    keyboard = get_sleep2_keyboard()  # ✅ УЖЕ ЕСТЬ КНОПКА "В ТАВЕРНУ"
    
    await send_message(vk, user_id, text, keyboard)
    await update_user_async(user_id, state='tavern2_room', context={'parent_state': 'tavern2'})


async def show_tavern2_rumors(vk, user_id):
    await send_message(vk, user_id, 
        "🗣️ Слухи Озерного Края:\n\n"
        "🌊 Говорят, в глубине озера обитает древнее чудовище.\n"
        "🎣 Рыбаки видели странные огни над водой по ночам.\n"
        "⚔️ На Арене появился новый чемпион, никто не может его победить.\n"
        "💎 Кто-то нашёл клад на дне озера, но не смог его поднять.\n"
        "🦞 В этом сезоне особенно много омаров!",
        get_back_keyboard('город2'))
    await update_user_async(user_id, state='tavern2_rumors', context={'parent_state': 'city2'})


async def buy_food2(vk, user_id, percent, price):
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    if char['silver'] < price:
        await send_message(vk, user_id, f'❌ Недостаточно серебра! Нужно {price}💰.', get_back_keyboard('город2'))
        return
    
    max_hp = char['max_hp']
    restore = int(max_hp * percent / 100)
    new_hp = min(max_hp, char['hp'] + restore)
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE characters SET silver = silver - ?, hp = ? WHERE id = ?', (price, new_hp, char['id']))
    conn.commit()
    conn.close()
    
    await send_message(vk, user_id, f'✅ Вы отведали блюдо и восстановили {restore} HP (теперь {new_hp}/{max_hp}).', get_back_keyboard('город2'))
    await show_tavern2(vk, user_id)


async def sleep2(vk, user_id, hours, percent):
    char = await get_character_async(user_id)
    if not char:
        await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город2'))
        return
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    
    if 'sleep2_task_id' in context:
        scheduler.cancel(context['sleep2_task_id'])
    
    # ✅ Используем статусную клавиатуру (без "В таверну")
    keyboard = get_sleep2_status_keyboard()
    
    await send_message(vk, user_id,
        f'😴 Вы легли спать на {hours} час(а). Восстановится {percent}% HP, {percent}% MP и {percent}% Stamina.\n'
        f'🌅 Просыпайтесь с видом на озеро!\n\n'
        f'Вы можете выйти из комнаты, чтобы отменить сон.',
        keyboard
    )
    
    task_id = scheduler.schedule(hours * 3600, restore_after_sleep2, vk, user_id, percent)
    context['sleep2_task_id'] = task_id
    context['sleep2_end_time'] = time.time() + hours * 3600
    await update_user_async(user_id, state='tavern2_room', context=context)


async def sleep2_check(vk, user_id):
    user_data = await get_user_async(user_id)
    context = user_data['context']
    sleep_end_time = context.get('sleep2_end_time')
    
    if not sleep_end_time:
        await send_message(vk, user_id, 'Вы сейчас не спите.', get_back_keyboard('город2'))
        return
    
    remaining = max(0, sleep_end_time - time.time())
    hours = int(remaining // 3600)
    minutes = int((remaining % 3600) // 60)
    seconds = int(remaining % 60)
    
    await send_message(vk, user_id, f'⏳ До пробуждения осталось: {hours}ч {minutes}м {seconds}с', get_sleep2_status_keyboard())


async def sleep2_cancel(vk, user_id):
    user_data = await get_user_async(user_id)
    context = user_data['context']
    
    if 'sleep2_task_id' in context:
        scheduler.cancel(context['sleep2_task_id'])
        del context['sleep2_task_id']
        del context['sleep2_end_time']
        await update_user_async(user_id, context=context)
        await send_message(vk, user_id, '❌ Вы проснулись! Восстановление отменено.', get_back_keyboard('город2'))
    else:
        await send_message(vk, user_id, 'Вы и так не спите.', get_back_keyboard('город2'))
    
    await show_tavern2(vk, user_id)


async def restore_after_sleep2(vk, user_id, percent):
    char = await get_character_async(user_id)
    if not char:
        return
    
    max_hp = char['max_hp']
    max_mana = char['max_mana']
    max_stamina = char['max_stamina']
    
    restore_hp = int(max_hp * percent / 100)
    restore_mana = int(max_mana * percent / 100)
    restore_stamina = int(max_stamina * percent / 100)
    
    new_hp = min(max_hp, char['hp'] + restore_hp)
    new_mana = min(max_mana, char['mana'] + restore_mana)
    new_stamina = min(max_stamina, char['stamina'] + restore_stamina)
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE characters SET hp = ?, mana = ?, stamina = ? WHERE id = ?', 
                (new_hp, new_mana, new_stamina, char['id']))
    conn.commit()
    conn.close()
    
    user_data = await get_user_async(user_id)
    context = user_data['context']
    context.pop('sleep2_task_id', None)
    context.pop('sleep2_end_time', None)
    await update_user_async(user_id, context=context)
    
    await send_message(vk, user_id,
        f'😴 Просыпайтесь с видом на озеро! Вы восстановили:\n❤️ {restore_hp} HP\n💧 {restore_mana} MP\n⚡ {restore_stamina} Stamina',
        get_back_keyboard('город2'))
    await show_tavern2(vk, user_id)