# natded/ai/gat_policy.py
"""
Graph Attention Network (GAT) policy for proof search.

- Nodes = formulas / statements in the current proof state.
- Edges (adj) = which nodes are related (syntactic overlap, rule linkage, goal/premise ties).
- Learns attention weights α_ij so important neighbors contribute more to each node's update.
- Outputs action logits you can plug into softmax to rank candidate inference steps.
"""

from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F


def masked_softmax(scores: torch.Tensor, mask: torch.Tensor, dim: int = -1) -> torch.Tensor:
    """
    Softmax that ignores positions where mask==0.
    scores: [*, N, N]
    mask  : [*, N, N] with 1 for valid edges, 0 for no edge.
    """
    # Put -inf on masked positions so softmax->0 there.
    neg_inf = torch.finfo(scores.dtype).min
    masked = scores.masked_fill(mask == 0, neg_inf)
    return F.softmax(masked, dim=dim)


class GATLayer(nn.Module):
    """
    Single-head GAT layer (Velickovic et al., 2018) without external libs.

    h_i' = σ( Σ_j α_ij * (W h_j) )
    α_ij = softmax_j( LeakyReLU( a^T [W h_i || W h_j] ) ), masked by adjacency
    """
    def __init__(self, in_dim: int, out_dim: int, negative_slope: float = 0.2, add_self_loops: bool = True):
        super().__init__()
        self.lin = nn.Linear(in_dim, out_dim, bias=False)
        self.a = nn.Parameter(torch.empty(2 * out_dim))  # attention vector
        nn.init.xavier_uniform_(self.lin.weight)
        nn.init.xavier_uniform_(self.a.unsqueeze(0))
        self.leaky_relu = nn.LeakyReLU(negative_slope)
        self.add_self_loops = add_self_loops

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        """
        x   : [N, in_dim] node features
        adj : [N, N] adjacency matrix (0/1). Will add self-loops if requested.
        returns: [N, out_dim]
        """
        N = x.size(0)
        if self.add_self_loops:
            adj = adj.clone()
            adj.fill_diagonal_(1)

        Wh = self.lin(x)                       # [N, out_dim]
        # Compute attention scores e_ij for all i,j (where adj[i,j]==1)
        # Build [N, N, 2*out_dim] with concat(Wh_i, Wh_j)
        Wh_i = Wh.unsqueeze(1).expand(N, N, -1)  # [N, N, out_dim]
        Wh_j = Wh.unsqueeze(0).expand(N, N, -1)  # [N, N, out_dim]
        cat = torch.cat([Wh_i, Wh_j], dim=-1)    # [N, N, 2*out_dim]

        e = self.leaky_relu(torch.matmul(cat, self.a))  # [N, N]
        alpha = masked_softmax(e, adj, dim=1)           # row-normalized attention to neighbors

        h_prime = alpha @ Wh                             # [N, out_dim]
        return F.elu(h_prime)


class GATPolicy(nn.Module):
    """
    Two GAT layers + global mean pool + linear head → action logits.
    """
    def __init__(self, in_dim: int = 32, hidden_dim: int = 64, out_dim: int = 16):
        super().__init__()
        self.gat1 = GATLayer(in_dim, hidden_dim)
        self.gat2 = GATLayer(hidden_dim, hidden_dim)
        self.head = nn.Linear(hidden_dim, out_dim)

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        """
        x   : [N, in_dim]
        adj : [N, N]
        returns: [out_dim] logits over candidate actions
        """
        h = self.gat1(x, adj)
        h = self.gat2(h, adj)
        g = h.mean(dim=0)            # global mean pool
        logits = self.head(g)        # [out_dim]
        return logits


# Quick sanity check with random inputs
if __name__ == "__main__":
    torch.manual_seed(0)
    N = 6
    in_dim = 32
    out_dim = 10
    x = torch.randn(N, in_dim)
    # Example: a chain graph with some extra links
    adj = torch.zeros(N, N)
    for i in range(N - 1):
        adj[i, i + 1] = 1
        adj[i + 1, i] = 1
    adj[0, 3] = 1; adj[3, 0] = 1

    model = GATPolicy(in_dim=in_dim, hidden_dim=64, out_dim=out_dim)
    logits = model(x, adj)
    print("GAT logits:", logits.detach())
