import random
import sys
import time
import csv
import os
from app_config import CONFIG
from hero import Hero
from hero_action import update_hero_after_action
from hero_archetypes import get_hero_class_name
from hero_features import create_hero
from synth_data import ARCHETYPES
from predict import predict


def display_hero(hero, label="Hero"):
    stats_str = f"{label} Class: {get_hero_class_name(hero)} | " + \
        " | ".join(f"{stat}: {hero[stat]}" for stat in CONFIG.STAT_NAMES) + \
        f" | HP: {hero['rem_hp']}/{hero['hp']} | Mana: {hero['rem_mana']}/{hero['mana']} | Sta: {hero['rem_sta']}/{hero['sta']}"
    print(stats_str)


def append_to_wins_csv(hero1: Hero, hero2: Hero, action):
    os.makedirs(os.path.dirname(CONFIG.WINS_CSV_PATH), exist_ok=True)
    hero1_features = hero1.features
    hero2_features = hero2.features
    header = None
    if not os.path.isfile(CONFIG.WINS_CSV_PATH):
        stat_fields = CONFIG.STAT_NAMES + ["rem_hp_ratio", "rem_mana_ratio"] + CONFIG.HERO_CLASS_NAMES
        header = [f'hero1_{f}' for f in stat_fields] + [f'hero2_{f}' for f in stat_fields] + ['next_action']

    with open(CONFIG.WINS_CSV_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerow(list(hero1_features.values()) + list(hero2_features.values()) + [action])


def print_overwrite(text):
    # Print text and overwrite previous line (works on many terminals)
    sys.stdout.write('\r' + ' ' * 120 + '\r')  # Clear line
    sys.stdout.write(text)
    sys.stdout.flush()

def play_game(predict_model):
    print("🎲 Welcome to DND Heroes League!")
    hero1 = create_hero()#hero1, hero1['rem_hp'], hero1['rem_mana'], hero1['class'])
    hero2 = create_hero()#hero2, hero2['rem_hp'], hero2['rem_mana'], hero2['class'])
    round_num = 1

    while hero1.features['rem_hp'] > 0 and hero2.features['rem_hp'] > 0:
        # Prepare normalized features
        

        # 🧾 Print round and hero stats
        status_line = (
            f"📣 Round {round_num}\n"
            f"🧙‍♂️ Hero1 ({hero1.class_name}): "
            f"❤️ HP {hero1.features['rem_hp']}/{hero1.features['hp']} | "
            f"🔮 Mana {hero1.features['rem_mana']}/{hero1.features['mana']} | "
            f"💪 Sta {hero1.features['rem_sta']}/{hero1.features['sta']}\n"
            f"🧝‍♀️ Hero2 ({hero2.class_name}): "
            f"❤️ HP {hero2.features['rem_hp']}/{hero2.features['hp']} | "
            f"🔮 Mana {hero2.features['rem_mana']}/{hero2.features['mana']} | "
            f"💪 Sta {hero2.features['rem_sta']}/{hero2.features['sta']}"
        )
        print_overwrite(status_line)

        # 🧠 Predict actions
        action1 = predict(predict_model, hero1, hero2)
        action2 = predict(predict_model, hero2, hero1)

        # 🗡️ Print actions taken
        print(f"\n🎯 Hero 1 action: {action1}")
        print(f"🎯 Hero 2 action: {action2}")

        # Apply actions
        update_hero_after_action(hero1, action1, hero2)
        if hero2.features['rem_hp'] <= 0: # Hero 2 defeated
            break

        update_hero_after_action(hero2, action2, hero1)
        if hero1.features['rem_hp'] <= 0: # Hero 1 defeated
            break

        append_to_wins_csv(hero1, hero2, action1)

        round_num += 1
        time.sleep(0.5)  # small delay for readability

    # Append last round's data (winner's last action)
    append_to_wins_csv(hero1, hero2, action1)

    print("\n\n--- Game Over ---")
    if hero1.features['rem_hp'] <= 0 and hero2.features['rem_hp'] <= 0:
        print("It's a draw! Both heroes have fallen.")
    elif hero1.features['rem_hp'] <= 0:
        print(f"Hero 2 ({hero2.class_name}) wins the duel!")
    else:
        print(f"Hero 1 ({hero1.class_name}) wins the duel!")
