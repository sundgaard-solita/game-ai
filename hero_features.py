from hero_archetypes import ARCHETYPES
from mod_globals import HERO_CLASS_NAMES, EXTRA_FEATURES, STAT_NAMES, TOTAL_INPUT_FEATURES

# Normalize to 0-1
def normalize(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val)

def one_hot_encode_hero_class_by_name(hero_class, hero_sample_feature_values):
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
    if hero_class not in HERO_CLASS_NAMES:
        raise ValueError(f"Unknown hero class: {hero_class}")

    for class_name in HERO_CLASS_NAMES:
        if class_name not in hero_sample_feature_values:
            raise ValueError(f"Missing expected one-hot encoded hero class field in hero_sample_feature_values: {class_name}")

    hero_sample_feature_values[hero_class] = 1


def hero_to_features(stats, cur_hp, cur_mana, hero_class):
    all_feats = STAT_NAMES + EXTRA_FEATURES
    norm_stats = [normalize(stats[feat], *ARCHETYPES[hero_class][feat]) for feat in all_feats]
    hp_ratio = cur_hp / stats["HP"] if stats["HP"] > 0 else 0
    mana_ratio = cur_mana / stats["Mana"] if stats["Mana"] > 0 else 0
    full_feature_vector = norm_stats + [hp_ratio, mana_ratio] # + one_hot_encode_hero_class(hero_class)

    expected_len = TOTAL_INPUT_FEATURES // 2
    if len(full_feature_vector) != expected_len:
        print(f"🚨 Feature length mismatch! Expected {expected_len}, got {len(full_feature_vector)}")
        print(f"🧪 Features: {all_feats}")
        print(f"📊 Vector: {full_feature_vector}")
        exit(1)

    return full_feature_vector
