# tests/test_fol.py
import pytest
from natded.engine import prove_from_strings

def test_forall_elimination_simple():
    # ∀x.P(x) ⊢ P(a)
    proof = prove_from_strings(["∀x.P(x)"], "P(a)")
    h = proof.human()
    assert "∀" in h and "P(a)" in h

def test_exists_introduction_from_instance():
    # P(a) ⊢ ∃x.P(x)
    proof = prove_from_strings(["P(a)"], "∃x.P(x)")
    h = proof.human()
    assert "∃" in h and "P(a)" in h

def test_exists_elim_with_universal_and_mp():
    # ∃x.P(x), ∀x.(P(x) -> R) ⊢ R
    proof = prove_from_strings(["∃x.P(x)", "∀x.(P(x) -> R)"], "R")
    h = proof.human()
    # Should mention ∃ and ∀ steps and reach R
    assert "∃" in h and "∀" in h and h.strip().endswith("R")

def test_universal_chain_to_instance():
    # ∀x.(P(x)->Q(x)), ∀x.(Q(x)->R(x)), P(a) ⊢ R(a)
    premises = ["∀x.(P(x) -> Q(x))", "∀x.(Q(x) -> R(x))", "P(a)"]
    proof = prove_from_strings(premises, "R(a)")
    h = proof.human()
    # Expect two instantiations + two MPs leading to R(a)
    assert "P(a)" in h and "Q(a)" in h and "R(a)" in h

def test_forall_elim_under_negation():
    # ∀x.~R(x) ⊢ ~R(a)
    proof = prove_from_strings(["∀x.~R(x)"], "~R(a)")
    h = proof.human()
    assert "~R(a)" in h
