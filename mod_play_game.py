import random
import sys
import time
import csv
import os
from hero_action import apply_damage, update_hero_after_action
from hero_features import hero_to_features
from mod_globals import EXTRA_FEATURES, WINS_CSV_PATH
from mod_synth_data import ARCHETYPES, CLASS_LABELS, STAT_NAMES
from mod_predict import predict

def init_hero():
    hero_class = random.choice(CLASS_LABELS)
    
    # Combine STAT_NAMES and EXTRA_FEATURES to initialize all features
    all_features = STAT_NAMES + EXTRA_FEATURES
    
    features = {feature: random.randint(*ARCHETYPES[hero_class][feature]) for feature in all_features}
    
    full_hp = features['HP']
    full_mana = features['Mana']
    full_sta = features['sta']
    cur_hp = full_hp
    cur_mana = full_mana
    cur_sta = full_sta
    
    return {
        'class': hero_class,
        'features': features,
        'cur_hp': cur_hp,
        'cur_mana': cur_mana,
        'cur_sta': cur_sta,
    }


def display_hero(hero, label="Hero"):
    stats_str = f"{label} Class: {hero['class']} | " + \
        " | ".join(f"{stat}: {hero['features'][stat]}" for stat in STAT_NAMES) + \
        f" | HP: {hero['cur_hp']}/{hero['features']['HP']} | Mana: {hero['cur_mana']}/{hero['features']['Mana']}"
    print(stats_str)


def append_to_wins_csv(hero1_features, hero2_features, action):
    os.makedirs(os.path.dirname(WINS_CSV_PATH), exist_ok=True)

    header = None
    if not os.path.isfile(WINS_CSV_PATH):
        stat_fields = STAT_NAMES + ["cur_HP_ratio", "cur_Mana_ratio"] + CLASS_LABELS
        header = [f'hero1_{f}' for f in stat_fields] + [f'hero2_{f}' for f in stat_fields] + ['next_action']

    with open(WINS_CSV_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        if header:
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

        # 🧾 Print round and hero stats
        status_line = (
            f"📣 Round {round_num}\n"
            f"🧙‍♂️ Hero1 ({hero1['class']}): "
            f"❤️ HP {hero1['cur_hp']}/{hero1['features']['HP']} | "
            f"🔮 Mana {hero1['cur_mana']}/{hero1['features']['Mana']} | "
            f"💪 Sta {hero1['cur_sta']}/{hero1['features']['sta']}\n"
            f"🧝‍♀️ Hero2 ({hero2['class']}): "
            f"❤️ HP {hero2['cur_hp']}/{hero2['features']['HP']} | "
            f"🔮 Mana {hero2['cur_mana']}/{hero2['features']['Mana']} | "
            f"💪 Sta {hero2['cur_sta']}/{hero2['features']['sta']}"
        )
        print_overwrite(status_line)

        # 🧠 Predict actions
        action1 = predict(predict_model, hero1_features, hero2_features)
        action2 = predict(predict_model, hero2_features, hero1_features)

        # 🗡️ Print actions taken
        print(f"\n🎯 Hero 1 action: {action1}")
        print(f"🎯 Hero 2 action: {action2}")


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
