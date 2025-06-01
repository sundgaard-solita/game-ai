from hero_archetypes import ARCHETYPES
from mod_globals import CLASS_LABELS, EXTRA_FEATURES, STAT_NAMES, TOTAL_INPUT_FEATURES

# Normalize to 0-1
def normalize(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val)

def one_hot_class(hero_class):
    return [1 if hero_class == cls else 0 for cls in CLASS_LABELS]

def hero_to_features(stats, cur_hp, cur_mana, hero_class):
    all_feats = STAT_NAMES + EXTRA_FEATURES
    norm_stats = [normalize(stats[feat], *ARCHETYPES[hero_class][feat]) for feat in all_feats]
    hp_ratio = cur_hp / stats["HP"] if stats["HP"] > 0 else 0
    mana_ratio = cur_mana / stats["Mana"] if stats["Mana"] > 0 else 0
    full_feature_vector = norm_stats + [hp_ratio, mana_ratio] + one_hot_class(hero_class)

    expected_len = TOTAL_INPUT_FEATURES // 2
    if len(full_feature_vector) != expected_len:
        print(f"🚨 Feature length mismatch! Expected {expected_len}, got {len(full_feature_vector)}")
        print(f"🧪 Features: {all_feats}")
        print(f"📊 Vector: {full_feature_vector}")
        exit(1)

    return full_feature_vector
