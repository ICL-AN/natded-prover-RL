# ai/heuristics.py
from __future__ import annotations
from typing import Set, Iterable, Tuple
from natded.ast import Formula, Var, Pred, And, Or, Imp, Iff, Not, ForAll, Exists

def symbols(f: Formula) -> Set[str]:
    out: Set[str] = set()
    def rec(x: Formula):
        
        if isinstance(x, Var): out.add(x.name)
        elif isinstance(x, Pred):
            out.add(x.name)
            for a in x.args: out.add(a.name)
        elif isinstance(x, (And, Or, Imp, Iff)): rec(x.left); rec(x.right)
        elif isinstance(x, Not): rec(x.phi)
        elif isinstance(x, (ForAll, Exists)): out.add(x.var); rec(x.body)
    rec(f)
    return out

def jaccard(a: Formula, b: Formula) -> float:
    A, B = symbols(a), symbols(b)
    if not A and not B: return 0.0
    inter = len(A & B); union = len(A | B)
    return inter / union

def move_score(goal: Formula, added: Iterable[Formula]) -> float:
    # Score a move by max Jaccard overlap of its added facts with the goal
    vals = [jaccard(goal, f) for f in added]
    return max(vals) if vals else 0.0
