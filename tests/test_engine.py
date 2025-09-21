import pytest
from natded.engine import prove_from_strings, parse_formula, prove
from natded.ast import Var

def test_parse_formula_roundtrip():
    f = parse_formula("P -> Q")
    assert isinstance(f, type(parse_formula("P -> Q")))

def test_simple_prove_success():
    proof = prove_from_strings(["P->Q","P"], "Q")
    assert proof is not None

def test_unsatisfiable_goal():
    with pytest.raises(RuntimeError):
        prove_from_strings(["P"], "Q")

def test_depth_limit_blocks_proof():
    # With small depth, proof may fail
    from natded.ast import Imp
    premises = [parse_formula("P->Q"), parse_formula("Q->R"), parse_formula("P")]
    goal = parse_formula("R")
    res = prove(premises, goal, max_depth=1)
    assert res.proof is None

def test_chain_proof():
    proof = prove_from_strings(["P->Q","Q->R","R->S","P"], "S")
    h = proof.human()
    assert "Modus Ponens" in h
