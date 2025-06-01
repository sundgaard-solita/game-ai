import os
import random
import torch
from safetensors.torch import load_file
from mod_action_predictor import ActionPredictor
from mod_globals import MODEL_PATH
from mod_play_game import play_game
from mod_predict import predict_random_sample
from mod_synth_data import create_synthetic_data, load_synthetic_data
from mod_train_model import train_ai_model

# ----- Model Loading -----
def load_model(hidden_dim=64):
    if not os.path.exists(MODEL_PATH):
        print("⚠️ No trained model found. Train one first.")
        return None

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ActionPredictor(hidden_dim=hidden_dim).to(device)
    weights = load_file(MODEL_PATH)
    model.load_state_dict(weights)
    model.eval()
    print("📂 Model loaded successfully.")
    return model

# ----- System Info -----
def check_cuda():
    print("🔍 Torch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))
    else:
        print("Running on CPU")


# ----- Main Menu -----
def main():
    model = None

    while True:
        print("\n🌟 DND Heroes League Menu 🌟")
        print("1. Play Game")
        print("2. Create Synthetic Data")
        print("3. Train AI Model")
        print("4. Predict Hero Action")
        print("5. Check CUDA")
        print("9. Exit")
        choice = input("Choose an option (1-9): ").strip()

        if choice == '1':
            model = model or load_model(hidden_dim=128)
            play_game(model)

        elif choice == '2':
            force = input("Force regenerate data? (y/N): ").strip().lower() == 'y'
            create_synthetic_data(num_samples=5000, force_regenerate=force)

        elif choice == '3':
            data = load_synthetic_data()
            if data:
                model = train_ai_model(data, epochs=15000, hidden_dim=128, lr=1e-3, optimizer_type="adamw")

        elif choice == '4':
            model = model or load_model(hidden_dim=128)
            if model:
                predict_random_sample(model)
            else:
                print("Please train or load the AI model first.")
        elif choice == '5':
            check_cuda()

        elif choice == '9':
            print("👋 Goodbye!")
            break

        else:
            print("❗ Invalid option.")

# ----- Entry -----
if __name__ == "__main__":
    main()
