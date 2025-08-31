import torch.nn as nn

from app_config import CONFIG

print(f"[DEBUG] TOTAL_INPUT_FEATURES in model: {CONFIG.TOTAL_INPUT_FEATURES}")
print(f"[DEBUG] NUM_ACTIONS in model: {CONFIG.NUM_ACTIONS}")

class ActionPredictor(nn.Module):
    def __init__(self, total_num_of_feature=CONFIG.TOTAL_INPUT_FEATURES, hidden_dim=64):
        super(ActionPredictor, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(total_num_of_feature, hidden_dim),  # use imported constant
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, CONFIG.NUM_ACTIONS)            # use imported constant
        )

    def forward(self, x):
        return self.net(x)


