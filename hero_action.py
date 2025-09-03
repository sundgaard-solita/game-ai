from hero import Hero
from hero_archetypes import get_hero_class_name
from hero_state import clamp_resources, init_flags
import random
from app_logger import logger

def apply_damage(target:Hero, damage):
        # Dodging chance to avoid damage
        if target.features.get('is_dodging', False):
            if random.random() < 0.5:
                logger.debug(f"💨 {target.class_name} dodged the attack!")
                target.features['is_dodging'] = False  # dodge used up
                return
            else:
                logger.debug(f"💥 {target.class_name} failed to dodge.")
            target.features['is_dodging'] = False

        # Blocking halves damage
        if target.features.get('is_blocking', False):
            damage = damage // 2
            logger.debug(f"🛡️ {target.class_name} blocks and reduces damage to {damage}.")
            target.features['is_blocking'] = False  # block used up

        target.features['rem_hp'] -= damage
        logger.debug(f"💥 {target.class_name} takes {damage} damage!")

def update_hero_after_action(hero:Hero, action, opponent:Hero):
    init_flags(hero)

    action_funcs = {
        'melee_attack': perform_melee_attack,
        'magic_missile': perform_magic_missile,
        'heal': perform_heal,
        'block': perform_block,
        'dodge': perform_dodge,
        'wand': perform_wand,
        'fire_bow': perform_fire_bow,
        'rest': perform_rest,
        'cast_protection_1': perform_cast_protection_1,
    }

    if action in action_funcs:
        action_funcs[action](hero, opponent)
    else:
        logger.debug(f"❓ {get_hero_class_name(hero)} does nothing.")

    clamp_resources(hero)
    clamp_resources(opponent)

def perform_melee_attack(hero:Hero, opponent:Hero):
    cost = 15
    if hero.features['rem_sta'] >= cost:
        damage = max(0, hero.features['str'] // 6)
        apply_damage(opponent, damage)
        hero.features['rem_sta'] -= cost
        logger.debug(f"💥 {hero.class_name} hits for {damage} melee damage!")
    else:
        logger.debug("🪫 Not enough stamina to melee attack.")

def perform_magic_missile(hero:Hero, opponent:Hero):
    cost = 20
    if hero.features['rem_mana'] >= cost:
        damage = max(0, hero.features['int'] // 4 + 10)
        hero.features['rem_mana'] -= cost
        apply_damage(opponent, damage)
        logger.debug(f"✨ {hero.class_name} casts magic missile for {damage} damage!")
    else:
        logger.debug("⚡ Not enough mana for magic missile!")

def perform_heal(hero:Hero, opponent:Hero):
    cost = 15
    if hero.features['rem_mana'] >= cost:
        heal_amount = hero.features['wis'] // 2
        hero.features['rem_hp'] = min(hero.features['hp'], hero.features['rem_hp'] + heal_amount)
        hero.features['rem_mana'] -= cost
        logger.debug(f"💖 {hero.class_name} heals for {heal_amount} HP!")
    else:
        logger.debug("⚡ Not enough mana to heal!")

def perform_block(hero:Hero, opponent:Hero):
    cost = 10
    if(hero.features['rem_sta']>cost):
        hero.features['is_blocking'] = True
        hero.features['rem_sta'] = max(0, hero.features['rem_sta'] - cost)
        logger.debug(f"🛡️ {hero.class_name} is blocking this turn.")
    else:
        logger.debug("🪫 Not enough stamina to block!")

def perform_dodge(hero:Hero, opponent:Hero):
    cost = 8
    if(hero.features['rem_sta']>cost):
        hero.features['is_dodging'] = True
        hero.features['rem_sta'] = max(0, hero.features['rem_sta'] - cost)
        logger.debug(f"💨 {hero.class_name} tries to dodge the next attack.")
    else:
        logger.debug("🪫 Not enough stamina to dodge!")

def perform_wand(hero:Hero, opponent:Hero):
    cost = 8
    if hero.features['rem_mana'] >= cost:
        damage = hero.features['int'] // 6 + 5
        hero.features['rem_mana'] -= cost
        apply_damage(opponent, damage)
        logger.debug(f"🔮 {hero.class_name} attacks with wand for {damage} damage!")
    else:
        logger.debug("⚡ Not enough mana for wand attack!")

def perform_fire_bow(hero:Hero, opponent:Hero):
    cost = 12
    if hero.features['rem_mana'] >= cost:
        damage = hero.features['agi'] // 4
        hero.features['rem_mana'] -= cost
        logger.debug(f"🔥 {hero.class_name} shoots fire bow for {damage} damage!")
        apply_damage(opponent, damage)
    else:
        logger.debug("⚡ Not enough mana for fire bow!")

def perform_rest(hero:Hero, opponent:Hero):
    """Restore a bit of stamina and mana."""    
    rem_sta_before = hero.features['rem_sta']
    rem_hp_before = hero.features['rem_hp']
    rem_mana_before = hero.features['rem_mana']
    hero.features['rem_sta'] = min(hero.features['rem_sta'] + int(hero.features['sta'] * 0.2), hero.features['sta'])
    hero.features['rem_hp'] = min(hero.features['rem_hp'] + int(hero.features['hp'] * 0.2), hero.features['hp'])
    hero.features['rem_mana'] = min(hero.features['rem_mana'] + int(hero.features['mana'] * 0.1), hero.features['mana'])
    logger.debug(f"🪫 Regained {hero.features['rem_sta']-rem_sta_before} stamina, {hero.features['rem_hp']-rem_hp_before} hp and {hero.features['rem_mana']-rem_mana_before} mana!")
    

def perform_cast_protection_1(hero:Hero, opponent:Hero):
    """Apply a temporary protection buff (dummy logic)."""
    # You can expand this as needed for actual buff tracking
    if hero.features['rem_mana'] >= 5:
        hero.features['rem_mana'] -= 5
        hero.buffs['protection'] = 2  # Lasts 2 rounds, reduce incoming damage maybe?
    else:
        logger.debug(f"⚡ Not enough mana to cast protection!")
