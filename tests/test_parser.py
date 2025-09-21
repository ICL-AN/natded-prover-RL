import pytest
from natded.parser import parse_formula
from natded.ast import Var, And, Or, Imp, Not, Iff, Bottom, ForAll, Exists, fmt

def test_parse_simple_var():
    f = parse_formula("P")
    assert isinstance(f, Var) and f.name == "P"

def test_parse_and_or_precedence():
    f = parse_formula("P & Q | R")
    # should parse as (P & Q) | R
    assert isinstance(f, Or)
    assert isinstance(f.left, And)

def test_parse_implication_assoc():
    f = parse_formula("P -> Q -> R")
    # right-assoc: P -> (Q -> R)
    assert isinstance(f, Imp)
    assert isinstance(f.right, Imp)

def test_parse_biconditional():
    f = parse_formula("P <-> Q")
    assert isinstance(f, Iff)
    assert fmt(f) == "(P <-> Q)"

def test_parse_bottom_and_quantifiers():
    f1 = parse_formula("⊥")
    f2 = parse_formula("∀x.P")
    f3 = parse_formula("∃y.Q")
    assert isinstance(f1, Bottom)
    assert isinstance(f2, ForAll)
    assert isinstance(f3, Exists)
