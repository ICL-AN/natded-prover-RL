# ai/beam.py
from __future__ import annotations
import heapq
from dataclasses import dataclass
from typing import List, Tuple, Optional

from natded.engine import prove
from natded.moves import State, Move, successors
from .policy import Policy, HeuristicPolicy

@dataclass
class BeamNode:
    neg_score: float
    state: State
    depth: int

def is_goal(state: State) -> bool:
    # quick check: try proving with small depth using your core engine
    res = prove(list(state.premises), state.goal, max_depth=4)
    return res.proof is not None

def beam_search(initial: State, policy: Optional[Policy] = None, beam_width: int = 8, max_steps: int = 200):
    pol = policy or HeuristicPolicy()
    beam: List[BeamNode] = [BeamNode(neg_score=0.0, state=initial, depth=0)]
    heapq.heapify(beam)

    visited = set()

    for _ in range(max_steps):
        if not beam: break
        next_frontier: List[BeamNode] = []

        # expand up to beam_width nodes
        cur_level = [heapq.heappop(beam) for _ in range(min(beam_width, len(beam)))]
        for node in cur_level:
            st = node.state
            key = (tuple(sorted(map(str, st.premises))), str(st.goal))
            if key in visited: continue
            visited.add(key)

            if is_goal(st):
                return st  # found a state that your engine can complete quickly

            moves = successors(st)
            if not moves: continue
            scores = pol.scores(st, moves)

            # push children scored by policy
            for m, s in zip(moves, scores):
                child = State(premises=tuple(set(st.premises) | set(m.add_premises)),
                              goal=st.goal)
                next_frontier.append(BeamNode(neg_score=-s, state=child, depth=node.depth+1))

        # keep top-k
        next_frontier.sort(key=lambda n: n.neg_score)
        beam = next_frontier[:beam_width]
        heapq.heapify(beam)

    return None  # not found within limits
