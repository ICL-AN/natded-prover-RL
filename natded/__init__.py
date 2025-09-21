# natded/__init__.py
from .engine import prove_from_strings, prove, parse_formula
from .proof import Proof

__all__ = ["prove_from_strings", "prove", "parse_formula", "Proof"]
