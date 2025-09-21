# ai/policy.py
from __future__ import annotations
import math, random
from typing import List, Tuple
from natded.ast import Formula
from natded.moves import Move, State
from .heuristics import move_score

class Policy:
    def scores(self, state: State, moves: List[Move]) -> List[float]:
        raise NotImplementedError

class RandomPolicy(Policy):
    def scores(self, state: State, moves: List[Move]) -> List[float]:
        return [random.random() for _ in moves]

class HeuristicPolicy(Policy):
    def scores(self, state: State, moves: List[Move]) -> List[float]:
        return [move_score(state.goal, m.add_premises) for m in moves]

class MLPPolicy(Policy):
    """Tiny stub: linear over two features (bias + max-jaccard)."""
    def __init__(self, w_bias: float = 0.1, w_jaccard: float = 1.0, temperature: float = 1.0):
        self.wb = w_bias; self.wj = w_jaccard; self.tau = max(1e-6, temperature)

    def scores(self, state: State, moves: List[Move]) -> List[float]:
        raw = [self.wb + self.wj * move_score(state.goal, m.add_premises) for m in moves]
        # softmax to [0,1]
        mx = max(raw) if raw else 0.0
        exps = [math.exp((r - mx)/self.tau) for r in raw]
        s = sum(exps) or 1.0
        return [e/s for e in exps]
