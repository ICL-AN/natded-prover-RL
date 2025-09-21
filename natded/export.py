# natded/export.py
from .proof import Proof

def proof_to_latex(proof: Proof) -> str:
    """
    Export proof to LaTeX using bussproofs package.
    """
    def render(p: Proof) -> str:
        if not p.deps:  # leaf
            return f"\\AxiomC{{{p.goal}}}"
        parts = [render(dep) for dep in p.deps]
        return "\n".join(parts) + f"\n\\RightLabel{{[{p.rule}]}}\n\\UnaryInfC{{{p.goal}}}" if len(p.deps)==1 else \
               "\n".join(parts) + f"\n\\RightLabel{{[{p.rule}]}}\n\\BinaryInfC{{{p.goal}}}" if len(p.deps)==2 else \
               "\n".join(parts) + f"\n\\RightLabel{{[{p.rule}]}}\n\\TrinaryInfC{{{p.goal}}}"

    return "\\begin{prooftree}\n" + render(proof) + "\n\\end{prooftree}"
