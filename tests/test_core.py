"""Comprehensive tests for Crop Advice Snippet AI milestones."""

import pytest
import torch

from app.cli import create_parser, main
from app.core import (
    AgriculturalDataset,
    BPETokenizer,
    CausalSelfAttention,
    EmbeddingLayer,
    FeedForward,
    GPTLanguageModel,
    TransformerBlock,
    format_advice_entry,
    generate_advice_snippet,
    generate_text,
    get_corpus_statistics,
    load_or_create_corpus,
    milestone_1,
    milestone_2,
    milestone_3,
    milestone_4,
    milestone_5,
    milestone_6,
    query_crop_advice,
    train_gpt_model,
)

# Milestone 1: Collect a small corpus of agricultural advice, crop guides, or farming articles.
def test_milestone_1():
    result = milestone_1()
    assert result["status"] == "completed"
    stats = result["stats"]
    assert stats["num_records"] >= 10
    assert stats["num_crops"] == 4
    assert set(stats["unique_crops"]) == {"Rice", "Maize", "Wheat", "Tomato"}
    assert stats["num_records"] == 20
    assert stats["num_words"] > 100
    assert stats["num_words"] > 100

    # Test format_advice_entry
    formatted = format_advice_entry({"crop": "Maize", "context": "drought", "advice": "Water at tasseling."})
    assert "[CROP: Maize | CONTEXT: drought] ADVICE: Water at tasseling." == formatted


# Milestone 2 coverage: BPE training, lossless encode/decode, and embedding shapes.
def test_training_corpus_uses_only_source_attributed_jsonl():
    from app.core import build_raw_corpus_text, load_source_advice_entries

    entries = load_source_advice_entries()
    corpus = build_raw_corpus_text()
    assert len(entries) == 20
    assert all(entry["source_name"] and entry["source_url"].startswith("https://") for entry in entries)
    assert corpus.count(" SOURCE: ") == 20
    assert "TNAU Agritech" in corpus
    assert "ICAR - Kharif Agro-Advisories" in corpus


def test_milestone_2():
    result = milestone_2()
    assert result["status"] == "completed"
    assert result["vocab_size"] > 256
    assert result["merges_count"] > 0
    assert result["decoded_text"] == result["sample_text"]

    # Test BPE tokenizer standalone
    tok = BPETokenizer(vocab_size=280)
    tok.train("crop wheat crop wheat crop rice crop rice")
    encoded = tok.encode("crop wheat")
    decoded = tok.decode(encoded)
    assert decoded == "crop wheat"

    # Test EmbeddingLayer
    emb = EmbeddingLayer(vocab_size=300, n_embd=32, block_size=16)
    idx = torch.tensor([[1, 2, 3, 4]], dtype=torch.long)
    out = emb(idx)
    assert out.shape == (1, 4, 32)


# Milestone 3: Build the causal self-attention mechanism and assemble the transformer block.
def test_milestone_3():
    result = milestone_3()
    assert result["status"] == "completed"
    assert result["csa_output_shape"] == [2, 16, 64]
    assert result["block_output_shape"] == [2, 16, 64]
    assert result["gpt_logits_shape"] == [2, 16, 300]

    # Verify Causal Masking: future tokens should not affect earlier tokens
    csa = CausalSelfAttention(n_embd=32, n_head=2, block_size=10, dropout=0.0)
    csa.eval()
    x1 = torch.randn(1, 4, 32)
    x2 = x1.clone()
    # Change the last token in x2
    x2[:, 3, :] = torch.randn(32)

    out1 = csa(x1)
    out2 = csa(x2)
    # Positions 0..2 must be identical because they cannot attend to position 3
    assert torch.allclose(out1[:, :3, :], out2[:, :3, :], atol=1e-5)

    # Test full GPT forward pass with loss
    gpt = GPTLanguageModel(vocab_size=50, n_embd=32, n_head=2, n_layer=1, block_size=10)
    tokens = torch.randint(0, 50, (2, 8))
    targets = torch.randint(0, 50, (2, 8))
    logits, loss = gpt(tokens, targets)
    assert logits.shape == (2, 8, 50)
    assert loss is not None
    assert loss.item() > 0


# Milestone 4: Train the GPT model using the agricultural text data.
def test_milestone_4():
    result = milestone_4()
    assert result["status"] == "completed"
    assert result["epochs"] == 50
    # Training loss should decrease over training
    assert result["final_loss"] < result["initial_loss"]

    # Test AgriculturalDataset
    data = list(range(100))
    ds = AgriculturalDataset(data, block_size=10)
    x, y = ds.get_batch(batch_size=4)
    assert x.shape == (4, 10)
    assert y.shape == (4, 10)
    # y should be shifted by 1 relative to x
    assert torch.all(x[:, 1:] == y[:, :-1])


# Milestone 5 coverage: generated advice is non-empty and respects the concise-output limit.
def test_milestone_5():
    result = milestone_5()
    assert result["status"] == "completed"
    snippet = result["generated_snippet"]
    assert isinstance(snippet, str)
    assert len(snippet) > 10
    assert result["is_concise"] is True

    # Test generate_advice_snippet with context
    tok = BPETokenizer(vocab_size=300)
    tok.train("crop advice wheat rice tomato potato soil weather")
    model = GPTLanguageModel(vocab_size=tok.vocab_size, n_embd=32, n_head=2, n_layer=1, block_size=32)
    snippet2 = generate_advice_snippet(model, tok, crop="Rice", context="clay soil", weather="wet")
    assert isinstance(snippet2, str)
    assert len(snippet2) > 0


# Milestone 6: Create a CLI where users can input a crop or problem and get advice.
def test_milestone_6(capsys, tmp_path):
    result = milestone_6()
    assert result["status"] == "completed"
    assert result["cli_ready"] is True

    # Test CLI parser
    parser = create_parser()
    args = parser.parse_args(["advice", "--crop", "Wheat", "--problem", "rust", "--soil", "clay"])
    assert args.crop == "Wheat"
    assert args.problem == "rust"
    assert args.soil == "clay"

    # Test CLI advice execution
    main(["advice", "--crop", "Wheat", "--problem", "rust"])
    captured = capsys.readouterr().out
    assert "CROP ADVICE SNIPPET AI" in captured
    assert "WHEAT" in captured
    assert "Advice Snippet" in captured

    # Test CLI stats
    main(["stats"])
    captured_stats = capsys.readouterr().out
    assert "Agricultural Dataset Corpus Stats" in captured_stats

    # Test CLI feedback (Stretch idea)
    main(["feedback", "--crop", "Wheat", "--rating", "5", "--comment", "Very helpful advice!"])
    captured_fb = capsys.readouterr().out
    assert "Recorded 5-star feedback" in captured_fb

    # Test query_crop_advice directly
    res = query_crop_advice(crop="Tomato", problem="blight")
    assert res["crop"] == "Tomato"
    assert "advice" in res and len(res["advice"]) > 10
