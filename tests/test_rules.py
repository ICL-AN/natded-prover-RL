import pytest
from natded.engine import prove_from_strings

def test_and_elimination():
    proof = prove_from_strings(["P & Q"], "P")
    assert "Premise: (P & Q)" in proof.human()
    assert "extract P" in proof.human()

def test_and_introduction():
    proof = prove_from_strings(["P","Q"], "P & Q")
    h = proof.human()
    assert "conjoin" in h and "(P & Q)" in h

def test_or_introduction():
    proof = prove_from_strings(["P"], "P | R")
    assert "Introduce disjunction" in proof.human()

def test_or_elimination():
    proof = prove_from_strings(["P|Q","P->R","Q->R"], "R")
    assert "Case analysis" in proof.human()

def test_modus_tollens():
    proof = prove_from_strings(["P->Q","~Q"], "~P")
    assert "Modus Tollens" in proof.human()
