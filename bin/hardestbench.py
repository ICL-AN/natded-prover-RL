
import time, csv
from natded.engine import prove_from_strings
from natded.export import proof_to_latex


# Some monster problems
problems = [
    # 1. Multi-hop quantified chain: ∀x.(P(x)->Q(x)), ∀x.(Q(x)->R(x)), ∀x.(R(x)->S(x)), P(a) ⊢ S(a)
    (["∀x.(P(x)->Q(x))", "∀x.(Q(x)->R(x))", "∀x.(R(x)->S(x))", "P(a)"], "S(a)"),

    # 2. Existential-universal mix: ∃x.P(x), ∀x.(P(x)->Q(x)), ∀x.(Q(x)->R(x)) ⊢ ∃x.R(x)
    (["∃x.P(x)", "∀x.(P(x)->Q(x))", "∀x.(Q(x)->R(x))"], "∃x.R(x)"),

    # 3. Nested connectives: (P->Q) & (Q->R) & (R->S) & (S->T), P ⊢ T
    (["(P->Q)", "(Q->R)", "(R->S)", "(S->T)", "P"], "T"),

    # 4. Quantified contraposition stress: ∀x.(P(x)->Q(x)) ⊢ ∀x.(~Q(x)->~P(x))
    (["∀x.(P(x)->Q(x))"], "∀x.(~Q(x)->~P(x))"),
]

strategies = [
    ("dfs", {}, {}),
    ("beam", {"beam_width": 16, "max_steps": 1000}, {}),
    ("mcts", {"c_puct": 1.4, "sims": 2000, "use_rave": True, "rave_b": 300.0}, {}),
]

with open("results_hardest.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["strategy","params","premises","goal","success","time_s"])
    for premises, goal in problems:
        for strat, params, extra in strategies:
            start = time.time()
            try:
                proof = prove_from_strings(premises, goal, depth=12)
                success = 1 if proof else 0
            except Exception:
                success = 0
            elapsed = time.time()-start
            writer.writerow([strat, params, premises, goal, success, f"{elapsed:.4f}"])
            print(f"{strat} {premises} ⊢ {goal} -> {success} in {elapsed:.4f}s")

            if proof:
                tex = proof_to_latex(proof)
                fname = f"proof_{strat}_{goal.replace(' ','').replace('(','').replace(')','')}.tex"
                with open(fname, "w") as f2:
                    f2.write(tex)