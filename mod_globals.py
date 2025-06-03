import os
import random

MODEL_DIR = './model'
MODEL_PATH = os.path.join(MODEL_DIR, 'gameai.safetensor')
WINS_CSV_PATH = './training_data/wins.csv'
HERO_CLASS_NAMES = ['Warrior', 'Rogue', 'Mage', 'Cleric']

STAT_NAMES = ['str', 'con', 'agi', 'dex', 'int', 'wis', 'cha', 'sta', 'hp', 'mana', 'rem_hp', 'rem_mana', 'rem_sta']
EXTRA_FEATURES = ["level", "weapon_pwr", "spell_pwr", "block_pwr"]
# Combine all features into a single list, i.e stats, extra and hero class names one-hot encoded
ALL_FEATURES = STAT_NAMES + EXTRA_FEATURES + HERO_CLASS_NAMES
# Total length of all input features 
NUM_FEATURES_PER_HERO = len(ALL_FEATURES)
# times 2 (for both heroes)
TOTAL_INPUT_FEATURES = 2 * NUM_FEATURES_PER_HERO


ACTIONS = ['heal', 'melee_attack', 'magic_missile', 'wand', 'block', 'dodge', 'fire_bow', 'rest', 'cast_protection_1']
NUM_ACTIONS = len(ACTIONS)

HIDDEN_LAYER_SIZE = 128  # Avoid hardcoded values