#!/usr/bin/env python3
# bin/natded_run.py
from __future__ import annotations
import argparse, sys
from natded.engine import parse_formula, prove
from natded.moves import State
from ai.policy import RandomPolicy, HeuristicPolicy, MLPPolicy
from ai.beam import beam_search
from ai.mcts import mcts_search

def main():
    ap = argparse.ArgumentParser(description="Run AI-guided search for natded")
    ap.add_argument("--prem", nargs="+", required=True, help='Premises, e.g. "P->Q" "P"')
    ap.add_argument("--goal", required=True, help='Goal, e.g. "Q"')
    ap.add_argument("--strategy", choices=["dfs", "beam", "mcts"], default="dfs")
    ap.add_argument("--policy", choices=["random", "heur", "mlp"], default="heur")
    ap.add_argument("--beam-width", type=int, default=8)
    ap.add_argument("--max-steps", type=int, default=200)
    ap.add_argument("--c-puct", type=float, default=1.4)
    ap.add_argument("--sims", type=int, default=256)
    ap.add_argument("--mlp-bias", type=float, default=0.1)
    ap.add_argument("--mlp-jaccard", type=float, default=1.0)
    ap.add_argument("--depth", type=int, default=6, help="final exact prove() depth to confirm")

    args = ap.parse_args()

    premises = tuple(parse_formula(p) for p in args.prem)
    goal = parse_formula(args.goal)
    state = State(premises=premises, goal=goal)

    if args.policy == "random":
        pol = RandomPolicy()
    elif args.policy == "mlp":
        pol = MLPPolicy(w_bias=args.mlp_bias, w_jaccard=args.mlp_jaccard)
    else:
        pol = HeuristicPolicy()

    if args.strategy == "dfs":
        res = prove(list(premises), goal, max_depth=args.depth)
        print(res.proof.human() if res.proof else "No proof found.")
        sys.exit(0)

    if args.strategy == "beam":
        st = beam_search(state, policy=pol, beam_width=args.beam_width, max_steps=args.max_steps)
        if not st:
            print("Beam failed to reach a provable state.")
            sys.exit(1)
        print(f"[beam] enriched premises: {len(st.premises)}; trying exact solve...")
        res = prove(list(st.premises), goal, max_depth=args.depth)
        print(res.proof.human() if res.proof else "No proof found at final step.")
        sys.exit(0)

    if args.strategy == "mcts":
        st = mcts_search(state, policy=pol, c_puct=args.c_puct, simulations=args.sims)
        if not st:
            print("MCTS failed to suggest a promising state.")
            sys.exit(1)
        print(f"[mcts] enriched premises: {len(st.premises)}; trying exact solve...")
        res = prove(list(st.premises), goal, max_depth=args.depth)
        print(res.proof.human() if res.proof else "No proof found at final step.")
        sys.exit(0)

if __name__ == "__main__":
    main()
