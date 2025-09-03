import random
import sys
import time
import csv
import os

from torch import nn
import torch
from app_config import CONFIG
from app_logger import DEBUG, INFO, logger
from hero import Hero
from hero_action import update_hero_after_action
from hero_archetypes import get_hero_class_name
from hero_features import create_hero
from synth_data import ARCHETYPES
from predict import predict
from train_model import DEVICE

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

def play_game(predict_model, max_rounds:int=10, round_lag:float=0.1):
    hero1 = create_hero()#hero1, hero1['rem_hp'], hero1['rem_mana'], hero1['class'])
    hero2 = create_hero()#hero2, hero2['rem_hp'], hero2['rem_mana'], hero2['class'])
    round_num = 1

    # ⚙️ Set up optimizer once for the model (outside play loop)
    optimizer = torch.optim.AdamW(predict_model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()  # loss = how wrong action choice was

    # 📦 Memory buffer: store states + chosen actions during this battle
    battle_memory = []

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
        logger.debug('\r' + ' ' * 120 + '\r')
        logger.debug(status_line)

        # 🧠 Predict actions
        prediction1 = predict(predict_model, hero1, hero2)
        prediction2 = predict(predict_model, hero2, hero1)

        # 🗡️ Print actions taken
        logger.debug(f"\n🎯 Hero 1 action: {prediction1.action_name}")
        logger.debug(f"🎯 Hero 2 action: {prediction2.action_name}")

        # 💾 Remember this turn for training later
        state_features = list(hero1.features.values()) + list(hero2.features.values())  # the input numbers
        battle_memory.append((state_features, prediction1.action_index, prediction1.action_scores))           # save: state, chosen action, all scores

        # Apply actions
        update_hero_after_action(hero1, prediction1.action_name, hero2)
        if hero2.features['rem_hp'] <= 0: # Hero 2 defeated
            break

        update_hero_after_action(hero2, prediction2.action_name, hero1)
        if hero1.features['rem_hp'] <= 0: # Hero 1 defeated
            break

        #append_to_wins_csv(hero1, hero2, prediction1.action_name)

        round_num += 1
        time.sleep(round_lag)  # small delay for readability
        if(round_num>max_rounds): break # circuit breaker

    # Append last round's data (winner's last action)
    #append_to_wins_csv(hero1, hero2, prediction1.action_name)

    logger.debug("\n\n--- Game Over ---")

    # 🏆 Decide winner → this is our reward signal
    if( hero1.features['rem_hp'] <= 0 and hero2.features['rem_hp'] <= 0):
        reward = 0  # draw
        logger.debug("It's a draw! Both heroes have fallen.")
    elif(hero1.features['rem_hp'] > 0 and hero2.features['rem_hp'] > 0):
        reward = 0  # draw
        logger.debug("It's a draw! No hero was defeated, battle was at a stand still.")        
    elif hero1.features['rem_hp'] <= 0:
        reward = -1  # hero1 lost
        logger.debug(f"Hero 2 ({hero2.class_name}) wins the duel!")
    else:
        reward = +1  # hero1 won
        logger.debug(f"Hero 1 ({hero1.class_name}) wins the duel!")

    # 📚 TRAINING STEP: use memory from this battle
    if reward != 0:  # only train if clear win/loss
        optimizer.zero_grad()
        loss_total = 0.0

        for features, action, logits in battle_memory:
            # 🎯 Turn action into target tensor
            target = torch.tensor([action], device=DEVICE)
            # 🧩 Compute loss (nudged by reward)
            loss = criterion(logits.unsqueeze(0), target) * (-reward)
            loss_total += loss

        # 🧮 Backprop: nudge model toward good moves, away from bad ones
        loss_total.backward()
        optimizer.step()
        logger.info(f"📖 Model updated with reward={reward}, total loss={loss_total.item():.4f}")

        # 💾 Save updated model
        torch.save(predict_model.state_dict(), "model/gameai.safetensor")
        logger.info("💾 Model saved to model/gameai.safetensor")    

def play_games(predict_model, no_of_games:int=1, max_rounds:int=10, round_lag:float=0.1):
    logger.info("🎲 Welcome to DND Heroes League!")
    for i in range(0, 100): 
        play_game(predict_model=predict_model, max_rounds=max_rounds, round_lag=round_lag)
