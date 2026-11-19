"""Train BPE from the agricultural JSONL dataset and save token IDs."""
import json
from pathlib import Path
from app.tokenizer import BytePairTokenizer

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "agriculture.jsonl"

def record_text(record):
    # Support the starter dataset's available text fields.
    preferred = ("crop", "problem", "advice", "season", "soil_type", "title", "content")
    parts = [str(record[k]).strip() for k in preferred if k in record and record[k]]
    if not parts:
        parts = [str(v).strip() for v in record.values() if isinstance(v, (str, int, float)) and str(v).strip()]
    return " ".join(parts)

def main():
    records = [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]
    texts = [record_text(r) for r in records]
    tokenizer = BytePairTokenizer().train(texts, vocab_size=320, min_frequency=2)
    (ROOT / "models").mkdir(exist_ok=True)
    (ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    tokenizer.save(ROOT / "models" / "agriculture_bpe.json")
    ids = [tokenizer.encode(t) for t in texts]
    (ROOT / "data" / "processed" / "token_ids.json").write_text(json.dumps(ids), encoding="utf-8")
    print(f"Loaded agricultural records: {len(records)}")
    print(f"Tokenizer vocabulary size: {tokenizer.vocab_size}")
    print("Saved: models/agriculture_bpe.json")
    print("Saved: data/processed/token_ids.json")
    if texts:
        print("Decoded sample:", tokenizer.decode(tokenizer.encode(texts[0]))[:160])

if __name__ == "__main__":
    main()
