from .ast import *

class Parser:
    def __init__(self, s: str):
        self.tokens = self.tokenize(s)
        self.i = 0

    def tokenize(self, s: str):
        s = s.replace(" ", "")
        tokens, i = [], 0
        while i < len(s):
            ch = s[i]
            # single-char tokens
            if ch in "()&|~.":                    # <-- includes dot now
                tokens.append(ch); i += 1
            elif s.startswith("<->", i):
                tokens.append("<->"); i += 3
            elif s.startswith("->", i):
                tokens.append("->"); i += 2
            elif ch == "⊥":
                tokens.append("⊥"); i += 1
            elif ch in ("∀", "∃"):                # quantifier token as its own
                tokens.append(ch); i += 1
            else:
                j = i
                # stop at any operator/paren/dot or when ->/<-> begin
                while j < len(s) and s[j] not in "()&|~.∀∃" \
                    and not s.startswith("->", j) and not s.startswith("<->", j):
                    j += 1
                tokens.append(s[i:j]); i = j
        return tokens

    def peek(self): return self.tokens[self.i] if self.i < len(self.tokens) else None
    def eat(self, tok): 
        if self.peek()==tok: self.i+=1
        else: raise ValueError(f"expected {tok}, got {self.peek()}")

    # precedence: ~ > & > | > -> > <->
    def parse(self): return self.parse_iff()
    def parse_iff(self):
        left = self.parse_imp()
        if self.peek()=="<->":
            self.eat("<->")
            right = self.parse_iff()
            return Iff(left,right)
        return left
    def parse_imp(self):
        left = self.parse_or()
        if self.peek()=="->":
            self.eat("->")
            right = self.parse_imp()
            return Imp(left,right)
        return left
    def parse_or(self):
        left = self.parse_and()
        while self.peek()=="|":
            self.eat("|"); right = self.parse_and(); left=Or(left,right)
        return left
    def parse_and(self):
        left = self.parse_unary()
        while self.peek()=="&":
            self.eat("&"); right=self.parse_unary(); left=And(left,right)
        return left
    
    def parse_unary(self):
        tok = self.peek()
        if tok == "~":
            self.eat("~"); return Not(self.parse_unary())
        if tok == "(":
            self.eat("("); e = self.parse_iff(); self.eat(")"); return e
        if tok == "⊥":
            self.i += 1; return Bottom()
        if tok in ("∀", "∃"):
            q = tok; self.i += 1
            var_tok = self.peek(); self.i += 1
            if self.peek() == ".": self.eat(".")
            body = self.parse_unary()
            return ForAll(var_tok, body) if q == "∀" else Exists(var_tok, body)
        if tok is None:
            raise ValueError("unexpected end")
    # --- predicate or variable ---
        self.i += 1
        if self.peek() == "(":
            # predicate with arguments
            self.eat("(")
            args = []
            while self.peek() and self.peek() != ")":
                arg_tok = self.peek(); self.i += 1
                args.append(Term(arg_tok))
                if self.peek() == ",": self.eat(",")
            self.eat(")")
            return Pred(tok, tuple(args))
        # otherwise just a propositional variable
        return Var(tok)



def parse_formula(s:str)->Formula: return Parser(s).parse()
