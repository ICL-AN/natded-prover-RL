from dataclasses import dataclass
from typing import List, Tuple
from .ast import Formula, fmt

@dataclass
class Proof:
    goal: Formula
    rule: str
    deps: List["Proof"]
    assumptions: Tuple[Formula,...]=()

    def pretty(self, indent=0):
        pad="  "*indent
        asm=f"  [assume {', '.join(fmt(a) for a in self.assumptions)}]" if self.assumptions else ""
        print(f"{pad}{fmt(self.goal)}   ⟵ {self.rule}{asm}")
        for d in self.deps: d.pretty(indent+1)
        return self

    def human(self):
        steps=[]; seen=set()
        def emit(p:"Proof"):
            if id(p) in seen: return
            for d in p.deps: emit(d)
            g=fmt(p.goal)
            if p.rule=="Premise": steps.append(f"Premise: {g}")
            elif p.rule=="Reiteration": steps.append(f"Recall: {g}")
            elif p.rule.startswith("→E"): steps.append(f"From {fmt(p.deps[0].goal)} and {fmt(p.deps[1].goal)}, infer {g} by Modus Ponens")
            elif p.rule=="∧I": steps.append(f"From {fmt(p.deps[0].goal)} and {fmt(p.deps[1].goal)}, conjoin to {g}")
            elif p.rule in("∧E1","∧E2"): steps.append(f"From {fmt(p.deps[0].goal)}, extract {g}")
            elif p.rule=="→I": steps.append(f"Assume {fmt(p.assumptions[0])}, derive {fmt(p.deps[0].goal)}; conclude {g} by →I")
            elif p.rule=="¬I": steps.append(f"Assume {fmt(p.assumptions[0])}, derive contradiction; conclude {g} by ¬I")
            elif p.rule == "¬¬I": steps.append(f"Apply Double Negation Introduction (¬¬I) to conclude {g}")
            elif p.rule == "¬¬E": steps.append(f"Apply Double Negation Elimination (¬¬E) to conclude {g}")
            elif p.rule=="∨I": steps.append(f"Introduce disjunction: from {fmt(p.deps[0].goal)} infer {g}")
            elif p.rule=="∨E": steps.append(f"Case analysis on {fmt(p.deps[0].goal)}; both branches yield {g}")
            elif p.rule=="↔I": steps.append(f"Both directions proven; infer {g} by ↔I")
            elif p.rule=="↔E": steps.append(f"From {fmt(p.deps[0].goal)}, extract {g} by ↔E")
            elif p.rule=="⊥E": steps.append(f"From ⊥, infer {g}")
            elif p.rule=="¬E (Contradiction)": steps.append(f"From {fmt(p.deps[0].goal)} and {fmt(p.deps[1].goal)}, derive ⊥")
            elif p.rule=="MT": steps.append(f"From {fmt(p.deps[0].goal)} and {fmt(p.deps[1].goal)}, infer {g} by Modus Tollens")
            elif p.rule == "∀E": steps.append(f"Instantiate ∀ with term to get {g}.")
            elif p.rule == "∀I": steps.append(f"Let {fmt(p.assumptions[0])} be arbitrary; generalize to {g}.")
            elif p.rule == "∃I": steps.append(f"From {fmt(p.deps[0].goal)}, introduce ∃ to get {g}.")
            elif p.rule == "∃E": steps.append(f"From ∃ premise, assume {fmt(p.assumptions[0])} witness; derive {g}.")
            else: steps.append(f"{g} by {p.rule}")
            seen.add(id(p))
        emit(self)

        # add a final line that ends exactly with the goal (no trailing period)
        if steps and not steps[-1].rstrip().endswith(fmt(self.goal)):
            steps.append(f"Therefore, {fmt(self.goal)}")

        return "\n".join(f"Step {i+1}. {s}" for i, s in enumerate(steps))
