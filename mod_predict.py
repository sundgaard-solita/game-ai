# ----- Prediction -----
import csv
import random
import torch
from mod_globals import ACTIONS, CLASS_LABELS, NUM_FEATURES, STAT_NAMES
from mod_synth_data import SYNTH_DATA_PATH

def predict(model, hero1_stats, hero2_stats):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    half = NUM_FEATURES // 2
    if len(hero1_stats) != half or len(hero2_stats) != half:
        raise ValueError(f"Each hero must have exactly {half} stats.")

    input_features = torch.tensor([hero1_stats + hero2_stats], dtype=torch.float32).to(device)

    model.eval()
    with torch.no_grad():
        output = model(input_features)
        predicted_idx = torch.argmax(output, dim=1).item()
        prediction = ACTIONS[predicted_idx]

    print(f"🔮 Predicted next action: {prediction}")
    return prediction


def predict_random_sample(model):
    with open(SYNTH_DATA_PATH, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        rows = list(reader)
        sample = random.choice(rows)

    half = NUM_FEATURES // 2  # features per hero
    hero1_features = list(map(float, sample[:half]))
    hero2_features = list(map(float, sample[half:NUM_FEATURES]))
    actual_action = sample[NUM_FEATURES]

    predicted_action = predict(model, hero1_features, hero2_features)

    print("🧪 Testing random duel scenario:")
    print(f"  Hero1: {dict(zip(header[:half], hero1_features))}")
    print(f"  Hero2: {dict(zip(header[half:NUM_FEATURES], hero2_features))}")
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
    print(f"  Hero1: {dict(zip(STAT_NAMES, hero1_stats))}")
    print(f"  Hero2: {dict(zip(STAT_NAMES, hero2_stats))}")
    print(f"  ✅ Actual action:    {actual_action}")
    print(f"  🔮 Predicted action: {predicted_action}")

