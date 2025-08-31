# ----- Prediction -----
import csv
import random
import torch
from app_config import CONFIG
from hero import Hero
from synth_data import SYNTH_DATA_PATH

def predict(model, hero1:Hero, hero2:Hero):
    #hero1 = hero1['features'] # TODO Why dont we want the rem_hp, rem_mana, rem_sta here?
    #hero2 = hero2['features'] 
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    half = CONFIG.TOTAL_INPUT_FEATURES // 2
    # Check for missing or additional features
    #ephemeral = {'is_blocking', 'is_dodging', 'is_casting', 'is_using_wand', 'is_using_bow', 'is_resting', 'is_protected', 'is_healing', 'is_attacking'}
    if len(hero1.features) != half or len(hero2.features) != half:
        print(f"\n🚨 Input feature length mismatch")
        print(f"🚨 Each hero must have exactly {half} features (half of TOTAL_INPUT_FEATURES = {CONFIG.TOTAL_INPUT_FEATURES})")
        print(f"🚨 But received lengths: hero1_feats={len(hero1.features)}, hero2_feats={len(hero2.features)}")
        print(f"🚨 Check your feature extraction and constants to ensure consistency.\n")
        raise ValueError(
            f"Input feature length mismatch:\n"
            f"Each hero must have exactly {half} features (half of TOTAL_INPUT_FEATURES = {CONFIG.TOTAL_INPUT_FEATURES}).\n"
            f"But received lengths: hero1_feats={len(hero1.features)}, hero2_feats={len(hero2.features)}.\n"
            f"Check your feature extraction and constants to ensure consistency."
        )


    #input_features = torch.tensor([hero1_feats + hero2_feats], dtype=torch.float32).to(device)
    combined_features = list(hero1.features.values()) + list(hero2.features.values())
    input_features = torch.tensor(combined_features, dtype=torch.float32).to(device)

    model.eval()
    with torch.no_grad():
        output = model(input_features)
        #predicted_idx = torch.argmax(output, dim=1).item()
        predicted_idx = torch.argmax(output).item()

        prediction = CONFIG.ACTIONS[predicted_idx]

    print(f"🔮 Predicted next action: {prediction}")
    return prediction


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

    print("🧪 Testing random duel scenario:")
    print(f"  Hero1: {dict(zip(header[:half], hero1_features))}")
    print(f"  Hero2: {dict(zip(header[half:CONFIG.TOTAL_INPUT_FEATURES], hero2_features))}")
    print(f"  ✅ Actual action:    {actual_action}")
    print(f"  🔮 Predicted action: {predicted_action}")



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

    print("🧪 Testing random duel scenario:")
    print(f"  Hero1: {dict(zip(CONFIG.STAT_NAMES, hero1_stats))}")
    print(f"  Hero2: {dict(zip(CONFIG.STAT_NAMES, hero2_stats))}")
    print(f"  ✅ Actual action:    {actual_action}")
    print(f"  🔮 Predicted action: {predicted_action}")

