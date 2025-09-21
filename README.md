# NatDed-Prover  

A lightweight **natural deduction theorem prover** (Work in Progress) extended with **first-order logic (FOL)** and experimental **neuro-symbolic search policies**.  

This project started as a learning exercise and evolved into a compact research-style playground for combining symbolic logic with modern AI search techniques.  

---

## Features  

- **Natural Deduction Core**
  - Propositional rules: `¬`, `∧`, `∨`, `→`, `↔`, contradiction, double negation  
  - First-order logic: quantifiers (`∀`, `∃`), Skolem constants, instantiation  
  - Proof objects with `.human()` explanations  

- **Multiple Search Policies**
  - **DFS**: brute force baseline  
  - **Beam Search** with heuristics  
  - **MCTS (PUCT)** with optional **RAVE** acceleration  
  - **Neural Policy (PyTorch MLP)** guiding proof search  
  - Configurable hyperparameters (beam width, sims, exploration constant, etc.)  

- **Benchmarking**
  - `bin/bench.py` for parameter sweeps  
  - `bin/hardbench.py` and `bin/hardestbench.py` for stress-test problems  
  - Results exported as `.csv` for quick analysis  

- **Export**
  - Optional LaTeX proof tree rendering (`natded.export`)

---


## Why It Matters

- **Bridging symbolic and neural methods**  
  Classic provers rely on brute force or hand-coded strategies.  
  This project integrates modern AI search (beam search, MCTS, RAVE) and a small ML policy to make proof search adaptive.  

- **Transparency of reasoning**  
  Proofs export as LaTeX trees, so every step is human-readable — no black-box outputs.  

- **Scalable research ideas**  
  Algorithms from **AlphaGo-style RL** (PUCT, RAVE) are repurposed for symbolic logic, making the connection between planning and deduction concrete.  

- **Practical takeaway**  
  Demonstrates ability to build a non-trivial solver, integrate RL/ML concepts, and benchmark systematically — useful both as a learning tool and a research stepping stone.  

---

## Future Work

- **Embedding-guided heuristics** to bias search with semantic similarity.  
- **Stronger ML policies** (transformers, graph neural nets).  
- **Benchmarking on standard proof corpora** for more rigorous evaluation.  
- **Extension to new logics** (modal, temporal, intuitionistic).  
- **Parallel and distributed search** for scaling harder proofs.  


## Quickstart  

```bash
git clone https://github.com/yourusername/natded-prover.git
cd natded-prover
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest          # run all tests
bin/bench.py    # run benchmarks



