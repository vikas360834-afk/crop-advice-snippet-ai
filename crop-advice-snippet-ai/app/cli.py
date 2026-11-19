"""Command-line entry point: `python -m app.cli --help`."""
import argparse


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="crop-advice-snippet-ai", description="Farmers use a CLI tool to generate concise, context-aware agricultural advice snippets for specific crops, trained on a dataset of farming best practices.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("hello", help="check that everything is wired up")
    # TODO: add your own commands here as you work through the milestones.
    args = parser.parse_args(argv)
    if args.command == "hello":
        print("Crop Advice Snippet AI is ready. Open README.md for your milestones.")


if __name__ == "__main__":
    main()
