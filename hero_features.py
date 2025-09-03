import random
from hero import Hero
from hero_archetypes import ARCHETYPES
from app_config import CONFIG

# Normalize to 0-1
#def normalize(value, min_val, max_val):
#    return (value - min_val) / (max_val - min_val)

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


def one_hot_encode_hero_class_by_name(hero:Hero):
    """
    Updates the class one-hot section in `features` based on `feature_names`, using `hero_class`.

    Looks for field names matching HERO_CLASS_NAMES, then sets the corresponding
    one-hot values in `features`.

    Args:
        feature_names (List[str]): Names corresponding to each feature index.
        features (List[float/int]): The actual numeric feature values.
        hero_class (str): The class to encode.

    Raises:
        ValueError: If any class name is not found in `feature_names`, or class is unknown.
    """
    #print(hero.features)
    if hero.class_name not in CONFIG.HERO_CLASS_NAMES:
        raise ValueError(f"Unknown hero class: {class_name}")

    for class_name in CONFIG.HERO_CLASS_NAMES:
        if class_name not in hero.features:
            raise ValueError(f"Missing expected one-hot encoded hero class field in hero_features: {class_name}")

    hero.features[hero.class_name] = 1

def init_hero()-> Hero:
    hero_class_name = random.choice(CONFIG.HERO_CLASS_NAMES)
    
    # Combine STAT_NAMES and EXTRA_FEATURES to initialize all features
    all_features = CONFIG.ALL_FEATURES
    
    features = {feature: random.randint(*ARCHETYPES[hero_class_name][feature]) for feature in all_features}
    
    full_hp = features['hp']
    full_mana = features['mana']
    full_sta = features['sta']
    rem_hp = full_hp
    rem_mana = full_mana
    rem_sta = full_sta
        
    features['rem_hp'] = rem_hp
    features['rem_mana'] = rem_mana
    features['rem_sta'] = rem_sta
    hero = Hero()
    hero.class_name = hero_class_name
    hero.features = features
    return hero

def create_hero()-> Hero:
    hero = init_hero()
    #all_feats = STAT_NAMES + EXTRA_FEATURES
    #norm_stats = [normalize(stats[feat], *ARCHETYPES[hero_class][feat]) for feat in all_feats]
    #all_feats_norm = normalize_features(all_feats,100)
    #hp_ratio = rem_hp / hero_features['hp'] if hero_features['hp'] > 0 else 0
    #mana_ratio = rem_mana / hero_features['mana'] if hero_features['mana'] > 0 else 0
    #full_feature_vector = all_feats_norm + [hp_ratio, mana_ratio] # + one_hot_encode_hero_class(hero_class)
    one_hot_encode_hero_class_by_name(hero)

    # Check for missing or additional features, excluding ephemeral features
    ephemeral = {'bogus'} #'is_blocking', 'is_dodging', 'is_casting', 'is_using_wand', 'is_using_bow', 'is_resting', 'is_protected', 'is_healing', 'is_attacking'}
    expected_features = set(CONFIG.ALL_FEATURES) - ephemeral
    hero_keys = set(hero.features.keys()) - ephemeral
    expected_len = CONFIG.NUM_FEATURES_PER_HERO - len(ephemeral & set(CONFIG.ALL_FEATURES))
    if len(hero_keys) != expected_len:
        print(f"🚨 Feature length mismatch! Expected {expected_len}, got {len(hero_keys)}")
        print(f"🧪 All Features (excluding ephemeral): {expected_features}")
        print(f"📊 Hero Features: {hero_keys}")
        missing = expected_features - hero_keys
        additional = hero_keys - expected_features
        if missing:
            print(f"❌ Missing feature(s): {', '.join(missing)}")
        if additional:
            print(f"⚠️ Additional feature(s): {', '.join(additional)}")
        raise ValueError("Feature length mismatch: see above for details.")

    return hero
