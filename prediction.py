from dataclasses import dataclass

@dataclass
class CombatPrediction:
    action_index: int
    action_name: str
    action_scores: int