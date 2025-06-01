from hero_state import clamp_resources, init_flags
from mod_globals import ACTIONS
import random

def select_action(hero, opponent_hp):
    weights = {a: 5 for a in ACTIONS}

    if opponent_hp < hero.max_hp:
        weights['melee_attack'] += 10
        weights['magic_missile'] += 10

    if hero.hp_ratio < 0.3:
        weights['block'] += 50
        if hero.wis > 60:
            weights['heal'] += 40
    else:
        if hero.str_ > 70 and hero.sta_ratio > 0.3:
            weights['melee_attack'] += 40
            weights['block'] += 10
        if hero.int_ > 70 and hero.mana_ratio > 0.5:
            weights['magic_missile'] += 40
            weights['wand'] += 30
        if (hero.agi > 70 or hero.dex > 70) and hero.sta_ratio > 0.2:
            weights['dodge'] += 40
            weights['fire_bow'] += 30

    total = sum(weights.values())
    rnd = random.random() * total
    cumulative = 0
    for action, weight in weights.items():
        cumulative += weight
        if rnd <= cumulative:
            return action

def apply_damage(target, damage):
        # Dodging chance to avoid damage
        if target.get('is_dodging', False):
            if random.random() < 0.5:
                print(f"💨 {target['class']} dodged the attack!")
                target['is_dodging'] = False  # dodge used up
                return
            else:
                print(f"💥 {target['class']} failed to dodge.")
            target['is_dodging'] = False

        # Blocking halves damage
        if target.get('is_blocking', False):
            damage = damage // 2
            print(f"🛡️ {target['class']} blocks and reduces damage to {damage}.")
            target['is_blocking'] = False  # block used up

        target['cur_hp'] -= damage
        print(f"💥 {target['class']} takes {damage} damage!")


def update_hero_after_action(hero, action, opponent):
    init_flags(hero)

    action_funcs = {
        'melee_attack': perform_melee_attack,
        'magic_missile': perform_magic_missile,
        'heal': perform_heal,
        'block': perform_block,
        'dodge': perform_dodge,
        'wand': perform_wand,
        'fire_bow': perform_fire_bow
    }

    if action in action_funcs:
        action_funcs[action](hero, opponent)
    else:
        print(f"❓ {hero['class']} does nothing.")

    clamp_resources(hero)
    clamp_resources(opponent)


def perform_melee_attack(hero, opponent):
    cost = 15
    if hero['cur_sta'] >= cost:
        damage = max(0, hero['features']['str'] // 6)
        apply_damage(opponent, damage)
        hero['cur_sta'] -= cost
        print(f"💥 {hero['class']} hits for {damage} melee damage!")
    else:
        print("🪫 Not enough stamina to melee attack.")

def perform_magic_missile(hero, opponent):
    cost = 20
    if hero['cur_mana'] >= cost:
        damage = max(0, hero['features']['int'] // 4 + 10)
        hero['cur_mana'] -= cost
        apply_damage(opponent, damage)
        print(f"✨ {hero['class']} casts magic missile for {damage} damage!")
    else:
        print("⚡ Not enough mana for magic missile!")

def perform_heal(hero, opponent):
    cost = 15
    if hero['cur_mana'] >= cost:
        heal_amount = hero['features']['wis'] // 2
        hero['cur_hp'] = min(hero['features']['HP'], hero['cur_hp'] + heal_amount)
        hero['cur_mana'] -= cost
        print(f"💖 {hero['class']} heals for {heal_amount} HP!")
    else:
        print("⚡ Not enough mana to heal!")

def perform_block(hero, opponent):
    hero['is_blocking'] = True
    hero['cur_sta'] = max(0, hero['cur_sta'] - 10)
    print(f"🛡️ {hero['class']} is blocking this turn.")

def perform_dodge(hero, opponent):
    hero['is_dodging'] = True
    hero['cur_sta'] = max(0, hero['cur_sta'] - 8)
    print(f"💨 {hero['class']} tries to dodge the next attack.")

def perform_wand(hero, opponent):
    cost = 8
    if hero['cur_mana'] >= cost:
        damage = hero['features']['int'] // 6 + 5
        hero['cur_mana'] -= cost
        apply_damage(opponent, damage)
        print(f"🔮 {hero['class']} attacks with wand for {damage} damage!")
    else:
        print("⚡ Not enough mana for wand attack!")

def perform_fire_bow(hero, opponent):
    cost = 12
    if hero['cur_mana'] >= cost:
        damage = hero['features']['agi'] // 4
        hero['cur_mana'] -= cost
        print(f"🔥 {hero['class']} shoots fire bow for {damage} damage!")
        apply_damage(opponent, damage)
    else:
        print("⚡ Not enough mana for fire bow!")
