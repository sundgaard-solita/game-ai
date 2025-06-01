import csv
import os
import random
from hero_archetypes import ARCHETYPES
from mod_globals import ACTIONS, ALL_FEATURES, CLASS_LABELS, STAT_NAMES

SYNTH_DATA_DIR = './synth_data'
SYNTH_DATA_PATH = os.path.join(SYNTH_DATA_DIR, 'synthetic_data.csv')


# Normalize to 0-1
def normalize(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val)

def one_hot_class(hero_class):
    return [1 if hero_class == cls else 0 for cls in CLASS_LABELS]

#def sample_stats_for_class(hero_class):
#    return {stat: random.randint(*ARCHETYPES[hero_class][stat]) for stat in STAT_NAMES}

def sample_features_for_class(hero_class):
    defined_feats = ARCHETYPES[hero_class]
    missing_feats = [feat for feat in ALL_FEATURES if feat not in defined_feats]
    if missing_feats:
        print(f"🚨 Missing features in ARCHETYPES[{hero_class}]: {missing_feats}.")
        print(f"🤔 Did we forget to define these features? Please check ARCHETYPES.")
        raise KeyError(f"Missing feature definitions for: {missing_feats}")
    
    # Sample all features (base stats + extras)
    return {feat: random.randint(*defined_feats[feat]) for feat in ALL_FEATURES}




def sample_current_hp_mana(stats):
    hp = stats["HP"]
    mana = stats["Mana"]
    current_hp = random.randint(int(hp * 0.3), hp)  # allow low HP
    current_mana = random.randint(int(mana * 0.3), mana)
    return current_hp, current_mana

def hero_to_features(stats, cur_hp, cur_mana, hero_class):
    norm_stats = [normalize(stats[stat], *ARCHETYPES[hero_class][stat]) for stat in STAT_NAMES]
    hp_ratio = cur_hp / stats["HP"] if stats["HP"] > 0 else 0
    mana_ratio = cur_mana / stats["Mana"] if stats["Mana"] > 0 else 0
    return norm_stats + [hp_ratio, mana_ratio] + one_hot_class(hero_class)

def select_action(stats, cur_hp, cur_mana, opponent_hp):
    str_ = stats.get('str', 0)
    sta = stats.get('sta', 0)
    agi = stats.get('agi', 0)
    dex = stats.get('dex', 0)
    int_ = stats.get('int', 0)
    wis = stats.get('wis', 0)
    cha = stats.get('cha', 0)
    HP = stats.get('HP', 1)
    Mana = stats.get('Mana', 1)

    hp_ratio = cur_hp / HP
    mana_ratio = cur_mana / Mana

    action_weights = {a: 0 for a in ACTIONS}

    # Aggressive play if opponent is low
    if opponent_hp < HP:
        action_weights['melee_attack'] += 10
        action_weights['magic_missile'] += 10

    if hp_ratio < 0.3:
        action_weights['block'] += 50
        if wis > 60:
            action_weights['heal'] += 40
    else:
        if str_ > 70:
            action_weights['melee_attack'] += 40
            action_weights['block'] += 10

        if int_ > 70 and mana_ratio > 0.5:
            action_weights['magic_missile'] += 40
            action_weights['wand'] += 30

        if agi > 70 or dex > 70:
            action_weights['dodge'] += 40
            action_weights['fire_bow'] += 30

    # Base weight
    for a in action_weights:
        if action_weights[a] == 0:
            action_weights[a] = 5

    total = sum(action_weights.values())
    rnd = random.random() * total
    cumulative = 0
    for action, weight in action_weights.items():
        cumulative += weight
        if rnd <= cumulative:
            return action

def create_synthetic_data(num_samples=1000, force_regenerate=False):
    if os.path.exists(SYNTH_DATA_PATH) and not force_regenerate:
        print("📂 Loading cached synthetic data from CSV...")
        return load_synthetic_data()

    print("🧪 Generating new synthetic data...")
    os.makedirs(SYNTH_DATA_DIR, exist_ok=True)
    data = []
    with open(SYNTH_DATA_PATH, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Header
        stat_fields = ALL_FEATURES + ["cur_HP_ratio", "cur_Mana_ratio"] + CLASS_LABELS
        header = [f'hero1_{f}' for f in stat_fields] + [f'hero2_{f}' for f in stat_fields] + ['next_action']
        writer.writerow(header)

        for _ in range(num_samples):
            hero1_class = random.choice(CLASS_LABELS)
            hero2_class = random.choice(CLASS_LABELS)

            try:
                hero1_stats = sample_features_for_class(hero1_class)
                hero2_stats = sample_features_for_class(hero2_class)           

                hero1_cur_hp, hero1_cur_mana = sample_current_hp_mana(hero1_stats)
                hero2_cur_hp, hero2_cur_mana = sample_current_hp_mana(hero2_stats)

                #hero1_features = [hero1_stats[f] for f in ALL_FEATURES]
                hero1_features = [hero1_stats[f] for f in ALL_FEATURES] + [
                    hero1_cur_hp / hero1_stats['HP'],
                    hero1_cur_mana / hero1_stats['Mana']
                ] + one_hot_class(hero1_class)

                #hero2_features = [hero2_stats[f] for f in ALL_FEATURES]
                hero2_features = [hero2_stats[f] for f in ALL_FEATURES] + [
                    hero2_cur_hp / hero2_stats['HP'],
                    hero2_cur_mana / hero2_stats['Mana']
                ] + one_hot_class(hero2_class)
            except KeyError:
                return  # Suppress traceback for known error

            action = select_action(hero1_stats, hero1_cur_hp, hero1_cur_mana, hero2_cur_hp)

            writer.writerow(hero1_features + hero2_features + [action])
            data.append((hero1_features + hero2_features, action))

    print(f"💾 Synthetic data saved to {SYNTH_DATA_PATH}")
    return data

def load_synthetic_data():
    data = []
    with open(SYNTH_DATA_PATH, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        feature_len = len(header) - 1
        for row in reader:
            features = list(map(float, row[:feature_len]))
            label = row[-1]
            if label not in ACTIONS:
                raise ValueError(f"Unexpected label: {label}")
            data.append((features, label))
    return data
