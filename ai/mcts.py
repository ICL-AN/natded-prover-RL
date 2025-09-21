# ai/mcts.py
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set

from natded.engine import prove
from natded.moves import State, Move, successors
from .policy import Policy, HeuristicPolicy

@dataclass
class EdgeStats:
    # standard stats
    N: int = 0
    W: float = 0.0
    Q: float = 0.0
    P: float = 0.0
    # RAVE / AMAF stats
    Nr: int = 0
    Wr: float = 0.0
    Qr: float = 0.0

@dataclass
class Node:
    state: State
    prior: float = 1.0
    # key is move_key (tuple of added premises as strings)
    edges: Dict[Tuple[str, ...], EdgeStats] = field(default_factory=dict)
    children: Dict[Tuple[str, ...], "Node"] = field(default_factory=dict)
    N: int = 0
    is_terminal: Optional[bool] = None

def quick_value(state: State) -> float:
    # shallow exact check
    res = prove(list(state.premises), state.goal, max_depth=4)
    return 1.0 if res.proof else 0.0

def move_key(m: Move) -> Tuple[str, ...]:
    return tuple(sorted(map(str, m.add_premises)))

def puct_score(N_parent: int, est: EdgeStats, c_puct: float, use_rave: bool, rave_b: float) -> float:
    # blend Q with RAVE early if enabled
    if use_rave:
        beta = rave_b / (est.N + rave_b)
        Qeff = beta * est.Qr + (1.0 - beta) * est.Q
    else:
        Qeff = est.Q
    U = c_puct * est.P * math.sqrt(max(1, N_parent)) / (1 + est.N)
    return Qeff + U

def mcts_search(
    initial: State,
    policy: Optional[Policy] = None,
    c_puct: float = 1.4,
    simulations: int = 256,
    use_rave: bool = False,
    rave_b: float = 100.0
):
    pol = policy or HeuristicPolicy()
    root = Node(state=initial)

    # init root edges
    root_moves = successors(initial)
    priors = pol.scores(initial, root_moves)
    for m, p in zip(root_moves, priors):
        root.edges[move_key(m)] = EdgeStats(P=p)

    def simulate():
        node = root
        path: List[Tuple[Node, Tuple[str, ...]]] = []  # (node, move_key)
        played_keys: Set[Tuple[str, ...]] = set()

        # SELECTION / EXPANSION
        while True:
            if node.is_terminal is None:
                node.is_terminal = bool(quick_value(node.state))
            if node.is_terminal:
                v = 1.0
                break

            if not node.edges:
                # expand
                ms = successors(node.state)
                if not ms:
                    v = 0.0
                    node.is_terminal = False
                    break
                pri = pol.scores(node.state, ms)
                for m, p in zip(ms, pri):
                    node.edges[move_key(m)] = EdgeStats(P=p)

            # pick best by PUCT
            best_k, best_s = None, -1e9
            for k, est in node.edges.items():
                s = puct_score(node.N, est, c_puct, use_rave, rave_b)
                if s > best_s:
                    best_s, best_k = s, k
            akey = best_k
            path.append((node, akey))
            played_keys.add(akey)

            # child state build
            # reconstruct move from key
            ms = successors(node.state)
            chosen = None
            for m in ms:
                if move_key(m) == akey:
                    chosen = m; break
            child_state = State(premises=tuple(set(node.state.premises)|set(chosen.add_premises)),
                                goal=node.state.goal)

            child = node.children.get(akey)
            if child is None:
                child = Node(state=child_state, prior=node.edges[akey].P)
                node.children[akey] = child
                v = quick_value(child_state)  # one-step rollout
                break
            else:
                node = child

        # BACKPROP (+ RAVE)
        for n, k in path:
            es = n.edges[k]
            es.N += 1
            es.W += v
            es.Q = es.W / es.N
            n.N += 1
            if use_rave:
                # AMAF: update all edges whose move-key appeared later in the playout
                for rk, rs in n.edges.items():
                    if rk in played_keys:
                        rs.Nr += 1
                        rs.Wr += v
                        rs.Qr = rs.Wr / max(1, rs.Nr)

    for _ in range(simulations):
        simulate()

    if not root.edges:
        return None

    # pick best child by visits
    best_k = max(root.edges.items(), key=lambda kv: kv[1].N)[0]
    # reconstruct best move and state
    ms = successors(initial)
    chosen = None
    for m in ms:
        if move_key(m) == best_k:
            chosen = m; break
    best_state = State(premises=tuple(set(initial.premises)|set(chosen.add_premises)),
                       goal=initial.goal)
    return best_state
