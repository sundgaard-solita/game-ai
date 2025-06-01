import os
import random

MODEL_DIR = './model'
MODEL_PATH = os.path.join(MODEL_DIR, 'gameai.safetensor')
WINS_CSV_PATH = './training_data/wins.csv'
CLASS_LABELS = ['Warrior', 'Rogue', 'Mage', 'Cleric']

STAT_NAMES = ['str', 'con', 'agi', 'dex', 'int', 'wis', 'cha', 'sta', 'HP', 'Mana']
EXTRA_FEATURES = ["level", "weapon_pwr", "spell_pwr", "block_pwr"]
ALL_FEATURES = STAT_NAMES + EXTRA_FEATURES
NUM_FEATURES_PER_HERO = len(ALL_FEATURES)
TOTAL_INPUT_FEATURES = NUM_FEATURES_PER_HERO * 2 + 2 * (2 + len(CLASS_LABELS))  # 40


ACTIONS = ['heal', 'melee_attack', 'magic_missile', 'wand', 'block', 'dodge', 'fire_bow']
NUM_ACTIONS = len(ACTIONS)

HIDDEN_LAYER_SIZE = 128  # Avoid hardcoded values