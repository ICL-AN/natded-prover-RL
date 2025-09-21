import pytest
from natded.engine import prove_from_strings

def test_human_linear_steps():
    proof = prove_from_strings(["P->Q","P"], "Q")
    h = proof.human().splitlines()
    assert h[0].startswith("Step 1.") and any("Modus Ponens" in line for line in h)

def test_pretty_tree_structure(capsys):
    proof = prove_from_strings(["P->Q","P"], "Q")
    proof.pretty()
    out = capsys.readouterr().out
    assert "⟵ →E" in out

def test_double_negation_intro_elim():
    proof = prove_from_strings(["P"], "~~P")
    assert "Double Negation" in proof.human()

def test_bottom_elim():
    proof = prove_from_strings(["⊥"], "R")
    assert "⊥" in proof.human()

def test_biconditional_intro():
    proof = prove_from_strings(["P->Q","Q->P"], "P<->Q")
    assert "↔I" in proof.human()
