# natded/ai/gnn_policy.py
"""
Graph Neural Network (GNN) policy for proof search.

- Encodes proof states as graphs:
  - Nodes = formulas (premises, subgoals, derived facts)
  - Edges = inference relations (syntactic overlaps, premises-to-goal links, etc.)
- Uses a simple Graph Convolutional Network (GCN) to propagate structure.
- Outputs policy logits over candidate inference steps.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

# ----------------------------
# Simple GCN Layer
# ----------------------------
class GCNLayer(nn.Module):
    """
    One GCN layer: updates each node by mixing neighbor features.
    """
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.linear = nn.Linear(in_dim, out_dim)

    def forward(self, x, adj):
        """
        Args:
            x   : [N, in_dim] node feature matrix
            adj : [N, N] adjacency matrix (binary or weighted)
        Returns:
            [N, out_dim] updated node embeddings
        """
        h = torch.matmul(adj, x)        # aggregate neighbors
        h = self.linear(h)              # apply transformation
        return F.relu(h)


# ----------------------------
# GNN Policy Network
# ----------------------------
class GNNPolicy(nn.Module):
    """
    A 2-layer GCN followed by pooling and a classifier head.
    """
    def __init__(self, in_dim=32, hidden_dim=64, out_dim=16):
        """
        Args:
            in_dim     : input node feature size
            hidden_dim : hidden layer size
            out_dim    : number of possible actions (policy head)
        """
        super().__init__()
        self.gcn1 = GCNLayer(in_dim, hidden_dim)
        self.gcn2 = GCNLayer(hidden_dim, hidden_dim)
        self.fc = nn.Linear(hidden_dim, out_dim)

    def forward(self, x, adj):
        """
        Args:
            x   : [N, in_dim] node features
            adj : [N, N] adjacency matrix
        Returns:
            logits : [out_dim] action scores
        """
        h = self.gcn1(x, adj)
        h = self.gcn2(h, adj)

        # global pooling: mean over nodes
        g = h.mean(dim=0)

        # map pooled graph embedding → action logits
        logits = self.fc(g)
        return logits


# ----------------------------
# Example runner (toy demo)
# ----------------------------
if __name__ == "__main__":
    # Suppose we have 5 formulas (nodes), each with a 32-dim feature
    N = 5
    in_dim = 32
    out_dim = 10   # e.g. 10 candidate inference steps

    # random toy inputs
    x = torch.rand(N, in_dim)          # node features
    adj = torch.eye(N)                 # trivial adj (identity, no edges yet)

    # symmetrize adj for GCN (if you had edges, you'd add them here)
    adj = (adj + adj.t()) / 2

    model = GNNPolicy(in_dim=in_dim, hidden_dim=64, out_dim=out_dim)
    logits = model(x, adj)

    print("Logits over actions:", logits)
