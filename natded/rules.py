from typing import Set, Dict, Optional
from .ast import *
from .ast import Term, Pred
from .proof import Proof


def structurally_equal(a:Formula,b:Formula)->bool: return a==b

def substitute(formula: Formula, var: str, term: Term) -> Formula:
    if isinstance(formula, Pred):
        new_args = tuple(term if a.name == var and not a.args else a for a in formula.args)
        return Pred(formula.name, new_args)
    if isinstance(formula, Not): return Not(substitute(formula.phi, var, term))
    if isinstance(formula, And): return And(substitute(formula.left, var, term), substitute(formula.right, var, term))
    if isinstance(formula, Or): return Or(substitute(formula.left, var, term), substitute(formula.right, var, term))
    if isinstance(formula, Imp): return Imp(substitute(formula.left, var, term), substitute(formula.right, var, term))
    if isinstance(formula, Iff): return Iff(substitute(formula.left, var, term), substitute(formula.right, var, term))
    if isinstance(formula, ForAll): return ForAll(formula.var, substitute(formula.body, var, term))
    if isinstance(formula, Exists): return Exists(formula.var, substitute(formula.body, var, term))
    return formula

from typing import Set

def extract_terms(fs: Set[Formula]) -> Set[Term]:
    out: Set[Term] = set()

    def rec_term(t: Term):
        out.add(t)
        for a in t.args:
            rec_term(a)

    def rec(f: Formula):
        if isinstance(f, Pred):
            for a in f.args:
                rec_term(a)
        elif isinstance(f, Not):
            rec(f.phi)
        elif isinstance(f, (And, Or, Imp, Iff)):
            rec(f.left); rec(f.right)
        elif isinstance(f, (ForAll, Exists)):
            rec(f.body)
        # Var/Bottom: no terms inside

    for f in fs:
        rec(f)
    return out


def extract_atoms(fs:Set[Formula])->Set[Var]:
    out:set[Var]=set()
    def rec(x:Formula):
        if isinstance(x,Var): out.add(x)
        elif isinstance(x,Not): rec(x.phi)
        elif isinstance(x,(And,Or,Imp,Iff)): rec(x.left); rec(x.right)
        elif isinstance(x,(ForAll,Exists)): rec(x.body)
    for f in fs: rec(f)
    return out

def expand_goal(prem:Set[Formula], goal:Formula, depth:int, cache:Dict)->Optional[Proof]:
    key=(frozenset(prem),goal,depth)
    if key in cache: return cache[key]
    if goal in prem:
        pr=Proof(goal,"Reiteration",[]); cache[key]=pr; return pr
    if depth<=0: cache[key]=None; return None

    # ⊥E
    if any(isinstance(f,Bottom) for f in prem):
        pr=Proof(goal,"⊥E",[Proof(Bottom(),"Premise",[])]); cache[key]=pr; return pr
        # Contraposition: from (P -> Q), infer (~Q -> ~P)
        
    if isinstance(goal, Imp) and isinstance(goal.left, Not) and isinstance(goal.right, Not):
        Q = goal.left.phi
        P = goal.right.phi
        for f in prem:
            if isinstance(f, Imp) and structurally_equal(f.left, P) and structurally_equal(f.right, Q):
                pr = Proof(goal, "Contraposition", [Proof(f, "Premise", [])])
                cache[key] = pr
                return pr

        # Contraposition under ∀
    if isinstance(goal, ForAll) and isinstance(goal.body, Imp):
        body = goal.body
        if isinstance(body.left, Not) and isinstance(body.right, Not):
            Q, P = body.left.phi, body.right.phi
            for f in prem:
                if isinstance(f, ForAll) and isinstance(f.body, Imp):
                    if structurally_equal(f.body.left, P) and structurally_equal(f.body.right, Q):
                        pr = Proof(goal, "Contraposition ∀",
                                   [Proof(f, "Premise", [])])
                        cache[key] = pr
                        return pr


    # ∧I
    if isinstance(goal,And):
        p1=expand_goal(prem,goal.left,depth-1,cache)
        p2=expand_goal(prem,goal.right,depth-1,cache) if p1 else None
        if p1 and p2: pr=Proof(goal,"∧I",[p1,p2]); cache[key]=pr; return pr

    # →I
    if isinstance(goal,Imp):
        A,B=goal.left,goal.right
        sub=expand_goal(prem|{A},B,depth-1,cache)
        if sub: pr=Proof(goal,"→I",[sub],assumptions=(A,)); cache[key]=pr; return pr

    # ¬I
    if isinstance(goal,Not):
        if isinstance(goal.phi, Not):
            A = goal.phi.phi
            pA = expand_goal(prem, A, depth-1, cache)
            if pA:
                pr = Proof(goal, "¬¬I", [pA])
                cache[key] = pr; return pr
        A=goal.phi
        for X in extract_atoms(prem|{goal}):
            px=expand_goal(prem|{A},X,depth-2,cache)
            nx=expand_goal(prem|{A},Not(X),depth-2,cache)
            if px and nx: pr=Proof(goal,"¬I",[px,nx],assumptions=(A,)); cache[key]=pr; return pr

    # ∨I
    if isinstance(goal,Or):
        lp=expand_goal(prem,goal.left,depth-1,cache)
        if lp: pr=Proof(goal,"∨I",[lp]); cache[key]=pr; return pr
        rp=expand_goal(prem,goal.right,depth-1,cache)
        if rp: pr=Proof(goal,"∨I",[rp]); cache[key]=pr; return pr

    # ↔I
    if isinstance(goal,Iff):
        p1=expand_goal(prem,Imp(goal.left,goal.right),depth-1,cache)
        p2=expand_goal(prem,Imp(goal.right,goal.left),depth-1,cache) if p1 else None
        if p1 and p2: pr=Proof(goal,"↔I",[p1,p2]); cache[key]=pr; return pr

    # ∀I
    if isinstance(goal, ForAll):
        fresh = Term(f"c_fresh{len(cache)}")
        sub = expand_goal(prem, substitute(goal.body, goal.var, fresh), depth-1, cache)
        if sub:
            pr = Proof(goal, "∀I", [sub], assumptions=(fresh,))
            cache[key] = pr; return pr

    # ∃I
    if isinstance(goal, Exists):
        # Try any term in the premises
        atoms = extract_terms(prem)
        for t in atoms or [Term("c_witness")]:
            sub = expand_goal(prem, substitute(goal.body, goal.var, t), depth-1, cache)
            if sub:
                pr = Proof(goal, "∃I", [sub])
                cache[key] = pr; return pr


        # ---------- Forward/tactical steps ----------
    # ∀E -> MP toward current goal (instantiate universal to an implication ending in goal, then fire MP)
    candidate_terms = extract_terms(prem | {goal}) or {Term("c_inst")}
    for f in list(prem):
        if isinstance(f, ForAll):
            for t in candidate_terms:
                inst = substitute(f.body, f.var, t)          # e.g., P(t) -> R  or  Q(a) -> R(a)
                if isinstance(inst, Imp) and structurally_equal(inst.right, goal):
                    pA = expand_goal(prem, inst.left, depth-1, cache)
                    if pA:
                        pr_imp = Proof(inst, "∀E", [Proof(f, "Premise", [])])
                        pr = Proof(goal, "→E (MP)", [pr_imp, pA])
                        cache[key] = pr; return pr

    # Direct MP, ∧E, ↔E
    for f in prem:
        if isinstance(f, Imp) and structurally_equal(f.right, goal):
            pa = expand_goal(prem, f.left, depth-1, cache)
            if pa:
                pr = Proof(goal, "→E (MP)", [Proof(f, "Premise", []), pa])
                cache[key] = pr; return pr
        if isinstance(f, And):
            if structurally_equal(f.left, goal):
                pr = Proof(goal, "∧E1", [Proof(f, "Premise", [])])
                cache[key] = pr; return pr
            if structurally_equal(f.right, goal):
                pr = Proof(goal, "∧E2", [Proof(f, "Premise", [])])
                cache[key] = pr; return pr
        if isinstance(f, Iff):
            if structurally_equal(goal, Imp(f.left, f.right)):
                pr = Proof(goal, "↔E", [Proof(f, "Premise", [])])
                cache[key] = pr; return pr
            if structurally_equal(goal, Imp(f.right, f.left)):
                pr = Proof(goal, "↔E", [Proof(f, "Premise", [])])
                cache[key] = pr; return pr

    # ∨E (cases)
    for f in prem:
        if isinstance(f, Or):
            A, B = f.left, f.right
            p1 = expand_goal(prem | {A}, goal, depth-1, cache)
            p2 = expand_goal(prem | {B}, goal, depth-1, cache) if p1 else None
            if p1 and p2:
                pr = Proof(goal, "∨E", [Proof(f, "Premise", []), p1, p2], assumptions=(A, B))
                cache[key] = pr; return pr

    # ∃E (assume witness, prove goal under that assumption)
    for f in prem:
        if isinstance(f, Exists):
            fresh = Term(f"c_exist{len(cache)}")
            witness = substitute(f.body, f.var, fresh)
            sub = expand_goal(prem | {witness}, goal, depth-1, cache)
            if sub:
                pr = Proof(goal, "∃E", [Proof(f, "Premise", []), sub], assumptions=(witness,))
                cache[key] = pr; return pr

    # MT (from P->Q and ~Q infer ~P)
    if isinstance(goal, Not):
        P = goal.phi
        for f in prem:
            if isinstance(f, Imp) and structurally_equal(f.left, P):
                notQ = Not(f.right)
                pNQ = expand_goal(prem, notQ, depth-1, cache)
                if pNQ:
                    pr = Proof(goal, "MT", [Proof(f, "Premise", []), pNQ])
                    cache[key] = pr; return pr

    # ∀E (direct instantiation equals the goal)
    for f in prem:
        if isinstance(f, ForAll):
            for t in (extract_terms(prem | {goal}) or {Term("c_inst")}):
                inst = substitute(f.body, f.var, t)
                if structurally_equal(inst, goal):
                    pr = Proof(goal, "∀E", [Proof(f, "Premise", [])])
                    cache[key] = pr; return pr

    # ∃I (to prove ∃x φ(x), try φ(t) for any seen term t; fallback to fresh)
    if isinstance(goal, Exists):
        for t in (extract_terms(prem | {goal}) or {Term("c_witness")}):
            inst = substitute(goal.body, goal.var, t)
            sub = expand_goal(prem, inst, depth-1, cache)
            if sub:
                pr = Proof(goal, "∃I", [sub])
                cache[key] = pr; return pr

    # ¬E (derive ⊥ from X and ~X)
    if isinstance(goal, Bottom):
        for X in extract_atoms(prem):
            px = expand_goal(prem, X, depth-1, cache)
            nx = expand_goal(prem, Not(X), depth-1, cache)
            if px and nx:
                pr = Proof(goal, "¬E (Contradiction)", [px, nx])
                cache[key] = pr; return pr

    # Double Negation
    if isinstance(goal, Not) and isinstance(goal.phi, Not):
        A = goal.phi.phi
        pA = expand_goal(prem, A, depth-1, cache)
        if pA:
            pr = Proof(goal, "¬¬I", [pA])
            cache[key] = pr; return pr
    else:
        pnnA = expand_goal(prem, Not(Not(goal)), depth-1, cache)
        if pnnA:
            pr = Proof(goal, "¬¬E", [pnnA])
            cache[key] = pr; return pr

    cache[key] = None
    return None

    
