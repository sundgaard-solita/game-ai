import random
import sys
import time
import csv
from mod_globals import EXTRA_FEATURES, WINS_CSV_PATH
from mod_synth_data import ARCHETYPES, CLASS_LABELS, STAT_NAMES, normalize, one_hot_class, hero_to_features
from mod_predict import predict

def init_hero():
    hero_class = random.choice(CLASS_LABELS)
    
    # Combine STAT_NAMES and EXTRA_FEATURES to initialize all features
    all_features = STAT_NAMES + EXTRA_FEATURES
    
    features = {feature: random.randint(*ARCHETYPES[hero_class][feature]) for feature in all_features}
    
    full_hp = features['HP']
    full_mana = features['Mana']
    cur_hp = full_hp
    cur_mana = full_mana
    
    return {
        'class': hero_class,
        'features': features,
        'cur_hp': cur_hp,
        'cur_mana': cur_mana
    }


def display_hero(hero, label="Hero"):
    stats_str = f"{label} Class: {hero['class']} | " + \
        " | ".join(f"{stat}: {hero['stats'][stat]}" for stat in STAT_NAMES) + \
        f" | HP: {hero['cur_hp']}/{hero['stats']['HP']} | Mana: {hero['cur_mana']}/{hero['stats']['Mana']}"
    print(stats_str)

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
    # Initialize blocking/dodging flags if missing
    if 'is_blocking' not in hero:
        hero['is_blocking'] = False
    if 'is_dodging' not in hero:
        hero['is_dodging'] = False

    if action == 'melee_attack':
        damage = max(0, hero['stats']['str'] // 6)
        apply_damage(opponent, damage)
        print(f"💥 {hero['class']} hits for {damage} melee damage!")

    elif action == 'magic_missile':
        cost = 20
        if hero['cur_mana'] >= cost:
            damage = max(0, hero['stats']['int'] // 4 + 10)
            hero['cur_mana'] -= cost
            apply_damage(opponent, damage)
            print(f"✨ {hero['class']} casts magic missile for {damage} damage!")
        else:
            print(f"⚡ Not enough mana for magic missile!")

    elif action == 'heal':
        cost = 15
        if hero['cur_mana'] >= cost:
            heal_amount = hero['stats']['wis'] // 2
            hero['cur_hp'] = min(hero['stats']['HP'], hero['cur_hp'] + heal_amount)
            hero['cur_mana'] -= cost
            print(f"💖 {hero['class']} heals for {heal_amount} HP!")
        else:
            print(f"⚡ Not enough mana to heal!")

    elif action == 'block':
        hero['is_blocking'] = True
        print(f"🛡️ {hero['class']} is blocking this turn.")

    elif action == 'dodge':
        hero['is_dodging'] = True
        print(f"💨 {hero['class']} tries to dodge the next attack.")

    elif action == 'wand':
        cost = 8
        if hero['cur_mana'] >= cost:
            damage = hero['stats']['int'] // 6 + 5
            hero['cur_mana'] -= cost
            apply_damage(opponent, damage)
            print(f"🔮 {hero['class']} attacks with wand for {damage} damage!")
        else:
            print(f"⚡ Not enough mana for wand attack!")

    elif action == 'fire_bow':
        cost = 12
        if hero['cur_mana'] >= cost:
            damage = hero['stats']['agi'] // 4
            hero['cur_mana'] -= cost
            apply_damage(opponent, damage)
            print(f"🔥 {hero['class']} shoots fire bow for {damage} damage!")
        else:
            print(f"⚡ Not enough mana for fire bow!")

    else:
        print(f"❓ {hero['class']} does nothing.")

    # Clamp HP and Mana to minimum zero
    hero['cur_hp'] = max(hero['cur_hp'], 0)
    hero['cur_mana'] = max(hero['cur_mana'], 0)
    opponent['cur_hp'] = max(opponent['cur_hp'], 0)

def append_to_wins_csv(hero1_features, hero2_features, action):
    header = None
    try:
        with open(WINS_CSV_PATH, 'r', newline='') as f:
            header = next(csv.reader(f))
    except FileNotFoundError:
        pass

    with open(WINS_CSV_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        if header is None:
            stat_fields = STAT_NAMES + ["cur_HP_ratio", "cur_Mana_ratio"] + CLASS_LABELS
            header = [f'hero1_{f}' for f in stat_fields] + [f'hero2_{f}' for f in stat_fields] + ['next_action']
            writer.writerow(header)
        writer.writerow(hero1_features + hero2_features + [action])

def print_overwrite(text):
    # Print text and overwrite previous line (works on many terminals)
    sys.stdout.write('\r' + ' ' * 120 + '\r')  # Clear line
    sys.stdout.write(text)
    sys.stdout.flush()

def play_game(predict_model):
    print("🎲 Welcome to DND Heroes League!")
    hero1 = init_hero()
    hero2 = init_hero()
    round_num = 1

    while hero1['cur_hp'] > 0 and hero2['cur_hp'] > 0:
        # Prepare normalized features
        hero1_features = hero_to_features(hero1['features'], hero1['cur_hp'], hero1['cur_mana'], hero1['class'])
        hero2_features = hero_to_features(hero2['features'], hero2['cur_hp'], hero2['cur_mana'], hero2['class'])

        # Print round + hero stats in one line
        status_line = f"Round {round_num} | Hero1: {hero1['class']} HP {hero1['cur_hp']}/{hero1['features']['HP']} | Mana {hero1['cur_mana']}/{hero1['features']['Mana']} || " \
                      f"Hero2: {hero2['class']} HP {hero2['cur_hp']}/{hero2['features']['HP']} | Mana {hero2['cur_mana']}/{hero2['features']['Mana']}"
        print_overwrite(status_line)

        # Predict actions
        action1 = predict(predict_model, hero1_features, hero2_features)
        action2 = predict(predict_model, hero2_features, hero1_features)

        # Print chosen actions in new lines to keep readability
        print(f"\nHero 1 action: {action1}")
        print(f"Hero 2 action: {action2}")

        # Apply actions
        update_hero_after_action(hero1, action1, hero2)
        if hero2['cur_hp'] <= 0:
            break

        update_hero_after_action(hero2, action2, hero1)
        if hero1['cur_hp'] <= 0:
            break

        append_to_wins_csv(hero1_features, hero2_features, action1)

        round_num += 1
        time.sleep(0.5)  # small delay for readability

    # Append last round's data (winner's last action)
    append_to_wins_csv(hero1_features, hero2_features, action1)

    print("\n\n--- Game Over ---")
    if hero1['cur_hp'] <= 0 and hero2['cur_hp'] <= 0:
        print("It's a draw! Both heroes have fallen.")
    elif hero1['cur_hp'] <= 0:
        print(f"Hero 2 ({hero2['class']}) wins the duel!")
    else:
        print(f"Hero 1 ({hero1['class']}) wins the duel!")
