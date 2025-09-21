#!/usr/bin/env python3
from __future__ import annotations
import time, itertools, statistics as stats
from typing import List, Tuple
from natded.engine import parse_formula, prove
from natded.moves import State
from ai.policy import RandomPolicy, HeuristicPolicy, MLPPolicy
from ai.beam import beam_search
from ai.mcts import mcts_search

PROBLEMS: List[Tuple[List[str], str]] = [
    (["P->Q","P"], "Q"),
    (["P->Q","Q->R","P"], "R"),
    (["∀x.(P(x)->Q(x))","∀x.(Q(x)->R(x))","P(a)"], "R(a)"),
    (["∃x.P(x)","∀x.(P(x)->R)"], "R"),
]

def run_once(strategy: str, policy_name: str, params: dict, prem: List[str], goal: str, final_depth: int=6):
    premises = tuple(parse_formula(p) for p in prem)
    g = parse_formula(goal)
    state = State(premises=premises, goal=g)

    if policy_name == "random": pol = RandomPolicy()
    elif policy_name == "mlp": pol = MLPPolicy(w_bias=params.get("mlp_bias",0.1), w_jaccard=params.get("mlp_jaccard",1.0))
    else: pol = HeuristicPolicy()

    t0 = time.time()
    proof_found = False
    if strategy == "dfs":
        res = prove(list(premises), g, max_depth=final_depth)
        proof_found = res.proof is not None
    elif strategy == "beam":
        st = beam_search(state, policy=pol, beam_width=params.get("beam_width",8), max_steps=params.get("max_steps",200))
        if st:
            res = prove(list(st.premises), g, max_depth=final_depth)
            proof_found = res.proof is not None
    elif strategy == "mcts":
        st = mcts_search(
            state, policy=pol,
            c_puct=params.get("c_puct",1.4),
            simulations=params.get("sims",256),
            use_rave=params.get("use_rave",False),
            rave_b=params.get("rave_b",100.0),
        )
        if st:
            res = prove(list(st.premises), g, max_depth=final_depth)
            proof_found = res.proof is not None
    dt = time.time() - t0
    return proof_found, dt

def main():
    strategies = ["dfs","beam","mcts"]
    policies = ["heur","random","mlp"]

    grid = []
    # Beam grid
    for bw in [4,8,16]:
        grid.append(("beam","heur",{"beam_width":bw,"max_steps":200}))
    # MCTS grid
    for cp in [0.8,1.4,2.0]:
        for sims in [200,400,800]:
            grid.append(("mcts","heur",{"c_puct":cp,"sims":sims,"use_rave":False}))
            grid.append(("mcts","heur",{"c_puct":cp,"sims":sims,"use_rave":True,"rave_b":100.0}))
    # Baseline DFS
    grid.append(("dfs","heur",{}))

    print("strategy,policy,params,problem,success,time_s")
    for (prem, goal) in PROBLEMS:
        pname = f"{prem} ⊢ {goal}"
        for (strat, pol, params) in grid:
            ok, t = run_once(strat, pol, params, prem, goal)
            print(f"{strat},{pol},{params},{pname},{int(ok)},{t:.4f}")

if __name__ == "__main__":
    main()
