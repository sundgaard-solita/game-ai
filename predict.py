# ----- Prediction -----
import csv
import random
import torch
from app_config import CONFIG
from hero import Hero
from prediction import CombatPrediction
from synth_data import SYNTH_DATA_PATH
from app_logger import logger

def predict(model, hero1: Hero, hero2: Hero)->CombatPrediction:
    """
    Decide the next action for hero1 against hero2.

    Returns:
      - action_index: int (0-8) → which slot in CONFIG.ACTIONS
      - action_name: str → human-readable action name
      - action_scores: tensor of length 9 → raw scores for all actions
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # ✅ Each hero must provide exactly half the features
    half = CONFIG.TOTAL_INPUT_FEATURES // 2
    if len(hero1.features) != half or len(hero2.features) != half:
        raise ValueError(
            f"🚨 Feature length mismatch! hero1={len(hero1.features)}, "
            f"hero2={len(hero2.features)}, expected each={half}"
        )

    # 🧮 Collect all features: hero1 + hero2 → ~46 numbers
    all_features = list(hero1.features.values()) + list(hero2.features.values())

    # 🔢 Turn into a 2D matrix [1, 46] → one row, 46 columns
    features_matrix = torch.tensor(all_features, dtype=torch.float32).unsqueeze(0).to(device)

    # 🧠 Model forward pass
    # input [1,46] → output [1,9] (scores for 9 possible actions)
    model.eval()
    action_scores_batch = None
    if CONFIG.TRAINING_MODE:
        # keep training trail → allows loss.backward()
        action_scores_batch = model(features_matrix)
    else:
        # faster, less memory → but no training possible
        with torch.no_grad():
            action_scores_batch = model(features_matrix)
    action_scores_batch = model(features_matrix)  # shape [1, 9]
    action_scores = action_scores_batch[0]        # shape [9], drop batch dimension
    predicted_action_index = torch.argmax(action_scores).item()  # int 0–8
    predicted_action_name = CONFIG.ACTIONS[predicted_action_index]         # string label

    logger.debug(f"🔮 Predicted next action: {predicted_action_name}")
    return CombatPrediction(action_index=predicted_action_index, action_name=predicted_action_name, action_scores=action_scores)


def predict_random_sample(model):
    with open(SYNTH_DATA_PATH, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        rows = list(reader)
        sample = random.choice(rows)

    half = CONFIG.TOTAL_INPUT_FEATURES // 2  # features per hero
    hero1_features = list(map(float, sample[:half]))
    hero2_features = list(map(float, sample[half:CONFIG.TOTAL_INPUT_FEATURES]))
    actual_action = sample[CONFIG.TOTAL_INPUT_FEATURES]

    predicted_action = predict(model, hero1_features, hero2_features)

    logger.debug("🧪 Testing random duel scenario:")
    logger.debug(f"  Hero1: {dict(zip(header[:half], hero1_features))}")
    logger.debug(f"  Hero2: {dict(zip(header[half:CONFIG.TOTAL_INPUT_FEATURES], hero2_features))}")
    logger.debug(f"  ✅ Actual action:    {actual_action}")
    logger.debug(f"  🔮 Predicted action: {predicted_action}")



def predict_random_sample2(model):
    with open(SYNTH_DATA_PATH, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Skip header
        rows = list(reader)
        sample = random.choice(rows)

    # Changed from int to float here:
    hero1_stats = list(map(float, sample[:9]))
    hero2_stats = list(map(float, sample[9:18]))
    actual_action = sample[18]

    predicted_action = predict(model, hero1_stats, hero2_stats)

    logger.debug("🧪 Testing random duel scenario:")
    logger.debug(f"  Hero1: {dict(zip(CONFIG.STAT_NAMES, hero1_stats))}")
    logger.debug(f"  Hero2: {dict(zip(CONFIG.STAT_NAMES, hero2_stats))}")
    logger.debug(f"  ✅ Actual action:    {actual_action}")
    logger.debug(f"  🔮 Predicted action: {predicted_action}")

