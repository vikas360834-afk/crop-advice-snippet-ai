# Crop Advice Snippet AI

[![Built with askThili](https://ask.thili.ai/api/v1/public/projects/v5chnbu335/badge.svg)](https://ask.thili.ai/b/v5chnbu335)

This 'Crop Advice Snippet AI' project empowers farmers with a CLI tool to quickly generate concise, context-aware agricultural advice. By training a custom GPT model on farming best practices, the AI provides relevant guidance for specific crops, making valuable agricultural knowledge easily accessible.

## What you are building

**Goal.** You will build a command-line interface (CLI) tool that generates concise, context-aware agricultural advice snippets for specific crops, trained on a dataset of farming best practices.

**Done when.** The CLI tool successfully generates relevant agricultural advice snippets for specific crops, demonstrating a trained GPT model from scratch that uses byte-pair tokenization, embeddings, and causal self-attention.

## Milestones

Tick these off as you go, and commit after each one.

- [x] **1. Collect a small corpus of agricultural advice, crop guides, or farming articles.**  
      Hint: Data Collection
- [ ] **2. Implement the byte-pair tokenizer and generate embeddings from the agricultural text.**  
      Hint: Byte-Pair Tokenization, Embeddings
- [ ] **3. Build the causal self-attention mechanism and assemble the transformer block.**  
      Hint: Causal Self-Attention, Transformer Block
- [ ] **4. Train the GPT model using the agricultural text data.**  
      Hint: GPT Training Loop
- [ ] **5. Implement a text generation function to provide concise advice snippets.**  
      Hint: Text Generation
- [ ] **6. Create a CLI where users can input a crop or problem and get advice.**  
      Hint: CLI Interface

## Run it

You need Python 3.12 and git.

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then choose a model; see the comments inside
python -m app.cli hello
pytest
```

Your work goes in `app/core.py` and `tests/test_core.py`. Milestone 1 is implemented: a small source-attributed JSONL corpus is stored at `data/raw/agriculture.jsonl`, and the loader validates each record.

### Windows PowerShell setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pytest -q
python -c "from app.core import milestone_1; rows=milestone_1(); print(f'Loaded {len(rows)} advice records')"
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

The starter corpus is for model-development and classroom demonstration. It is not a substitute for local agronomist advice. Crop recommendations vary by region, season, soil test, cultivar and crop stage. Verify any field action with a local agricultural extension officer. The source URLs are stored with each record.

## Settings and secrets

Model settings live in `.env`, which is ignored by git. **Never commit `.env` or paste a key into code.** If a key ever
reaches GitHub, treat it as leaked and make a new one.

## Stretch ideas

- Curate a larger and more diverse agricultural dataset to improve the quality and breadth of advice.
- Allow users to specify additional contextual information (e.g., soil type, weather conditions) alongside the crop for more tailored advice.
- Implement a simple feedback mechanism within the CLI for users to rate the helpfulness of generated advice.


## Milestone 2: BPE tokenizer and embeddings

Run these commands from the project root:

```powershell
python -m app.prepare_tokenizer
python -m pytest -q
```

`app/tokenizer.py` implements byte-level BPE without a pretrained tokenizer.
`app/embeddings.py` implements trainable token and positional embeddings in PyTorch.
The preparation script reads `data/raw/agriculture.jsonl` and writes
`models/agriculture_bpe.json` and `data/processed/token_ids.json`.
