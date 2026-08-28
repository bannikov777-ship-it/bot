# locations/healer.py (ПОЛНЫЙ ИСПРАВЛЕННЫЙ)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import asyncio
from core import (
    get_character_async, update_user_async, send_message, get_user_async,
    get_consumable_templates, buy_consumable, get_character, DB_NAME
)
from keyboards import get_back_keyboard
from crafting import get_craft_recipes, craft_item
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from .base import navigate_to

async def show_healer(vk, user_id):
    """Показ лекаря"""
    try:
        char = await get_character_async(user_id)
        if not char:
            await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
            return
        
        keyboard = VkKeyboard()
        
        # Первая строка - 2 кнопки
        keyboard.add_button('💊 Купить зелья', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'healer_buy'})
        keyboard.add_button('🌿 Продать травы', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'healer_sell_herbs'})
        keyboard.add_line()
        
        # Вторая строка - крафт
        keyboard.add_button('⚗️ Крафт', color=VkKeyboardColor.PRIMARY, payload={'cmd': 'healer_craft'})
        keyboard.add_line()
        
        # Третья строка - назад в город
        keyboard.add_button('🏪 На рынок', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'go_market'})
        attachment = "photo-240828623_456239162"
        
        await send_message(vk, user_id, f'💊 Лекарь\nВаши 💰: {char["silver"]}\n\nВыберите действие:', keyboard)
        
        user_data = await get_user_async(user_id)
        context = user_data['context']
        context['parent_state'] = 'market'
        await update_user_async(user_id, state='healer', context=context)
    except Exception as e:
        print(f"❌ Ошибка в show_healer: {e}")
        import traceback
        traceback.print_exc()
        await send_message(vk, user_id, f'⚠️ Ошибка: {e}', get_back_keyboard('рынок'))


async def show_healer_buy(vk, user_id):
    """Показ покупки зелий - с реальными ценами из БД"""
    try:
        char = await get_character_async(user_id)
        if not char:
            await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
            return
        
        # ✅ Получаем реальные данные из БД
        all_templates = get_consumable_templates()
        
        # Фильтруем только зелья (HP, MP, Stamina) - исключаем кристаллы и свитки
        consumables = []
        for t in all_templates:
            if t['restore_type'] in ('hp', 'mana', 'stamina'):
                consumables.append(t)
        
        if not consumables:
            await send_message(vk, user_id, 'Нет доступных зелий.', get_back_keyboard('лекаря'))
            return
        
        # Группируем по типу
        hp_consumables = [c for c in consumables if c['restore_type'] == 'hp']
        mana_consumables = [c for c in consumables if c['restore_type'] == 'mana']
        stamina_consumables = [c for c in consumables if c['restore_type'] == 'stamina']
        
        keyboard = VkKeyboard()
        
        # Заголовки столбцов
        keyboard.add_button('❤️ HP', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('💧 MP', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('⚡ STA', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        
        # Строки зелий
        max_rows = max(len(hp_consumables), len(mana_consumables), len(stamina_consumables))
        
        for i in range(max_rows):
            # HP зелье
            if i < len(hp_consumables):
                t = hp_consumables[i]
                # ✅ Используем реальную цену из БД
                price = t['price']
                percent = t['restore_percent']
                label = f"{percent}%"
                keyboard.add_button(
                    label,
                    color=VkKeyboardColor.PRIMARY,
                    payload={'cmd': 'buy_consumable', 'template_id': t['id'], 'price': price}
                )
            else:
                keyboard.add_button('·', color=VkKeyboardColor.SECONDARY)
            
            # MP зелье
            if i < len(mana_consumables):
                t = mana_consumables[i]
                price = t['price']
                percent = t['restore_percent']
                keyboard.add_button(
                    f"{percent}%",
                    color=VkKeyboardColor.PRIMARY,
                    payload={'cmd': 'buy_consumable', 'template_id': t['id'], 'price': price}
                )
            else:
                keyboard.add_button('·', color=VkKeyboardColor.SECONDARY)
            
            # STA зелье
            if i < len(stamina_consumables):
                t = stamina_consumables[i]
                price = t['price']
                percent = t['restore_percent']
                keyboard.add_button(
                    f"{percent}%",
                    color=VkKeyboardColor.PRIMARY,
                    payload={'cmd': 'buy_consumable', 'template_id': t['id'], 'price': price}
                )
            else:
                keyboard.add_button('·', color=VkKeyboardColor.SECONDARY)
            
            keyboard.add_line()
        
        # Кнопка назад
        keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'healer'})
        
        # ✅ Формируем текст с реальными ценами из БД
        text = f"💊 Выберите зелье:\n\n"
        text += f"❤️ HP  💧 MP  ⚡ STA\n"
        
        # Показываем реальные цены
        for i in range(max_rows):
            line = ""
            if i < len(hp_consumables):
                t = hp_consumables[i]
                line += f"{t['restore_percent']}% {t['price']}💰  "
            else:
                line += "        "
            
            if i < len(mana_consumables):
                t = mana_consumables[i]
                line += f"{t['restore_percent']}% {t['price']}💰  "
            else:
                line += "        "
            
            if i < len(stamina_consumables):
                t = stamina_consumables[i]
                line += f"{t['restore_percent']}% {t['price']}💰"
            
            if line.strip():
                text += line + "\n"
        
        text += f"\n💰 Ваше серебро: {char['silver']}"
        
        await send_message(vk, user_id, text, keyboard)
        
        user_data = await get_user_async(user_id)
        context = user_data['context']
        context['parent_state'] = 'healer'
        await update_user_async(user_id, state='healer_buy', context=context)
        
    except Exception as e:
        print(f"❌ Ошибка в show_healer_buy: {e}")
        import traceback
        traceback.print_exc()
        await send_message(vk, user_id, f'⚠️ Ошибка: {e}', get_back_keyboard('лекаря'))


async def show_healer_craft(vk, user_id):
    """Показ крафта"""
    try:
        char = await get_character_async(user_id)
        if not char:
            await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
            return
        
        recipes = get_craft_recipes()
        if not recipes:
            await send_message(vk, user_id, 'Нет доступных рецептов.', get_back_keyboard('лекаря'))
            return
        
        keyboard = VkKeyboard()
        
        hp_recipes = []
        mana_recipes = []
        stamina_recipes = []
        other_recipes = []
        
        for recipe in recipes:
            restore_type = recipe.get('restore_type')
            if restore_type == 'hp':
                hp_recipes.append(recipe)
            elif restore_type == 'mana':
                mana_recipes.append(recipe)
            elif restore_type == 'stamina':
                stamina_recipes.append(recipe)
            else:
                other_recipes.append(recipe)
        
        # Сортируем по проценту восстановления
        hp_recipes.sort(key=lambda x: x.get('restore_percent', 0))
        mana_recipes.sort(key=lambda x: x.get('restore_percent', 0))
        stamina_recipes.sort(key=lambda x: x.get('restore_percent', 0))
        
        # Заголовки
        keyboard.add_button('❤️ HP', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('💧 MP', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('⚡ STA', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        
        # Выводим рецепты в 3 столбика
        max_rows = max(len(hp_recipes), len(mana_recipes), len(stamina_recipes))
        
        for i in range(max_rows):
            # HP рецепт
            if i < len(hp_recipes):
                recipe = hp_recipes[i]
                percent = recipe.get('restore_percent', 0)
                keyboard.add_button(
                    f"{percent}%",
                    color=VkKeyboardColor.PRIMARY,
                    payload={'cmd': 'healer_craft_do', 'recipe_id': recipe['id']}
                )
            else:
                keyboard.add_button('·', color=VkKeyboardColor.SECONDARY)
            
            # MP рецепт
            if i < len(mana_recipes):
                recipe = mana_recipes[i]
                percent = recipe.get('restore_percent', 0)
                keyboard.add_button(
                    f"{percent}%",
                    color=VkKeyboardColor.PRIMARY,
                    payload={'cmd': 'healer_craft_do', 'recipe_id': recipe['id']}
                )
            else:
                keyboard.add_button('·', color=VkKeyboardColor.SECONDARY)
            
            # STA рецепт
            if i < len(stamina_recipes):
                recipe = stamina_recipes[i]
                percent = recipe.get('restore_percent', 0)
                keyboard.add_button(
                    f"{percent}%",
                    color=VkKeyboardColor.PRIMARY,
                    payload={'cmd': 'healer_craft_do', 'recipe_id': recipe['id']}
                )
            else:
                keyboard.add_button('·', color=VkKeyboardColor.SECONDARY)
            
            keyboard.add_line()
        
        # Другие рецепты (если есть)
        if other_recipes:
            for recipe in other_recipes:
                name = recipe.get('result_name', 'Зелье')
                keyboard.add_button(
                    name,
                    color=VkKeyboardColor.PRIMARY,
                    payload={'cmd': 'healer_craft_do', 'recipe_id': recipe['id']}
                )
                keyboard.add_line()
        
        # Кнопка назад
        keyboard.add_button('🔙 Назад', color=VkKeyboardColor.SECONDARY, payload={'cmd': 'healer'})
        
        # Формируем текст с рецептами
        text = "⚗️ Доступные рецепты:\n\n"
        for recipe in recipes:
            icon = recipe.get('result_icon', '🧪')
            name = recipe.get('result_name', 'Зелье')
            percent = recipe.get('restore_percent', 0)
            ingredients = recipe.get('ingredients', [])
            ingredients_text = ", ".join([f"{ing.get('icon', '')} {ing.get('name', '')} x{ing.get('quantity', 1)}" for ing in ingredients])
            text += f"{icon} {name} ({percent}%): {ingredients_text}\n"
        text += f"\n💰 {char['silver']}"
        
        await send_message(vk, user_id, text, keyboard)
        
        user_data = await get_user_async(user_id)
        context = user_data['context']
        context['parent_state'] = 'healer'
        await update_user_async(user_id, state='healer_craft', context=context)
        
    except Exception as e:
        print(f"❌ Ошибка в show_healer_craft: {e}")
        import traceback
        traceback.print_exc()
        await send_message(vk, user_id, f'⚠️ Ошибка: {e}', get_back_keyboard('лекаря'))


async def show_healer_sell_herbs(vk, user_id):
    """Продажа трав"""
    try:
        char = await get_character_async(user_id)
        if not char:
            await send_message(vk, user_id, 'Сначала создайте персонажа.', get_back_keyboard('город'))
            return
        from core import sell_all_herbs
        total, msg = sell_all_herbs(char['id'])
        await send_message(vk, user_id, msg, get_back_keyboard('лекаря'))
        await show_healer(vk, user_id)
    except Exception as e:
        print(f"❌ Ошибка в show_healer_sell_herbs: {e}")
        await send_message(vk, user_id, f'⚠️ Ошибка: {e}', get_back_keyboard('лекаря'))