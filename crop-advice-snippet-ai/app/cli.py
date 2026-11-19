"""Command-line interface for Crop Advice Snippet AI.

Farmers can generate concise, context-aware agricultural advice snippets
for specific crops, trained on farming best practices.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from app.core import (
    MODEL_DEFAULT_PATH,
    get_corpus_statistics,
    load_or_create_corpus,
    load_or_train_model,
    query_crop_advice,
)
from app.storage import Store


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crop-advice-snippet-ai",
        description="Crop Advice Snippet AI: Generate concise, context-aware agricultural advice snippets for specific crops.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # Smoke / sanity command
    sub.add_parser("hello", help="check that everything is wired up")

    # Advice generation command
    adv_parser = sub.add_parser("advice", help="Get concise advice for a crop")
    adv_parser.add_argument("--crop", "-c", required=True, help="Crop name (e.g. Wheat, Rice, Tomato, Potato)")
    adv_parser.add_argument("--problem", "-p", "--issue", dest="problem", default=None, help="Pest, disease, or problem")
    adv_parser.add_argument("--soil", "-s", default=None, help="Soil type (e.g. clay, sandy, loam)")
    adv_parser.add_argument("--weather", "-w", default=None, help="Weather conditions (e.g. drought, humid, wet)")

    # Train command
    train_parser = sub.add_parser("train", help="Train the GPT model from scratch on agricultural corpus")
    train_parser.add_argument("--epochs", "-e", type=int, default=150, help="Training epochs (default: 150)")
    train_parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate (default: 1e-3)")

    # Feedback command (Stretch idea: rating advice)
    fb_parser = sub.add_parser("feedback", help="Rate the helpfulness of advice")
    fb_parser.add_argument("--crop", "-c", required=True, help="Crop name")
    fb_parser.add_argument("--rating", "-r", type=int, choices=[1, 2, 3, 4, 5], required=True, help="Rating from 1 to 5")
    fb_parser.add_argument("--comment", default="", help="Optional feedback comment")

    # Stats command
    sub.add_parser("stats", help="Display dataset corpus statistics")

    # Interactive farmer assistant loop
    sub.add_parser("interactive", help="Start interactive terminal advice assistant for farmers")

    return parser


def handle_advice(args: argparse.Namespace) -> None:
    result = query_crop_advice(
        crop=args.crop,
        problem=args.problem,
        soil=args.soil,
        weather=args.weather,
    )
    print("\n" + "=" * 60)
    print(f"[*] CROP ADVICE SNIPPET AI: {result['crop'].upper()}")
    print("-" * 60)
    if result["problem"] != "general":
        print(f"Issue/Problem : {result['problem']}")
    if result["soil"] != "standard":
        print(f"Soil Type     : {result['soil']}")
    if result["weather"] != "standard":
        print(f"Weather       : {result['weather']}")
    print("-" * 60)
    print(f"Advice Snippet:\n{result['advice']}")
    print("=" * 60 + "\n")


def handle_train(args: argparse.Namespace) -> None:
    print(f"Training GPT model on agricultural corpus for {args.epochs} epochs...")
    model, tokenizer = load_or_train_model(epochs=args.epochs, force_train=True)
    print(f"Model successfully trained and saved! Vocab size: {tokenizer.vocab_size}")


def handle_feedback(args: argparse.Namespace) -> None:
    store = Store()
    fb_key = f"feedback_{args.crop.lower()}"
    existing = store.get(fb_key, [])
    existing.append({
        "rating": args.rating,
        "comment": args.comment,
    })
    store.put(fb_key, existing)
    print(f"Thank you! Recorded {args.rating}-star feedback for {args.crop}.")


def handle_stats() -> None:
    text = load_or_create_corpus()
    stats = get_corpus_statistics(text)
    print("\n--- Agricultural Dataset Corpus Stats ---")
    print(f"Total Advice Snippets: {stats['num_records']}")
    print(f"Total Words          : {stats['num_words']}")
    print(f"Unique Crops ({stats['num_crops']}) : {', '.join(stats['unique_crops'])}")
    print("----------------------------------------\n")


def handle_interactive() -> None:
    print("\n=== Welcome to Crop Advice Snippet AI CLI ===")
    print("Type 'exit' or 'quit' at any prompt to exit.\n")
    while True:
        try:
            crop = input("Enter crop name (e.g. Tomato, Rice, Wheat): ").strip()
            if not crop or crop.lower() in ("exit", "quit"):
                break
            problem = input("Enter problem or pest (optional, press Enter to skip): ").strip() or None
            soil = input("Enter soil type (optional, press Enter to skip): ").strip() or None
            weather = input("Enter weather conditions (optional, press Enter to skip): ").strip() or None

            res = query_crop_advice(crop=crop, problem=problem, soil=soil, weather=weather)
            print("\n" + "-" * 50)
            print(f"Advice for {crop}:")
            print(res["advice"])
            print("-" * 50 + "\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Happy farming!")
            break


def main(argv: Optional[List[str]] = None) -> None:
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command == "hello":
        print("Crop Advice Snippet AI is ready. Open README.md for your milestones.")
    elif args.command == "advice":
        handle_advice(args)
    elif args.command == "train":
        handle_train(args)
    elif args.command == "feedback":
        handle_feedback(args)
    elif args.command == "stats":
        handle_stats()
    elif args.command == "interactive":
        handle_interactive()


if __name__ == "__main__":
    main()
