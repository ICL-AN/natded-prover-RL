from typing import List, Optional, Dict, Set
from dataclasses import dataclass
from .ast import Formula
from .parser import parse_formula
from .proof import Proof
from .rules import expand_goal

@dataclass
class Result: proof:Optional[Proof]; depth:int

def prove(premises:List[Formula],goal:Formula,max_depth:int=6)->Result:
    prem_set=set(premises); cache={}
    for d in range(1,max_depth+1):
        pr=expand_goal(prem_set,goal,d,cache)
        if pr: return Result(pr,d)
    return Result(None,max_depth)

def prove_from_strings(premises:List[str],goal:str,depth:int=6)->Proof:
    ps=[parse_formula(p) for p in premises]; g=parse_formula(goal)
    res=prove(ps,g,depth)
    if not res.proof: raise RuntimeError(f"No proof up to depth {depth}")
    return res.proof
