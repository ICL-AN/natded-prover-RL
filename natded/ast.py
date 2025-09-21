from __future__ import annotations
from dataclasses import dataclass
from typing import Union, Tuple

@dataclass(frozen=True)
class Var: name: str

@dataclass(frozen=True)
class Not: phi: "Formula"

@dataclass(frozen=True)
class And: left: "Formula"; right: "Formula"

@dataclass(frozen=True)
class Or: left: "Formula"; right: "Formula"

@dataclass(frozen=True)
class Imp: left: "Formula"; right: "Formula"

@dataclass(frozen=True)
class Iff: left: "Formula"; right: "Formula"

@dataclass(frozen=True)
class Bottom: pass

@dataclass(frozen=True)
class ForAll: var: str; body: "Formula"

@dataclass(frozen=True)
class Exists: var: str; body: "Formula"

@dataclass(frozen=True)
class Term: name: str; args: Tuple["Term", ...] = ()

@dataclass(frozen=True)
class Pred:
    name: str
    args: Tuple[Term, ...]

def fmt_term(t: Term) -> str:
    if not t.args:
        return t.name
    return f"{t.name}(" + ", ".join(fmt_term(a) for a in t.args) + ")"

Formula = Union[Var, Not, And, Or, Imp, Iff, Bottom, ForAll, Exists, Pred]

def fmt(f: Formula) -> str:
    if isinstance(f, Var): return f.name
    if isinstance(f, Not): return f"~{fmt(f.phi)}"
    if isinstance(f, And): return f"({fmt(f.left)} & {fmt(f.right)})"
    if isinstance(f, Or):  return f"({fmt(f.left)} | {fmt(f.right)})"
    if isinstance(f, Imp): return f"({fmt(f.left)} -> {fmt(f.right)})"
    if isinstance(f, Iff): return f"({fmt(f.left)} <-> {fmt(f.right)})"
    if isinstance(f, Bottom): return "⊥"
    if isinstance(f, ForAll): return f"(∀{f.var}.{fmt(f.body)})"
    if isinstance(f, Exists): return f"(∃{f.var}.{fmt(f.body)})"
    if isinstance(f, Pred):    return f"{f.name}(" + ", ".join(fmt_term(a) for a in f.args) + ")"
    return str(f)
