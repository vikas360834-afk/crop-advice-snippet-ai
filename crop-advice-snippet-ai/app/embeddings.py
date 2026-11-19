"""Learnable token and positional embeddings for the GPT model."""
import torch
from torch import nn

class TokenPositionEmbedding(nn.Module):
    def __init__(self, vocab_size: int, d_model: int, max_seq_len: int, dropout: float = 0.1):
        super().__init__()
        if min(vocab_size, d_model, max_seq_len) <= 0:
            raise ValueError("vocab_size, d_model and max_seq_len must be positive")
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position_embedding = nn.Embedding(max_seq_len, d_model)
        self.dropout = nn.Dropout(dropout)
        self.max_seq_len = max_seq_len

    def forward(self, token_ids: torch.Tensor):
        if token_ids.ndim != 2:
            raise ValueError("token_ids must have shape [batch, sequence]")
        batch, length = token_ids.shape
        if length > self.max_seq_len:
            raise ValueError(f"Sequence length {length} exceeds max_seq_len {self.max_seq_len}")
        positions = torch.arange(length, device=token_ids.device).unsqueeze(0).expand(batch, length)
        return self.dropout(self.token_embedding(token_ids) + self.position_embedding(positions))
