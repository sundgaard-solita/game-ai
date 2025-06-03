import csv
import os
import random
from hero_archetypes import ARCHETYPES
from hero_features import one_hot_encode_hero_class_by_name
from mod_globals import ACTIONS, ALL_FEATURES, HERO_CLASS_NAMES, STAT_NAMES
from mod_logging import log_debug

SYNTH_DATA_DIR = './synth_data'
SYNTH_DATA_PATH = os.path.join(SYNTH_DATA_DIR, 'synthetic_data.csv')

def normalize_features(features_dict, max_value=100):
    """
    Normalize numeric feature values to 0-1 range by dividing by max_value.
    Leaves 0/1 one-hot encoded features as-is.

    Args:
        features_dict (dict): feature_name -> numeric value
        max_value (float): value to normalize against

    Returns:
        dict: normalized features
    """
    normalized = {}
    for key, value in features_dict.items():
        if isinstance(value, (int, float)):
            # Leave 0/1 as-is (likely one-hot)
            if value in (0, 1):
                normalized[key] = value
            else:
                normalized[key] = value / max_value
        else:
            normalized[key] = value  # keep strings or other types as-is

    return normalized

def generate_sample_feature_values(hero_class):
    # Ge default feature values based on the hero class / ARCHETYPE
    archetype_base_feature_values = ARCHETYPES[hero_class]
    missing_feats = [feat for feat in ALL_FEATURES if feat not in archetype_base_feature_values]
    # Check if all required features are defined in the archetype
    if missing_feats:
        print(f"🚨 Missing features in ARCHETYPES[{hero_class}]: {missing_feats}.")
        print(f"🤔 Did we forget to define these features? Please check ARCHETYPES.")
        raise KeyError(f"Missing feature definitions for: {missing_feats}")
    
    # Adjust the default hero feature values but ensure they are sensible for the given hero class
    return {feat: random.randint(*archetype_base_feature_values[feat]) for feat in ALL_FEATURES}

def randomize_current_hp_mana_and_sta(hero_sample_feature_values):
    """
    Randomly adjusts remaining HP, mana and stamina values for a hero within a realistic range.

    The current values are sampled between 30% and 100% of the hero's max HP, mana and stamina.
    This simulates a variety of combat readiness states—from weakened to fully charged—
    to create more diverse and realistic training data for the model.
    """
    # Get the base values for HP, mana and stamina from the hero sample feature values
    hp = hero_sample_feature_values["hp"]
    mana = hero_sample_feature_values["mana"]
    sta = hero_sample_feature_values["sta"]
    # Randomly set remaining HP, mana and stamina to a value between 30% and 100% of the max values
    hero_sample_feature_values["rem_hp"] = random.randint(int(hp * 0.3), hp)
    hero_sample_feature_values["rem_mana"] = random.randint(int(mana * 0.3), mana)
    hero_sample_feature_values["rem_sta"] = random.randint(int(sta * 0.3), sta)
    return


def pick_random_action_no_predict(hero1_sample_feature_values, hero2_sample_feature_values):
    """
    Intelligently select next action based on hero state and class archetype.
    Returns: Most logical action given current battle conditions
    """
    # Initialize action weights dictionary with base weights
    weights = {action: 1 for action in ACTIONS}  # Start with minimal base weights
    
    # Calculate important combat ratios
    hp_ratio = hero1_sample_feature_values['rem_hp'] / hero1_sample_feature_values['hp']
    mana_ratio = hero1_sample_feature_values['rem_mana'] / hero1_sample_feature_values['mana']
    sta_ratio = hero1_sample_feature_values['rem_sta'] / hero1_sample_feature_values['sta']
    
    # Class-specific behavior patterns
    if hero1_sample_feature_values['Warrior'] == 1:
        weights.update({
            'melee_attack': 35 if sta_ratio > 0.3 else 10,
            'block': 25 if hp_ratio < 0.4 else 15,
            'dodge': 15 if sta_ratio > 0.4 else 5,
            'rest': 30 if sta_ratio < 0.2 else 5
        })
        
    elif hero1_sample_feature_values['Rogue'] == 1:
        weights.update({
            'dodge': 30 if sta_ratio > 0.3 else 10,
            'fire_bow': 25 if sta_ratio > 0.4 else 5,
            'melee_attack': 20 if sta_ratio > 0.5 else 5,
            'rest': 25 if sta_ratio < 0.3 else 5
        })
        
    elif hero1_sample_feature_values['Mage'] == 1:
        weights.update({
            'magic_missile': 35 if mana_ratio > 0.4 else 5,
            'wand': 20 if mana_ratio > 0.2 else 15,
            'dodge': 15 if sta_ratio > 0.5 else 5,
            'rest': 30 if mana_ratio < 0.3 else 5
        })
        
    elif hero1_sample_feature_values['Cleric'] == 1:
        weights.update({
            'heal': 35 if (hp_ratio < 0.5 and mana_ratio > 0.3) else 10,
            'cast_protection_1': 25 if mana_ratio > 0.4 else 5,
            'melee_attack': 20 if sta_ratio > 0.4 else 5,
            'rest': 25 if (mana_ratio < 0.3 or hp_ratio < 0.3) else 5
        })

    # Universal defensive behaviors
    if hp_ratio < 0.3:  # Critical HP
        weights['rest'] += 20
        weights['dodge'] += 15
        weights['block'] += 15
        if hero1_sample_feature_values['Cleric'] == 1 or hero1_sample_feature_values['Mage'] == 1 and mana_ratio > 0.2:
            weights['heal'] += 25

    # Resource management
    if sta_ratio < 0.2 or mana_ratio < 0.2:
        weights['rest'] += 30
        for action in ['melee_attack', 'dodge', 'block', 'fire_bow']:
            weights[action] = max(1, weights[action] - 15)

    # Weighted random selection
    total_weight = sum(weights.values())
    roll = random.uniform(0, total_weight)
    current_weight = 0
    
    for action, weight in weights.items():
        current_weight += weight
        if roll <= current_weight:
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

        # Write all features as headers to CSV file for training purposes
        # Prefix hero features with hero1_ and hero2_ as we need to distinguish between two heroes.
        # Predicted column is next_action.
        header_row = [f'hero1_{feature}' for feature in ALL_FEATURES] + [f'hero2_{f}' for f in ALL_FEATURES] + ['next_action']
        writer.writerow(header_row)

        for _ in range(num_samples):
            # Pick random hero classes for each hero for training purposes
            hero1_class = random.choice(HERO_CLASS_NAMES) 
            hero2_class = random.choice(HERO_CLASS_NAMES)

            try:
                # For each hero, generate sample feature values based on their class / ARCHETYPE
                hero1_sample_feature_values = generate_sample_feature_values(hero1_class)
                hero2_sample_feature_values = generate_sample_feature_values(hero2_class)           

                randomize_current_hp_mana_and_sta(hero1_sample_feature_values)
                randomize_current_hp_mana_and_sta(hero2_sample_feature_values)

                one_hot_encode_hero_class_by_name(hero1_class, hero1_sample_feature_values)
                one_hot_encode_hero_class_by_name(hero2_class, hero2_sample_feature_values)
            except KeyError:
                return  # Suppress traceback for known error

            next_action = pick_random_action_no_predict(hero1_sample_feature_values, hero2_sample_feature_values)

            hero1_sample_feature_values = normalize_features(hero1_sample_feature_values)
            hero2_sample_feature_values = normalize_features(hero2_sample_feature_values)
            writer.writerow(list(hero1_sample_feature_values.values()) + list(hero2_sample_feature_values.values()) + [next_action])
            data.append((list(hero1_sample_feature_values) + list(hero2_sample_feature_values), next_action))

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



# TEMP
def force_pick_synthetic_action_temp(hero, cur_hp, cur_mana, cur_sta):
    """Intelligently select next action based on hero state and class archetype."""
    
    # Calculate resource ratios
    hp_ratio = cur_hp / hero['HP']
    mana_ratio = cur_mana / hero['Mana']
    sta_ratio = cur_sta / hero['sta']
    
    log_debug(f"Hero State - HP: {hp_ratio:.2f}, Mana: {mana_ratio:.2f}, STA: {sta_ratio:.2f}", "📊")
    
    # Base weights with class-specific adjustments
    weights = {action: 1 for action in ACTIONS}
    
    # Universal critical state handling
    if hp_ratio < 0.3:
        log_debug("Critical HP state detected!", "⚠️")
        weights['rest'] += 25
        if hero['class'] in ['Cleric', 'Mage'] and mana_ratio > 0.3:
            weights['heal'] += 30
    
    # Class-specific behavior patterns
    class_behaviors = {
        'Warrior': {
            'primary': ('melee_attack', 40, sta_ratio > 0.3),
            'secondary': ('block', 25, hp_ratio < 0.5),
            'defensive': ('dodge', 15, sta_ratio > 0.4)
        },
        'Rogue': {
            'primary': ('fire_bow', 35, sta_ratio > 0.4),
            'secondary': ('dodge', 30, sta_ratio > 0.3),
            'defensive': ('melee_attack', 20, sta_ratio > 0.5)
        },
        'Mage': {
            'primary': ('magic_missile', 40, mana_ratio > 0.4),
            'secondary': ('wand', 25, mana_ratio > 0.3),
            'defensive': ('dodge', 20, sta_ratio > 0.4)
        },
        'Cleric': {
            'primary': ('heal', 35, hp_ratio < 0.6 and mana_ratio > 0.4),
            'secondary': ('cast_protection_1', 30, mana_ratio > 0.5),
            'defensive': ('melee_attack', 20, sta_ratio > 0.4)
        }
    }
    
    # Apply class-specific weights
    behavior = class_behaviors[hero['class']]
    for action_type, (action, weight, condition) in behavior.items():
        if condition:
            weights[action] += weight
            log_debug(f"Adding {weight} weight to {action} ({action_type})", "⚖️")
    
    # Resource management adjustments
    if sta_ratio < 0.2:
        log_debug("Low stamina state - adjusting weights", "🪫")
        weights['rest'] += 35
        for action in ['melee_attack', 'dodge', 'block', 'fire_bow']:
            weights[action] = max(1, weights[action] - 20)
    
    if mana_ratio < 0.2:
        log_debug("Low mana state - adjusting weights", "⚡")
        weights['rest'] += 35
        for action in ['magic_missile', 'heal', 'wand', 'cast_protection_1']:
            weights[action] = max(1, weights[action] - 20)
    
    # Select action based on weights
    total_weight = sum(weights.values())
    roll = random.uniform(0, total_weight)
    current = 0
    
    for action, weight in weights.items():
        current += weight
        if roll <= current:
            log_debug(f"Selected action: {action} (weight: {weight})", "✅")
            return action

def create_synthetic_data_temp(num_samples=1000, force_regenerate=False):
    """Generate synthetic training data with realistic class behaviors."""
    if os.path.exists(SYNTH_DATA_PATH) and not force_regenerate:
        log_debug("Loading cached synthetic data from CSV...", "📂")
        return load_synthetic_data()

    log_debug("Generating new synthetic data...", "🧪")
    os.makedirs(SYNTH_DATA_DIR, exist_ok=True)
    data = []
    with open(SYNTH_DATA_PATH, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Header
        stat_fields = ALL_FEATURES + ["cur_HP_ratio", "cur_Mana_ratio"] + HERO_CLASS_NAMES
        header = [f'hero1_{f}' for f in stat_fields] + [f'hero2_{f}' for f in stat_fields] + ['next_action']
        writer.writerow(header)

        synthetic_data = []
        log_debug(f"Generating {num_samples} synthetic battles...", "🎲")
        
        for i in range(num_samples):
            if i % 100 == 0:
                log_debug(f"Progress: {i}/{num_samples}", "📈")
                
            # Generate heroes with appropriate class distributions
            hero1_class = random.choice(HERO_CLASS_NAMES)
            hero2_class = random.choice(HERO_CLASS_NAMES)
            
            # Generate base stats with some randomization but maintaining class identity
            hero1 = {
                'class': hero1_class,
                **{stat: random.randint(*ARCHETYPES[hero1_class][stat]) 
                for stat in ALL_FEATURES}
            }
            
            hero2 = {
                'class': hero2_class,
                **{stat: random.randint(*ARCHETYPES[hero2_class][stat]) 
                for stat in ALL_FEATURES}
            }
            
            # Generate realistic resource levels based on battle progression
            battle_progress = random.random()  # 0.0 to 1.0
            
            # Earlier in battle = higher resources
            base_resource_ratio = 0.4 + (0.6 * (1 - battle_progress))
            variation = 0.2  # Allow for ±20% variation
            
            hero1_cur_hp = hero1['HP'] * max(0.1, min(1.0, base_resource_ratio + random.uniform(-variation, variation)))
            hero1_cur_mana = hero1['Mana'] * max(0.1, min(1.0, base_resource_ratio + random.uniform(-variation, variation)))
            hero1_cur_sta = hero1['sta'] * max(0.1, min(1.0, base_resource_ratio + random.uniform(-variation, variation)))
            
            # Create feature vectors
            hero1_features = [
                *[hero1[feat] for feat in ALL_FEATURES],
                hero1_cur_hp / hero1['HP'],
                hero1_cur_mana / hero1['Mana'],
                hero1_cur_sta / hero1['sta'],
                *[1 if hero1_class == c else 0 for c in HERO_CLASS_NAMES]
            ]
            
            hero2_features = [
                *[hero2[feat] for feat in ALL_FEATURES],
                hero2['HP'],
                hero2['Mana'],
                hero2['sta'],
                *[1 if hero2_class == c else 0 for c in HERO_CLASS_NAMES]
            ]
            
            action = force_pick_synthetic_action_temp(hero1, hero1_cur_hp, hero1_cur_mana, hero1_cur_sta)
            synthetic_data.append((hero1_features + hero2_features, action))
            writer.writerow(hero1_features + hero2_features + [action])

    log_debug(f"Synthetic data saved to {SYNTH_DATA_PATH}", "💾")
    log_debug("Synthetic data generation complete!", "🎮")
    return synthetic_data
