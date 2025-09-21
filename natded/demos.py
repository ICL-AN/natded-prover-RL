from .engine import prove_from_strings

if __name__=="__main__":
    print(prove_from_strings(["P->Q","Q->R","P"],"R").human())
    print("\n")
    print(prove_from_strings(["P & Q"],"Q").human())
    print("\n")
    print(prove_from_strings(["P->Q"],"(~Q)->(~P)").human())
    print("\n")
    print(prove_from_strings(["P->Q","Q->P"],"P<->Q").human())
    print("\n")
    print(prove_from_strings(["P|Q","P->R","Q->R"],"R").human())
    print("\n")
    print(prove_from_strings(["P->Q","~Q"],"~P").human())
    print("\n")
    print(prove_from_strings(["⊥"],"R").human())
