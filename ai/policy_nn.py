# ai/policy_nn.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class PolicyMLP(nn.Module):
    """
    Simple feedforward policy network.
    Input: feature vector of proof state
    Output: probabilities over possible actions (rules to apply)
    """
    def __init__(self, input_dim: int, hidden_dim: int, num_actions: int):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.out = nn.Linear(hidden_dim, num_actions)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return F.log_softmax(self.out(x), dim=-1)


def dummy_features(proof_state) -> torch.Tensor:
    """
    Convert a proof state into a toy feature vector.
    Currently counts how many of each connective type exist.
    """
    counts = {
        "var": 0, "not": 0, "and": 0, "or": 0,
        "imp": 0, "iff": 0, "forall": 0, "exists": 0
    }
    def walk(f):
        if f.__class__.__name__.lower() in counts:
            counts[f.__class__.__name__.lower()] += 1
        for sub in getattr(f, "__dict__", {}).values():
            if hasattr(sub, "__dict__"):
                walk(sub)
            elif isinstance(sub, (list, tuple)):
                for s in sub:
                    if hasattr(s, "__dict__"):
                        walk(s)
    walk(proof_state)
    return torch.tensor(list(counts.values()), dtype=torch.float32)


def pick_action(model: PolicyMLP, proof_state, action_space):
    """
    Given a model and a state, return an action index.
    """
    feats = dummy_features(proof_state).unsqueeze(0)
    with torch.no_grad():
        log_probs = model(feats)
    probs = torch.exp(log_probs).squeeze(0)
    action_idx = torch.multinomial(probs, num_samples=1).item()
    return action_space[action_idx], probs[action_idx].item()
