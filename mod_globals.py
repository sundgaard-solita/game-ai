import os
import random

MODEL_DIR = './model'
MODEL_PATH = os.path.join(MODEL_DIR, 'gameai.safetensor')
WINS_CSV_PATH = './training_data/wins.csv'
CLASS_LABELS = ['Warrior', 'Rogue', 'Mage', 'Cleric']
STAT_NAMES = ['str', 'sta', 'agi', 'dex', 'int', 'wis', 'cha', 'HP', 'Mana']
ACTIONS = ['heal', 'melee_attack', 'magic_missile', 'wand', 'block', 'dodge', 'fire_bow']
NUM_ACTIONS = len(ACTIONS)

# Each hero has:
# - 9 normalized stats
# - 2 current HP/Mana ratios
# - 4 one-hot class vector
# Total per hero = 15
NUM_FEATURES = 15 * 2  # two heroes