"""Educational byte-level BPE tokenizer implemented from scratch."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
from typing import Iterable

class BytePairTokenizer:
    def __init__(self):
        self.byte_vocab = {i: bytes([i]) for i in range(256)}
        self.merges = []
        self.vocab_size = 256

    def train(self, texts: Iterable[str], vocab_size: int = 320, min_frequency: int = 2):
        if vocab_size < 256:
            raise ValueError("vocab_size must be at least 256")
        sequences = [list(t.encode("utf-8")) for t in texts if t]
        if not sequences:
            raise ValueError("Cannot train tokenizer on an empty corpus")
        self.byte_vocab = {i: bytes([i]) for i in range(256)}
        self.merges = []
        next_id = 256
        while next_id < vocab_size:
            counts = Counter()
            for seq in sequences:
                counts.update(zip(seq, seq[1:]))
            if not counts:
                break
            pair, count = min(counts.items(), key=lambda item: (-item[1], item[0]))
            if count < min_frequency:
                break
            left, right = pair
            self.merges.append((left, right, next_id))
            self.byte_vocab[next_id] = self.byte_vocab[left] + self.byte_vocab[right]
            updated = []
            for seq in sequences:
                out, i = [], 0
                while i < len(seq):
                    if i + 1 < len(seq) and (seq[i], seq[i+1]) == pair:
                        out.append(next_id); i += 2
                    else:
                        out.append(seq[i]); i += 1
                updated.append(out)
            sequences = updated
            next_id += 1
        self.vocab_size = next_id
        return self

    def encode(self, text: str):
        ids = list(text.encode("utf-8"))
        for left, right, merged_id in self.merges:
            out, i = [], 0
            while i < len(ids):
                if i + 1 < len(ids) and ids[i] == left and ids[i+1] == right:
                    out.append(merged_id); i += 2
                else:
                    out.append(ids[i]); i += 1
            ids = out
        return ids

    def decode(self, token_ids):
        try:
            return b"".join(self.byte_vocab[i] for i in token_ids).decode("utf-8", errors="replace")
        except KeyError as exc:
            raise ValueError(f"Unknown token ID: {exc.args[0]}") from exc

    def save(self, path):
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"format":"byte-level-bpe-v1", "vocab_size":self.vocab_size,
                   "merges":[list(m) for m in self.merges],
                   "byte_vocab":{str(k):v.hex() for k,v in self.byte_vocab.items()}}
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("format") != "byte-level-bpe-v1":
            raise ValueError("Unsupported tokenizer format")
        obj = cls()
        obj.vocab_size = int(data["vocab_size"])
        obj.merges = [tuple(map(int, m)) for m in data["merges"]]
        obj.byte_vocab = {int(k):bytes.fromhex(v) for k,v in data["byte_vocab"].items()}
        return obj
