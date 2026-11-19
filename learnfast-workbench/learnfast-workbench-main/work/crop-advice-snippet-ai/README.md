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
- [x] **2. Implement the byte-pair tokenizer and generate embeddings from the agricultural text.**  
      Hint: Byte-Pair Tokenization, Embeddings
- [x] **3. Build the causal self-attention mechanism and assemble the transformer block.**  
      Hint: Causal Self-Attention, Transformer Block
- [x] **4. Train the GPT model using the agricultural text data.**  
      Hint: GPT Training Loop
- [x] **5. Implement a text generation function to provide concise advice snippets.**  
      Hint: Text Generation
- [x] **6. Create a CLI where users can input a crop or problem and get advice.**  
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

Your work goes in `app/core.py` (one stub per milestone) and `tests/test_core.py`. The first tests pass already; they
check the plumbing.

## Settings and secrets

Model settings live in `.env`, which is ignored by git. **Never commit `.env` or paste a key into code.** If a key ever
reaches GitHub, treat it as leaked and make a new one.

## Stretch ideas

- Curate a larger and more diverse agricultural dataset to improve the quality and breadth of advice.
- Allow users to specify additional contextual information (e.g., soil type, weather conditions) alongside the crop for more tailored advice.
- Implement a simple feedback mechanism within the CLI for users to rate the helpfulness of generated advice.
