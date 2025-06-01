import torch
import torch.nn as nn
from safetensors.torch import save_file
import os
import datetime
from mod_action_predictor import ActionPredictor
from mod_globals import ACTIONS, MODEL_DIR, MODEL_PATH

def train_ai_model(
    data,
    epochs=10000,
    hidden_dim=64,
    lr=0.00005, #0.0003,
    optimizer_type="adamw"
):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"🤖 Training on {device.upper()} using {optimizer_type.upper()} (lr={lr}, epochs={epochs})...")

    # Define model dynamically with chosen hidden size

    model = ActionPredictor(hidden_dim=hidden_dim).to(device)
    criterion = nn.CrossEntropyLoss()

    if optimizer_type.lower() == "adamw":
        optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    else:
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    inputs = torch.tensor([d[0] for d in data], dtype=torch.float32).to(device)

    # Map action string to index
    label_map = {a: i for i, a in enumerate(ACTIONS)}
    targets = torch.tensor([label_map[d[1]] for d in data], dtype=torch.long).to(device)

    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 50 == 0 or epoch == 0:
            print(f"  🔁 Epoch {epoch + 1}/{epochs} | Loss: {loss.item():.4f}")

    print("✅ AI model trained!")

    os.makedirs(MODEL_DIR, exist_ok=True)
    state_dict = model.state_dict()
    save_file({k: v for k, v in state_dict.items()}, MODEL_PATH)

    date_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    backup_path = os.path.join(MODEL_DIR, f'gameai_{date_stamp}.safetensor')
    save_file({k: v for k, v in state_dict.items()}, backup_path)

    print(f"💾 Model saved as {MODEL_PATH} and backup created.")
    return model
