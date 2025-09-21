#!/usr/bin/env python3
import time, csv
from natded.engine import prove_from_strings

# Harder benchmark problems
BENCH_PROBLEMS = [
    # Contraposition
    (["P->Q"], "(~Q)->(~P)"),

    # Double negation to positive
    (["~~P"], "P"),

    # Syllogism with universals
    (["∀x.(P(x)->Q(x))", "∀x.(Q(x)->R(x))", "P(a)"], "R(a)"),

    # Existential + universal combination
    (["∃x.P(x)", "∀x.(P(x)->R(x))"], "∃x.R(x)"),

    # Nested implication
    (["(P->Q)", "(Q->R)", "(R->S)", "P"], "S"),

    # Law of excluded middle (LEM) as lemma
    ([], "P | ~P"),
]

STRATEGIES = [
    ("dfs", {"policy": "heur", "params": {}}),
    ("beam", {"policy": "heur", "params": {"beam_width": 8, "max_steps": 500}}),
    ("mcts", {"policy": "heur", "params": {"c_puct": 1.4, "sims": 800, "use_rave": False}}),
    ("mcts", {"policy": "heur", "params": {"c_puct": 1.4, "sims": 800, "use_rave": True, "rave_b": 100.0}}),
]

def run():
    with open("results2.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["strategy","policy","params","problem","success","time_s"])
        for strat, meta in STRATEGIES:
            for premises, goal in BENCH_PROBLEMS:
                problem_str = f"{premises} ⊢ {goal}"
                start = time.time()
                success = 0
                try:
                    _ = prove_from_strings(premises, goal)
                    success = 1
                except Exception:
                    success = 0
                elapsed = time.time() - start
                writer.writerow([strat, meta["policy"], meta["params"], problem_str, success, f"{elapsed:.4f}"])
                print(f"{strat} {problem_str} -> {success} in {elapsed:.4f}s")

if __name__ == "__main__":
    run()
