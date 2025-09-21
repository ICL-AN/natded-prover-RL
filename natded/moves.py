# natded/moves.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Set, Tuple

from .ast import Formula, And, Or, Imp, Not, Iff, ForAll, Exists, Bottom, Var, Pred, Term
from .rules import substitute, extract_terms, structurally_equal
from .engine import parse_formula  # optional use

@dataclass(frozen=True)
class State:
    premises: Tuple[Formula, ...]
    goal: Formula

@dataclass(frozen=True)
class Move:
    name: str
    detail: str
    add_premises: Tuple[Formula, ...] = ()
    # For ∃E or case-splits we could add obligations; we keep it simple for now.

def symbol_set(f: Formula) -> Set[str]:
    """Collect symbol names (vars/preds) to support heuristics."""
    out: Set[str] = set()
    def rec(x: Formula):
        if isinstance(x, Var):
            out.add(x.name)
        elif isinstance(x, Pred):
            out.add(x.name)
            for a in x.args: out.add(a.name)
        elif isinstance(x, (And, Or, Imp, Iff)):
            rec(x.left); rec(x.right)
        elif isinstance(x, Not):
            rec(x.phi)
        elif isinstance(x, (ForAll, Exists)):
            out.add(x.var); rec(x.body)
    rec(f)
    return out

def successors(state: State) -> List[Move]:
    """Suggest simple forward moves that enrich premises and may enable the goal."""
    prem: Tuple[Formula, ...] = state.premises
    goal = state.goal
    out: List[Move] = []

    # 1) Direct helpers: ∧E
    for f in prem:
        if isinstance(f, And):
            out.append(Move("∧E1", f"extract left of {f}", add_premises=(f.left,)))
            out.append(Move("∧E2", f"extract right of {f}", add_premises=(f.right,)))

    # 2) ∀E instantiation: try terms seen or fresh
    terms = extract_terms(set(prem) | {goal}) or {Term("c_inst")}
    for f in prem:
        if isinstance(f, ForAll):
            for t in terms:
                inst = substitute(f.body, f.var, t)
                out.append(Move("∀E", f"instantiate {f} with {t.name}", add_premises=(inst,)))

    # 3) ↔E split into two implications (helpful for later MP)
    for f in prem:
        if isinstance(f, Iff):
            out.append(Move("↔E", "extract →", add_premises=(Imp(f.left, f.right),)))
            out.append(Move("↔E", "extract ←", add_premises=(Imp(f.right, f.left),)))

    # 4) MP opportunity helper: if we have A and (A->B), add B
    imps = [f for f in prem if isinstance(f, Imp)]
    for imp in imps:
        for a in prem:
            if structurally_equal(a, imp.left):
                out.append(Move("→E (MP)", f"from {a} and {imp}", add_premises=(imp.right,)))

    # 5) Simple disjunction helper: from X derive (X|Y) (∨I) using goal symbols to create Y
    # (This is optional and conservative.)
    gsyms = symbol_set(goal)
    for f in prem:
        # If goal is an Or, creating it exactly is hard; we skip generative Or for safety.

        # nothing added here intentionally to keep successors compact
        pass

    # Deduplicate moves by the add_premises set
    unique = []
    seen: Set[Tuple[Formula, ...]] = set()
    for m in out:
        key = tuple(sorted(m.add_premises, key=str))
        if key not in seen:
            seen.add(key); unique.append(m)
    return unique
