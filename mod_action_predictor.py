import torch.nn as nn
from mod_globals import NUM_ACTIONS, NUM_FEATURES

class ActionPredictor(nn.Module):
    def __init__(self, hidden_dim=64):
        super(ActionPredictor, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(NUM_FEATURES, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, NUM_ACTIONS)
        )

    def forward(self, x):
        return self.net(x)

