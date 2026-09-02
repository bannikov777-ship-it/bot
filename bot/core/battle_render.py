# core/battle_render.py - с короткими барами

def render_battle(battle, player_name='Вы'):
    """
    Чистая визуализация боя с короткими барами
    """
    monster = battle['monster']
    
    # ===== HP БАР МОНСТРА (короткий) =====
    hp_percent = (monster['hp'] / monster['max_hp']) * 100
    bar_length = 10  # ✅ УМЕНЬШИЛИ С 20 ДО 10
    filled = int((hp_percent / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    hp_text = f"{monster['hp']}/{monster['max_hp']}"
    
    # ===== HP БАР ИГРОКА (короткий) =====
    player_hp_percent = (battle['player_hp'] / battle['player_max_hp']) * 100
    p_filled = int((player_hp_percent / 100) * bar_length)
    p_bar = "█" * p_filled + "░" * (bar_length - p_filled)
    p_hp_text = f"{battle['player_hp']}/{battle['player_max_hp']}"
    
    # ===== МАНА (только для магов) =====
    mana_text = ""
    if battle.get('show_mana', False):
        mana_percent = (battle['player_mana'] / battle['player_max_mana']) * 100
        m_filled = int((mana_percent / 100) * 10)  # ✅ 10 вместо 15
        m_bar = "█" * m_filled + "░" * (10 - m_filled)
        mana_text = f"💧 Мана: [{m_bar}] {battle['player_mana']}/{battle['player_max_mana']}\n"
    
    # ===== ВЫНОСЛИВОСТЬ =====
    stamina_percent = (battle['player_stamina'] / battle['player_max_stamina']) * 100
    s_filled = int((stamina_percent / 100) * 10)  # ✅ 10 вместо 15
    s_bar = "█" * s_filled + "░" * (10 - s_filled)
    
    # ===== СТАТУС ЗАЩИТЫ =====
    if battle.get('shield_active'):
        duration = battle.get('shield_duration', 0)
        if duration > 0:
            shield_status = f"🛡️ ЗАЩИТА АКТИВНА ({duration} ход.)"
        else:
            shield_status = f"🛡️ ЗАЩИТА (последний ход!)"
    else:
        shield_status = f"❌ ЗАЩИТА НЕ АКТИВНА"
    
    # ===== ПАРИРОВАНИЕ =====
    parry_charges = battle.get('parry_charges', 4)
    p_charge_bar = "█" * parry_charges + "░" * (4 - parry_charges)
    if parry_charges >= 4:
        parry_status = f"✅ [{p_charge_bar}] ГОТОВО"
    elif parry_charges == 0:
        parry_status = f"⏳ [{p_charge_bar}] ЗАРЯДКА..."
    else:
        parry_status = f"🔄 [{p_charge_bar}] {parry_charges}/4"
    
    # ===== ХАРАКТЕРИСТИКИ ИГРОКА =====
    player_stats = f"⚔️ {battle['player_attack']}  🛡️ {battle['player_defense']}"
    
    crit = battle.get('crit_chance', 0)
    dodge = battle.get('dodge_chance', 0)
    if crit > 0 or dodge > 0:
        player_stats += f"  💥{crit}%  💨{dodge}%"
    
    # ===== ЛОГ БОЯ =====
    log_lines = battle['log'][-4:] if battle['log'] else ["⚔️ Бой начинается!"]
    formatted_log = []
    for line in log_lines:
        if line.startswith('💥') or line.startswith('💨') or \
           line.startswith('🛡️') or line.startswith('🌀') or \
           line.startswith('✨') or line.startswith('⚔️') or \
           line.startswith('💢') or line.startswith('📌') or \
           line.startswith('🔥') or line.startswith('🏃'):
            formatted_log.append(line)
        else:
            if 'КРИТ' in line or 'крит' in line:
                formatted_log.append(f"💥 {line}")
            elif 'уклонились' in line:
                formatted_log.append(f"💨 {line}")
            elif 'Защита поглотила' in line:
                formatted_log.append(f"🛡️ {line}")
            elif 'Парирование' in line or 'Контратака' in line:
                formatted_log.append(f"🌀 {line}")
            elif 'Исцеление' in line:
                formatted_log.append(f"✨ {line}")
            elif 'Суперудар' in line:
                formatted_log.append(f"🔥 {line}")
            elif 'нанесли' in line:
                formatted_log.append(f"⚔️ {line}")
            elif 'атакует' in line or 'Монстр нанёс' in line:
                formatted_log.append(f"💢 {line}")
            else:
                formatted_log.append(f"📌 {line}")
    
    log_text = "\n".join(formatted_log)
    
    # ===== ЛИНИЯ РАЗДЕЛИТЕЛЯ =====
    divider = "─────────────────"
    
    # ===== СОБИРАЕМ =====
    text = (
        f"⚔️ {monster['name'].upper()}\n"
        f"❤️ HP: [{bar}] {hp_text} ({hp_percent:.0f}%)\n"
        f"⚔️ {monster['attack']}  🛡️ {monster['defense']}\n\n"
        f"{divider}\n\n"
        f"🧑 {player_name.upper()}\n"
        f"❤️ HP: [{p_bar}] {p_hp_text} ({player_hp_percent:.0f}%)\n"
        f"{mana_text}"
        f"⚡ Stamina: [{s_bar}] {battle['player_stamina']}/{battle['player_max_stamina']}\n"
        f"{player_stats}\n"
        f"{shield_status}   |   🌀 {parry_status}\n\n"
        f"{divider}\n\n"
        f"📜 ЛОГ:\n{log_text}"
    )
    
    return text