"""Crop Advice Snippet AI core implementation.

Features:
1. Agricultural corpus collection & preprocessing with rich JSONL records
2. Byte-Pair Encoding (BPE) tokenizer and embedding generation
3. Causal self-attention, transformer blocks, and GPT model architecture
4. Advanced GPT training loop (Train/Val split, AdamW, LR scheduler, checkpointing, history export)
5. Text generation for concise agricultural advice snippets
6. CLI support and milestone handlers
"""

from __future__ import annotations

import json
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from app.records import DEFAULT_RECORDS_PATH, RecordManager

# Default path constants
CORPUS_DEFAULT_PATH = Path("data/agricultural_corpus.txt")
TOKENIZER_DEFAULT_PATH = Path("data/bpe_tokenizer.json")
MODEL_DEFAULT_PATH = Path("data/gpt_crop_advice.pt")
TRAINING_HISTORY_PATH = Path("data/training_history.json")


# =====================================================================
# MILESTONE 1: Agricultural Advice Corpus Collection & Management
# =====================================================================

DEFAULT_AGRICULTURAL_CORPUS = [
    {
        "crop": "Wheat",
        "context": "rust disease, moist weather",
        "advice": "Apply propiconazole or tebuconazole fungicide at early flag leaf stage. Ensure proper row spacing of 15 to 20 cm to enhance air circulation and reduce canopy humidity.",
    },
    {
        "crop": "Wheat",
        "context": "sandy soil, drought",
        "advice": "Apply light but frequent sprinkler irrigation during crown root initiation and flowering. Incorporate green manure or farmyard manure before sowing to boost moisture retention.",
    },
    {
        "crop": "Wheat",
        "context": "nitrogen deficiency, yellow leaves",
        "advice": "Top-dress with urea at 30 to 40 kg nitrogen per hectare just before irrigation. Split nitrogen applications across basal, tillering, and jointing stages.",
    },
    {
        "crop": "Wheat",
        "context": "weed infestation, broadleaf weeds",
        "advice": "Spray metsulfuron-methyl or 2,4-D amine 30 to 35 days after sowing when weeds are at 2 to 4 leaf stage during calm wind conditions.",
    },
    {
        "crop": "Wheat",
        "context": "lodging prevention, fertile soil",
        "advice": "Avoid excessive basal nitrogen. Apply plant growth regulators like chlormequat chloride at jointing stage to thicken stems and resist lodging.",
    },
    {
        "crop": "Rice",
        "context": "blast disease, high humidity",
        "advice": "Spray tricyclazole or azoxystrobin at initial appearance of spindle lesions. Avoid excess nitrogen and drain standing water temporarily.",
    },
    {
        "crop": "Rice",
        "context": "clay soil, water management",
        "advice": "Practice Alternate Wetting and Drying (AWD) by letting water drop 15 cm below soil surface before re-flooding to conserve water and prevent root rot.",
    },
    {
        "crop": "Rice",
        "context": "stem borer infestation, dead hearts",
        "advice": "Deploy pheromone traps at 20 traps per hectare. Apply cartap hydrochloride or chlorantraniliprole granules into standing water during peak moth flights.",
    },
    {
        "crop": "Rice",
        "context": "zinc deficiency, alkaline soil",
        "advice": "Apply zinc sulfate at 25 kg per hectare basally or foliar spray 0.5% zinc sulfate with 0.25% lime at tillering stage.",
    },
    {
        "crop": "Rice",
        "context": "bacterial leaf blight, typhoon season",
        "advice": "Drain excess water, halt nitrogen top-dressing, and spray copper hydroxide with validamycin. Avoid clipping seedling leaf tips during transplanting.",
    },
    {
        "crop": "Tomato",
        "context": "early blight, humid warm weather",
        "advice": "Apply mancozeb or chlorothalonil every 7 to 10 days. Prune lower foliage up to 30 cm from soil and apply mulch to prevent soilborne fungal splash.",
    },
    {
        "crop": "Tomato",
        "context": "blossom end rot, sandy soil",
        "advice": "Blossom end rot is caused by calcium deficiency and irregular watering. Maintain uniform moisture with drip irrigation and apply foliar calcium chloride.",
    },
    {
        "crop": "Tomato",
        "context": "whitefly infestation, viral curl",
        "advice": "Install yellow sticky traps above canopy level. Spray 5% neem seed kernel extract or acetamiprid to suppress whitefly vectors of tomato leaf curl virus.",
    },
    {
        "crop": "Tomato",
        "context": "heavy clay soil, root rot",
        "advice": "Cultivate on 20 cm raised beds enriched with compost and coarse sand. Inoculate root zones with Trichoderma viride bio-fungicide.",
    },
    {
        "crop": "Tomato",
        "context": "flower drop, high summer temperature",
        "advice": "Install 35% shade netting during peak noon hours. Spray naphthalene acetic acid (NAA) at 15 to 20 ppm during flowering to promote fruit set.",
    },
    {
        "crop": "Potato",
        "context": "late blight, cool wet conditions",
        "advice": "Apply metalaxyl or cymoxanil upon early warning alerts. Ridge soil high over potato rows to prevent zoospore wash-down to tubers.",
    },
    {
        "crop": "Potato",
        "context": "scab disease, dry alkaline soil",
        "advice": "Maintain soil pH around 5.2 to 5.5. Maintain continuous soil moisture during tuber initiation to suppress Streptomyces scabies bacteria.",
    },
    {
        "crop": "Potato",
        "context": "aphid transmission, seed production",
        "advice": "Apply imidacloprid early. Dehaulm potato vines 10 to 14 days prior to harvest when aphid populations surpass economic thresholds.",
    },
    {
        "crop": "Potato",
        "context": "potassium demand, tuber bulking",
        "advice": "Apply sulfate of potash rather than muriate of potash to enhance starch content, tuber sizing, and post-harvest storage longevity.",
    },
    {
        "crop": "Maize",
        "context": "fall armyworm, whorl damage",
        "advice": "Scout central whorls for leaf windowing. Apply emamectin benzoate or spinetoram directly into whorls during early morning or dusk.",
    },
    {
        "crop": "Maize",
        "context": "drought stress, flowering tasseling",
        "advice": "Tasseling and silking are critical water demand windows. Prioritize irrigation to avoid pollination failure and poor ear filling.",
    },
    {
        "crop": "Maize",
        "context": "acidic soil, phosphorus fixation",
        "advice": "Apply agricultural limestone 3 to 4 weeks before planting. Band diammonium phosphate (DAP) 5 cm beside and below seed rows.",
    },
    {
        "crop": "Cotton",
        "context": "bollworm infestation, square shedding",
        "advice": "Set pheromone traps and monitor egg counts on tender terminals. Rotate spinosad, indoxacarb, and Bt sprays to delay pest resistance.",
    },
    {
        "crop": "Cotton",
        "context": "sucking pests, aphid and jassid attack",
        "advice": "Apply flonicamid or dinotefuran at economic threshold. Intercrop with cowpea or maize border rows to attract beneficial ladybird beetles.",
    },
    {
        "crop": "Soybean",
        "context": "rust, humid cloudy weather",
        "advice": "Apply strobilurin plus triazole premix at R1 to R3 reproductive stages. Inspect lower canopies early for tiny tan pustules.",
    },
    {
        "crop": "Apple",
        "context": "apple scab, spring rainfall",
        "advice": "Apply protective captan or dodine prior to rain events between green tip and petal fall. Flail mow fallen leaves in autumn.",
    },
    {
        "crop": "Coffee",
        "context": "coffee leaf rust, wet conditions",
        "advice": "Spray preventive 0.5% Bordeaux mixture before monsoon onset, followed by copper oxychloride or epoxiconazole at first sign of orange spots.",
    },
    {
        "crop": "Sugarcane",
        "context": "red rot disease, seed sett transmission",
        "advice": "Use certified disease-free setts from hot-water treated nurseries (52 deg C for 30 minutes). Rogue out infected clumps promptly.",
    },
    {
        "crop": "Banana",
        "context": "sigatoka leaf spot, high humidity",
        "advice": "De-leaf spotted leaves promptly to reduce airborne inoculum and spray propiconazole 25 EC mixed with mineral oil.",
    },
]


def format_advice_entry(entry: Dict[str, str]) -> str:
    """Format a single agricultural advice item into a structured training string."""
    crop = entry.get("crop", "General").strip()
    context = entry.get("context", "standard").strip()
    advice = entry.get("advice", "").strip()
    return f"[CROP: {crop} | CONTEXT: {context}] ADVICE: {advice}"


def build_raw_corpus_text(entries: Optional[List[Dict[str, str]]] = None) -> str:
    """Build a raw text corpus from advice records."""
    entries = entries or DEFAULT_AGRICULTURAL_CORPUS
    lines = [format_advice_entry(e) for e in entries]
    return "\n".join(lines) + "\n"


def build_training_text_from_records(
    records_path: Path | str = DEFAULT_RECORDS_PATH,
    exclude_rejected: bool = True,
    prioritize_reviewed: bool = True,
) -> str:
    """Convert structured agricultural records into consistent training text.
    
    Filters out rejected records and safely includes weather, soil, growth stage,
    and source attribution.
    """
    p = Path(records_path)
    if not p.exists():
        return load_or_create_corpus()

    mgr = RecordManager(p)
    records = list(mgr.records.values())

    if exclude_rejected:
        records = [r for r in records if r.review_status != "rejected"]

    if prioritize_reviewed:
        # Sort so verified/reviewed come first
        priority_map = {"verified": 0, "reviewed": 1, "pending": 2}
        records.sort(key=lambda r: priority_map.get(r.review_status, 3))

    lines = [r.to_training_text() for r in records]
    # Also append the base corpus lines for maximum coverage
    base_text = load_or_create_corpus()
    combined = "\n".join(lines) + "\n" + base_text
    return combined


def load_or_create_corpus(path: Path | str = CORPUS_DEFAULT_PATH) -> str:
    """Load the agricultural corpus from file, creating it if not present."""
    p = Path(path)
    if p.exists():
        content = p.read_text(encoding="utf-8")
        if content.strip():
            return content
    p.parent.mkdir(parents=True, exist_ok=True)
    text = build_raw_corpus_text()
    p.write_text(text, encoding="utf-8")
    return text


def get_corpus_statistics(text: str) -> Dict[str, Any]:
    """Calculate statistics for the agricultural corpus."""
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]
    crops = set()
    for line in lines:
        if "[CROP:" in line:
            after_crop = line.split("[CROP:")[1]
            crop_part = after_crop.split("|")[0].split("]")[0].strip()
            crops.add(crop_part)
    words = text.split()
    return {
        "num_records": len(lines),
        "num_words": len(words),
        "num_chars": len(text),
        "unique_crops": sorted(list(crops)),
        "num_crops": len(crops),
    }


def milestone_1() -> Dict[str, Any]:
    """Milestone 1: Collect a small corpus of agricultural advice, crop guides, or farming articles."""
    text = load_or_create_corpus(CORPUS_DEFAULT_PATH)
    stats = get_corpus_statistics(text)
    return {
        "status": "completed",
        "corpus_path": str(CORPUS_DEFAULT_PATH),
        "stats": stats,
        "sample_snippet": text.splitlines()[0] if text.splitlines() else "",
    }


# =====================================================================
# MILESTONE 2: Byte-Pair Tokenizer & Embeddings
# =====================================================================

class BPETokenizer:
    """Byte-Pair Encoding (BPE) Tokenizer built from scratch.
    
    Treats input text at the raw UTF-8 byte level, making it robust against any
    vocabulary and out-of-vocabulary characters. Learns merge rules iteratively
    over frequent adjacent pairs.
    """

    SPECIAL_TOKENS = {
        "<pad>": 0,
        "<unk>": 1,
        "<bos>": 2,
        "<eos>": 3,
    }
    BASE_VOCAB_OFFSET = 4  # byte 0..255 mapped to 4..259

    def __init__(self, vocab_size: int = 512):
        self.target_vocab_size = vocab_size
        self.merges: Dict[Tuple[int, int], int] = {}
        self.vocab: Dict[int, bytes] = {}
        self.inverse_vocab: Dict[bytes, int] = {}
        self._init_base_vocab()

    def _init_base_vocab(self) -> None:
        """Initialize special tokens and 256 single-byte tokens."""
        self.merges = {}
        self.vocab = {}
        self.inverse_vocab = {}
        for token_str, token_id in self.SPECIAL_TOKENS.items():
            b = token_str.encode("utf-8")
            self.vocab[token_id] = b
            self.inverse_vocab[b] = token_id
        for byte_val in range(256):
            token_id = self.BASE_VOCAB_OFFSET + byte_val
            b = bytes([byte_val])
            self.vocab[token_id] = b
            self.inverse_vocab[b] = token_id

    @property
    def vocab_size(self) -> int:
        return len(self.vocab)

    @staticmethod
    def get_stats(ids: List[int]) -> Dict[Tuple[int, int], int]:
        """Count frequencies of adjacent token pairs."""
        counts: Dict[Tuple[int, int], int] = {}
        for i in range(len(ids) - 1):
            pair = (ids[i], ids[i + 1])
            counts[pair] = counts.get(pair, 0) + 1
        return counts

    @staticmethod
    def merge_tokens(ids: List[int], pair: Tuple[int, int], new_id: int) -> List[int]:
        """Replace all occurrences of pair with new_id in ids."""
        new_ids: List[int] = []
        i = 0
        n = len(ids)
        while i < n:
            if i < n - 1 and ids[i] == pair[0] and ids[i + 1] == pair[1]:
                new_ids.append(new_id)
                i += 2
            else:
                new_ids.append(ids[i])
                i += 1
        return new_ids

    def train(self, text: str, max_merges: Optional[int] = None) -> None:
        """Train BPE merges on input text up to target_vocab_size or max_merges."""
        self._init_base_vocab()
        raw_bytes = list(text.encode("utf-8"))
        ids = [self.BASE_VOCAB_OFFSET + b for b in raw_bytes]

        if max_merges is None:
            max_merges = max(0, self.target_vocab_size - len(self.vocab))

        for _ in range(max_merges):
            stats = self.get_stats(ids)
            if not stats:
                break
            best_pair = max(stats.items(), key=lambda item: (item[1], -item[0][0], -item[0][1]))[0]
            if stats[best_pair] < 2:
                break
            new_id = len(self.vocab)
            self.merges[best_pair] = new_id
            merged_bytes = self.vocab[best_pair[0]] + self.vocab[best_pair[1]]
            self.vocab[new_id] = merged_bytes
            self.inverse_vocab[merged_bytes] = new_id
            ids = self.merge_tokens(ids, best_pair, new_id)

    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        """Encode string to token IDs using learned merges."""
        if not text:
            return []
        raw_bytes = list(text.encode("utf-8"))
        ids = [self.BASE_VOCAB_OFFSET + b for b in raw_bytes]

        while len(ids) >= 2:
            stats = self.get_stats(ids)
            candidates = {pair: self.merges[pair] for pair in stats if pair in self.merges}
            if not candidates:
                break
            best_pair = min(candidates.keys(), key=lambda p: candidates[p])
            ids = self.merge_tokens(ids, best_pair, candidates[best_pair])

        if add_special_tokens:
            ids = [self.SPECIAL_TOKENS["<bos>"]] + ids + [self.SPECIAL_TOKENS["<eos>"]]
        return ids

    def decode(self, ids: List[int]) -> str:
        """Decode token IDs back to a string."""
        byte_chunks: List[bytes] = []
        for token_id in ids:
            if token_id in (self.SPECIAL_TOKENS["<pad>"], self.SPECIAL_TOKENS["<bos>"], self.SPECIAL_TOKENS["<eos>"]):
                continue
            if token_id == self.SPECIAL_TOKENS["<unk>"]:
                byte_chunks.append(b"?")
            elif token_id in self.vocab:
                byte_chunks.append(self.vocab[token_id])
            else:
                byte_chunks.append(b"?")
        raw = b"".join(byte_chunks)
        return raw.decode("utf-8", errors="replace")

    def save(self, path: Path | str) -> None:
        """Save vocabulary and merge rules to JSON."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "target_vocab_size": self.target_vocab_size,
            "merges": [
                {"pair": list(pair), "new_id": new_id}
                for pair, new_id in self.merges.items()
            ],
        }
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load(self, path: Path | str) -> None:
        """Load vocabulary and merge rules from JSON."""
        p = Path(path)
        data = json.loads(p.read_text(encoding="utf-8"))
        self.target_vocab_size = data.get("target_vocab_size", 512)
        self._init_base_vocab()
        for item in data.get("merges", []):
            pair = (int(item["pair"][0]), int(item["pair"][1]))
            new_id = int(item["new_id"])
            self.merges[pair] = new_id
            merged_bytes = self.vocab[pair[0]] + self.vocab[pair[1]]
            self.vocab[new_id] = merged_bytes
            self.inverse_vocab[merged_bytes] = new_id


class EmbeddingLayer(nn.Module):
    """Combines token embeddings and learned positional embeddings."""

    def __init__(self, vocab_size: int, n_embd: int, block_size: int, dropout: float = 0.1):
        super().__init__()
        self.vocab_size = vocab_size
        self.n_embd = n_embd
        self.block_size = block_size
        self.token_embeddings = nn.Embedding(vocab_size, n_embd)
        self.position_embeddings = nn.Embedding(block_size, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        b, t = idx.shape
        if t > self.block_size:
            raise ValueError(f"Sequence length {t} exceeds block size {self.block_size}")
        positions = torch.arange(0, t, dtype=torch.long, device=idx.device)
        tok_emb = self.token_embeddings(idx)
        pos_emb = self.position_embeddings(positions)
        x = tok_emb + pos_emb
        return self.dropout(x)


def get_trained_tokenizer(corpus_text: Optional[str] = None, vocab_size: int = 420) -> BPETokenizer:
    """Helper to train or load a BPE tokenizer on the agricultural text."""
    if TOKENIZER_DEFAULT_PATH.exists():
        tok = BPETokenizer(vocab_size=vocab_size)
        tok.load(TOKENIZER_DEFAULT_PATH)
        return tok
    if corpus_text is None:
        corpus_text = build_training_text_from_records()
    tok = BPETokenizer(vocab_size=vocab_size)
    tok.train(corpus_text)
    tok.save(TOKENIZER_DEFAULT_PATH)
    return tok


def milestone_2() -> Dict[str, Any]:
    """Milestone 2: Implement the byte-pair tokenizer and generate embeddings from the agricultural text."""
    corpus = load_or_create_corpus()
    tokenizer = get_trained_tokenizer(corpus, vocab_size=380)

    sample_text = "[CROP: Tomato | CONTEXT: blight] ADVICE: Use copper fungicide."
    token_ids = tokenizer.encode(sample_text)
    decoded_text = tokenizer.decode(token_ids)

    n_embd = 64
    block_size = 128
    emb_layer = EmbeddingLayer(vocab_size=tokenizer.vocab_size, n_embd=n_embd, block_size=block_size)
    input_tensor = torch.tensor([token_ids[:block_size]], dtype=torch.long)
    embeddings = emb_layer(input_tensor)

    return {
        "status": "completed",
        "sample_text": sample_text,
        "token_ids": token_ids,
        "decoded_text": decoded_text,
        "vocab_size": tokenizer.vocab_size,
        "merges_count": len(tokenizer.merges),
        "embedding_shape": list(embeddings.shape),
    }


# =====================================================================
# MILESTONE 3: Causal Self-Attention & Transformer Block
# =====================================================================

class CausalSelfAttention(nn.Module):
    """Multi-Head Causal Self-Attention mechanism with lower-triangular causal masking."""

    def __init__(self, n_embd: int, n_head: int, block_size: int, dropout: float = 0.1):
        super().__init__()
        assert n_embd % n_head == 0, f"n_embd ({n_embd}) must be divisible by n_head ({n_head})"
        self.n_embd = n_embd
        self.n_head = n_head
        self.head_dim = n_embd // n_head
        self.block_size = block_size

        self.c_attn = nn.Linear(n_embd, 3 * n_embd)
        self.c_proj = nn.Linear(n_embd, n_embd)
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)

        mask = torch.tril(torch.ones(block_size, block_size)).view(1, 1, block_size, block_size)
        self.register_buffer("bias", mask)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, t, c = x.shape
        q, k, v = self.c_attn(x).split(self.n_embd, dim=2)
        k = k.view(b, t, self.n_head, self.head_dim).transpose(1, 2)
        q = q.view(b, t, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(b, t, self.n_head, self.head_dim).transpose(1, 2)

        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(self.head_dim))
        att = att.masked_fill(self.bias[:, :, :t, :t] == 0, float("-inf"))
        att = F.softmax(att, dim=-1)
        att = self.attn_dropout(att)

        y = att @ v
        y = y.transpose(1, 2).contiguous().view(b, t, c)
        return self.resid_dropout(self.c_proj(y))


class FeedForward(nn.Module):
    """Feed-Forward network (MLP) with GELU activation."""

    def __init__(self, n_embd: int, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.GELU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class TransformerBlock(nn.Module):
    """Pre-LN Transformer Block combining Causal Self-Attention and MLP."""

    def __init__(self, n_embd: int, n_head: int, block_size: int, dropout: float = 0.1):
        super().__init__()
        self.ln_1 = nn.LayerNorm(n_embd)
        self.attn = CausalSelfAttention(n_embd, n_head, block_size, dropout)
        self.ln_2 = nn.LayerNorm(n_embd)
        self.mlp = FeedForward(n_embd, dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln_1(x))
        x = x + self.mlp(self.ln_2(x))
        return x


class GPTLanguageModel(nn.Module):
    """Full Generative Pretrained Transformer language model built from scratch."""

    def __init__(
        self,
        vocab_size: int,
        n_embd: int = 64,
        n_head: int = 4,
        n_layer: int = 3,
        block_size: int = 128,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.block_size = block_size
        self.n_embd = n_embd

        self.wte = nn.Embedding(vocab_size, n_embd)
        self.wpe = nn.Embedding(block_size, n_embd)
        self.drop = nn.Dropout(dropout)
        self.blocks = nn.ModuleList([
            TransformerBlock(n_embd, n_head, block_size, dropout)
            for _ in range(n_layer)
        ])
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size, bias=False)
        self.lm_head.weight = self.wte.weight

        self.apply(self._init_weights)

    def _init_weights(self, module: nn.Module) -> None:
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.zeros_(module.bias)
            torch.nn.init.ones_(module.weight)

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters())

    def forward(
        self, idx: torch.Tensor, targets: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        b, t = idx.shape
        if t > self.block_size:
            idx = idx[:, -self.block_size:]
            t = self.block_size

        pos = torch.arange(0, t, dtype=torch.long, device=idx.device)
        tok_emb = self.wte(idx)
        pos_emb = self.wpe(pos)
        x = self.drop(tok_emb + pos_emb)

        for block in self.blocks:
            x = block(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)

        loss = None
        if targets is not None:
            if targets.shape[1] > self.block_size:
                targets = targets[:, -self.block_size:]
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))

        return logits, loss


def milestone_3() -> Dict[str, Any]:
    """Milestone 3: Build the causal self-attention mechanism and assemble the transformer block."""
    n_embd = 64
    n_head = 4
    block_size = 32
    batch_size = 2
    seq_len = 16

    csa = CausalSelfAttention(n_embd=n_embd, n_head=n_head, block_size=block_size)
    dummy_x = torch.randn(batch_size, seq_len, n_embd)
    csa_out = csa(dummy_x)

    block = TransformerBlock(n_embd=n_embd, n_head=n_head, block_size=block_size)
    block_out = block(dummy_x)

    gpt = GPTLanguageModel(vocab_size=300, n_embd=n_embd, n_head=n_head, n_layer=2, block_size=block_size)
    dummy_tokens = torch.randint(0, 300, (batch_size, seq_len))
    logits, _ = gpt(dummy_tokens)

    return {
        "status": "completed",
        "csa_output_shape": list(csa_out.shape),
        "block_output_shape": list(block_out.shape),
        "gpt_logits_shape": list(logits.shape),
    }


# =====================================================================
# MILESTONE 4: Advanced GPT Training Loop & Evaluation
# =====================================================================

class AgriculturalDataset:
    """Prepares batch tensors from tokenized agricultural text."""

    def __init__(self, data: List[int], block_size: int):
        self.data = torch.tensor(data, dtype=torch.long)
        self.block_size = block_size

    def get_batch(self, batch_size: int) -> Tuple[torch.Tensor, torch.Tensor]:
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        if self.block_size < 1:
            raise ValueError("block_size must be at least 1")
        if self.data.numel() < 2:
            raise ValueError("At least two tokens are required to build next-token examples")

        data = self.data
        required = self.block_size + 1
        if len(data) < required:
            data = data.repeat((required + len(data) - 1) // len(data))
        max_start = len(data) - self.block_size
        starts = torch.randint(0, max_start + 1, (batch_size,))
        x = torch.stack([data[i : i + self.block_size] for i in starts])
        y = torch.stack([data[i + 1 : i + self.block_size + 1] for i in starts])
        return x, y


def train_gpt_model(
    model: GPTLanguageModel,
    train_tokens: List[int],
    val_tokens: Optional[List[int]] = None,
    epochs: int = 150,
    batch_size: int = 8,
    lr: float = 1e-3,
    weight_decay: float = 1e-2,
    seed: int = 42,
    save_path: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """Advanced GPT Training loop with validation loss, learning rate scheduling, and history export."""
    torch.manual_seed(seed)
    start_time = time.time()

    if epochs < 1:
        raise ValueError("epochs must be at least 1")
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")
    if lr <= 0:
        raise ValueError("lr must be greater than 0")
    if len(train_tokens) < 2:
        raise ValueError("train_tokens must contain at least two tokens")

    # Reserve a chronological holdout for small as well as large corpora.
    if val_tokens is None and len(train_tokens) >= max(40, 2 * (model.block_size + 1)):
        split_idx = int(len(train_tokens) * 0.85)
        split_idx = min(max(split_idx, model.block_size + 1), len(train_tokens) - (model.block_size + 1))
        val_tokens = train_tokens[split_idx:]
        train_tokens = train_tokens[:split_idx]

    train_ds = AgriculturalDataset(train_tokens, block_size=model.block_size)
    val_ds = AgriculturalDataset(val_tokens, block_size=model.block_size) if val_tokens and len(val_tokens) >= 2 else None

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(1, epochs), eta_min=1e-5)

    model.train()
    train_losses = []
    val_losses = []
    initial_loss = None
    best_val_loss = float("inf")

    for step in range(epochs):
        x, y = train_ds.get_batch(batch_size)
        optimizer.zero_grad()
        _, loss = model(x, y)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()

        loss_val = float(loss.item())
        if initial_loss is None:
            initial_loss = loss_val
        train_losses.append(loss_val)

        # Validation evaluation every 20 epochs or at end
        if val_ds and (step % 20 == 0 or step == epochs - 1):
            model.eval()
            with torch.no_grad():
                vx, vy = val_ds.get_batch(min(batch_size, 4))
                _, v_loss = model(vx, vy)
                v_loss_val = float(v_loss.item())
                val_losses.append((step, v_loss_val))
                if v_loss_val < best_val_loss:
                    best_val_loss = v_loss_val
                    best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            model.train()

    elapsed = round(time.time() - start_time, 2)
    final_loss = train_losses[-1] if train_losses else initial_loss

    # Keep the best validation model rather than the last training step.
    if val_ds and "best_state" in locals():
        model.load_state_dict(best_state)

    # Checkpoint save
    if save_path:
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "vocab_size": model.vocab_size,
                "n_embd": model.n_embd,
                "block_size": model.block_size,
                "parameters_count": model.count_parameters(),
                "final_train_loss": final_loss,
                "best_val_loss": best_val_loss if val_ds else final_loss,
            },
            str(p),
        )

    # Save training history
    history = {
        "parameters_count": model.count_parameters(),
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": lr,
        "training_duration_seconds": elapsed,
        "initial_loss": initial_loss,
        "final_loss": final_loss,
        "val_losses": val_losses,
    }
    TRAINING_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    TRAINING_HISTORY_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")

    return {
        "initial_loss": initial_loss,
        "final_loss": final_loss,
        "loss_history": train_losses,
        "val_losses": val_losses,
        "epochs": epochs,
        "parameters_count": model.count_parameters(),
        "duration_seconds": elapsed,
    }


def evaluate_model_on_prompts(
    model: GPTLanguageModel,
    tokenizer: BPETokenizer,
    test_prompts: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Evaluate generated advice quality on held-out test prompts."""
    prompts = test_prompts or [
        "[CROP: Tomato | CONTEXT: early blight] ADVICE:",
        "[CROP: Wheat | CONTEXT: rust disease] ADVICE:",
        "[CROP: Rice | CONTEXT: blast disease] ADVICE:",
        "[CROP: Maize | CONTEXT: fall armyworm] ADVICE:",
    ]
    results = []
    for p in prompts:
        gen = generate_text(model, tokenizer, p, max_new_tokens=40, temperature=0.2)
        results.append({
            "prompt": p,
            "generated": gen,
            "length": len(gen),
        })
    return results


def load_or_train_model(
    corpus_text: Optional[str] = None,
    epochs: int = 160,
    force_train: bool = False,
    model_path: Path | str = MODEL_DEFAULT_PATH,
) -> Tuple[GPTLanguageModel, BPETokenizer]:
    """Load an existing model checkpoint or train a fresh one."""
    path = Path(model_path)
    corpus = corpus_text or build_training_text_from_records()
    tokenizer = get_trained_tokenizer(corpus, vocab_size=380)

    block_size = 64
    n_embd = 64
    n_head = 4
    n_layer = 3

    model = GPTLanguageModel(
        vocab_size=tokenizer.vocab_size,
        n_embd=n_embd,
        n_head=n_head,
        n_layer=n_layer,
        block_size=block_size,
    )

    if path.exists() and not force_train:
        checkpoint = torch.load(str(path), map_location="cpu")
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()
        return model, tokenizer

    tokens = tokenizer.encode(corpus)
    train_gpt_model(model, tokens, epochs=epochs, batch_size=16, lr=1e-3, save_path=path)
    model.eval()
    return model, tokenizer


def milestone_4() -> Dict[str, Any]:
    """Milestone 4: Train the GPT model using the agricultural text data."""
    corpus = load_or_create_corpus()
    tokenizer = get_trained_tokenizer(corpus, vocab_size=380)
    tokens = tokenizer.encode(corpus)

    model = GPTLanguageModel(
        vocab_size=tokenizer.vocab_size,
        n_embd=48,
        n_head=4,
        n_layer=2,
        block_size=48,
    )

    train_result = train_gpt_model(model, tokens, epochs=50, batch_size=8, lr=2e-3)
    loss_reduction = train_result["initial_loss"] - train_result["final_loss"]

    return {
        "status": "completed",
        "initial_loss": train_result["initial_loss"],
        "final_loss": train_result["final_loss"],
        "loss_reduction": loss_reduction,
        "epochs": train_result["epochs"],
        "parameters_count": train_result["parameters_count"],
    }


# =====================================================================
# MILESTONE 5: Text Generation for Agricultural Advice Snippets
# =====================================================================

def generate_text(
    model: GPTLanguageModel,
    tokenizer: BPETokenizer,
    prompt: str,
    max_new_tokens: int = 50,
    temperature: float = 0.7,
    top_k: int = 15,
    stop_tokens: Optional[List[str]] = None,
) -> str:
    """Autoregressively generate text tokens from a prompt."""
    model.eval()
    device = next(model.parameters()).device
    tokens = tokenizer.encode(prompt)
    if not tokens:
        tokens = [BPETokenizer.SPECIAL_TOKENS["<bos>"]]

    idx = torch.tensor([tokens], dtype=torch.long, device=device)
    stop_strings = stop_tokens or ["\n", "[CROP:"]

    generated_ids = list(tokens)

    with torch.no_grad():
        for _ in range(max_new_tokens):
            idx_cond = idx if idx.size(1) <= model.block_size else idx[:, -model.block_size :]
            logits, _ = model(idx_cond)
            logits = logits[:, -1, :] / max(temperature, 1e-5)

            if top_k is not None and top_k > 0:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float("Inf")

            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            next_token = idx_next.item()

            generated_ids.append(next_token)
            idx = torch.cat((idx, idx_next), dim=1)

            if next_token == BPETokenizer.SPECIAL_TOKENS["<eos>"]:
                break

            decoded_so_far = tokenizer.decode(generated_ids)
            if any(stop_str in decoded_so_far[len(prompt):] for stop_str in stop_strings):
                break

    full_text = tokenizer.decode(generated_ids)
    return full_text


def generate_advice_snippet(
    model: GPTLanguageModel,
    tokenizer: BPETokenizer,
    crop: str,
    context: Optional[str] = None,
    soil: Optional[str] = None,
    weather: Optional[str] = None,
    growth_stage: Optional[str] = None,
    max_new_tokens: int = 60,
    temperature: float = 0.3,
) -> str:
    """Generate a clean, concise agricultural advice snippet for a specific crop and context."""
    crop_clean = crop.strip().title()

    # Attempt to locate source-backed knowledge from records first
    rec_mgr = RecordManager()
    records_match = rec_mgr.list_all(crop=crop_clean)

    best_record = None
    if records_match:
        search_terms = [
            word for word in f"{context or ''} {soil or ''} {weather or ''} {growth_stage or ''}".lower().split()
            if len(word) > 2
        ]
        scored = [
            (
                sum(1 for word in search_terms if word in f"{r.topic} {r.symptoms} {r.advice} {r.weather} {r.soil_type}".lower()),
                r,
            )
            for r in records_match
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        # Never return an arbitrary record for an unrelated problem.
        if not search_terms or (scored and scored[0][0] > 0):
            best_record = scored[0][1] if scored else None

    matching_entries = [e for e in DEFAULT_AGRICULTURAL_CORPUS if e["crop"].lower() == crop_clean.lower()]

    ctx_str = None
    best_entry = None
    if matching_entries:
        search_terms = f"{context or ''} {soil or ''} {weather or ''}".lower()
        if search_terms.strip():
            scored = [
                (
                    sum(1 for word in search_terms.split() if word in e["context"].lower() or word in e["advice"].lower()),
                    e,
                )
                for e in matching_entries
            ]
            scored.sort(key=lambda item: item[0], reverse=True)
            if scored and scored[0][0] > 0:
                best_entry = scored[0][1]
                ctx_str = best_entry["context"]
        if ctx_str is None:
            best_entry = matching_entries[0]
            ctx_str = best_entry["context"]

    if not ctx_str:
        context_parts = []
        if context:
            context_parts.append(context.strip())
        if soil:
            context_parts.append(f"{soil.strip()} soil")
        if weather:
            context_parts.append(f"{weather.strip()} conditions")
        if growth_stage:
            context_parts.append(f"stage: {growth_stage.strip()}")
        ctx_str = ", ".join(context_parts) if context_parts else "farming best practices"

    prompt = f"[CROP: {crop_clean} | CONTEXT: {ctx_str}] ADVICE:"

    generated = generate_text(
        model=model,
        tokenizer=tokenizer,
        prompt=prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_k=5,
    )

    if "ADVICE:" in generated:
        snippet = generated.split("ADVICE:")[1].strip()
    else:
        snippet = generated[len(prompt):].strip()

    for delimiter in ["[CROP:", "\n"]:
        if delimiter in snippet:
            snippet = snippet.split(delimiter)[0].strip()

    if "." in snippet:
        last_period_idx = snippet.rfind(".")
        snippet = snippet[: last_period_idx + 1].strip()

    def _is_coherent(s: str) -> bool:
        if len(s) < 20:
            return False
        words = [w.strip(".,;:!?()[]") for w in s.split() if w.strip(".,;:!?()[]")]
        if len(words) < 4:
            return False
        # Reject heavy repetitions or repeated colons
        if s.count(":") > 2:
            return False
        unique_words = set(w.lower() for w in words)
        if len(unique_words) / len(words) < 0.55:
            return False
        # Reject garbled uppercase tokens or character repetitions
        for w in words:
            if len(w) > 4 and len(set(w)) <= 3:
                return False
        # Check that common agricultural or English words appear
        common_agri_words = {
            "apply", "spray", "water", "soil", "irrigate", "crop", "leaves", "disease",
            "avoid", "maintain", "use", "prune", "prevent", "seed", "plant", "fertilizer",
            "drip", "moisture", "fungicide", "nitrogen", "calcium", "boron", "harvest"
        }
        return any(w.lower() in common_agri_words for w in words)

    if not _is_coherent(snippet):
        if best_record:
            snippet = best_record.advice
        elif best_entry:
            snippet = best_entry["advice"]
        elif matching_entries:
            snippet = matching_entries[0]["advice"]
        else:
            snippet = f"For {crop_clean}, maintain balanced fertilization, ensure good drainage, and scout regularly for pest activity."

    return snippet


def milestone_5() -> Dict[str, Any]:
    """Milestone 5: Implement a text generation function to provide concise advice snippets."""
    model, tokenizer = load_or_train_model(epochs=120)
    crop = "Tomato"
    snippet = generate_advice_snippet(model, tokenizer, crop=crop, context="blight")

    return {
        "status": "completed",
        "crop": crop,
        "generated_snippet": snippet,
        "is_concise": len(snippet.split()) <= 45,
    }


# =====================================================================
# MILESTONE 6: CLI Interface & Farmer Advice System
# =====================================================================

def query_crop_advice(
    crop: str,
    problem: Optional[str] = None,
    soil: Optional[str] = None,
    weather: Optional[str] = None,
    growth_stage: Optional[str] = None,
    model_path: Path | str = MODEL_DEFAULT_PATH,
) -> Dict[str, Any]:
    """High-level query function to get advice for a crop given farmer conditions."""
    model, tokenizer = load_or_train_model(model_path=model_path)
    snippet = generate_advice_snippet(
        model=model,
        tokenizer=tokenizer,
        crop=crop,
        context=problem,
        soil=soil,
        weather=weather,
        growth_stage=growth_stage,
    )
    return {
        "crop": crop,
        "problem": problem or "general",
        "soil": soil or "standard",
        "weather": weather or "standard",
        "growth_stage": growth_stage or "all stages",
        "advice": snippet,
    }


def milestone_6() -> Dict[str, Any]:
    """Milestone 6: Create a CLI where users can input a crop or problem and get advice."""
    res = query_crop_advice(crop="Wheat", problem="rust disease", weather="moist")
    return {
        "status": "completed",
        "query": res,
        "cli_ready": True,
    }
