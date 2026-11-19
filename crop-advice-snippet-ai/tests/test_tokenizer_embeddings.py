import torch
from app.tokenizer import BytePairTokenizer
from app.embeddings import TokenPositionEmbedding

def test_bpe_round_trip():
    corpus = ["tomato leaves need water", "tomato plants need drainage", "rice needs water"]
    tok = BytePairTokenizer().train(corpus, vocab_size=280, min_frequency=2)
    sample = "tomato needs water"
    assert tok.decode(tok.encode(sample)) == sample
    assert 256 <= tok.vocab_size <= 280

def test_bpe_save_load(tmp_path):
    tok = BytePairTokenizer().train(["rice crop", "rice needs water"], vocab_size=270)
    path = tmp_path / "tokenizer.json"
    tok.save(path)
    loaded = BytePairTokenizer.load(path)
    assert loaded.decode(loaded.encode("rice crop")) == "rice crop"

def test_embedding_shape():
    layer = TokenPositionEmbedding(320, 32, 64)
    out = layer(torch.randint(0, 320, (2, 12)))
    assert out.shape == (2, 12, 32)

def test_embedding_rejects_long_sequence():
    layer = TokenPositionEmbedding(320, 32, 8)
    try:
        layer(torch.randint(0, 320, (1, 9)))
    except ValueError:
        return
    assert False, "Expected ValueError"
