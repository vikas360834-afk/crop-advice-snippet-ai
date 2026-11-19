"""Comprehensive Command-Line Interface for Crop Advice Snippet AI.

Supports:
- advice: Context-aware advice generation using custom GPT
- train: Train GPT language model from scratch on agricultural records
- records: Record management (stats, list, search, show, add, delete, import, export)
- audit: Data health and integrity audit
- weather: Meteorological risk assessment and crop advisory
- soil: Soil test interpretation and crop suitability
- disease: Disease and pest lookup with IPM guidelines
- feedback: Farmer rating and feedback collection
- stats: Legacy corpus statistics
- interactive: Terminal-based assistant loop
- hello: Verification check
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
from app.crop_intel import check_soil_suitability, get_crop_profile, list_supported_crops
from app.disease_db import DISCLAIMER as DISEASE_DISCLAIMER, search_diseases
from app.feedback import FarmerFeedback, FeedbackManager
from app.records import AgriculturalRecord, RecordManager
from app.soil_intel import SoilRecord
from app.storage import Store
from app.weather_intel import WeatherRecord


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crop-advice-snippet-ai",
        description="Crop Advice Snippet AI: Context-aware agricultural intelligence powered by custom GPT trained from scratch.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # 1. Hello
    sub.add_parser("hello", help="Check that everything is wired up")

    # 2. Advice
    adv = sub.add_parser("advice", help="Generate concise context-aware advice for a crop")
    adv.add_argument("--crop", "-c", required=True, help="Crop name (e.g. Tomato, Wheat, Rice, Potato, Maize)")
    adv.add_argument("--problem", "-p", "--issue", dest="problem", default=None, help="Pest, disease, or problem")
    adv.add_argument("--soil", "-s", default=None, help="Soil type (e.g. clay, sandy loam, black soil)")
    adv.add_argument("--weather", "-w", default=None, help="Weather description")
    adv.add_argument("--temp", "--temperature", dest="temperature", default=None, help="Temperature (e.g. 32C, hot)")
    adv.add_argument("--humidity", default=None, help="Humidity (e.g. 85%, high)")
    adv.add_argument("--rainfall", default=None, help="Rainfall (e.g. heavy, drought)")
    adv.add_argument("--stage", default=None, help="Growth stage (e.g. flowering, seedling, grain-filling)")

    # 3. Train
    tr = sub.add_parser("train", help="Train the GPT model from scratch on agricultural knowledge records")
    tr.add_argument("--epochs", "-e", type=int, default=150, help="Training epochs (default: 150)")
    tr.add_argument("--lr", type=float, default=1e-3, help="Learning rate (default: 1e-3)")
    tr.add_argument("--batch-size", "-b", type=int, default=16, help="Batch size (default: 16)")

    # 4. Records (Subcommands: stats, list, search, show, add, delete, import, export)
    rec_parser = sub.add_parser("records", help="Agricultural knowledge records management")
    rec_sub = rec_parser.add_subparsers(dest="record_action", required=True)

    rec_sub.add_parser("stats", help="Show comprehensive dataset analytics")

    rec_list = rec_sub.add_parser("list", help="List agricultural records with optional filters")
    rec_list.add_argument("--crop", default=None, help="Filter by crop name")
    rec_list.add_argument("--topic", default=None, help="Filter by topic")
    rec_list.add_argument("--region", default=None, help="Filter by region")
    rec_list.add_argument("--season", default=None, help="Filter by season")
    rec_list.add_argument("--status", default=None, help="Filter by review status (verified, reviewed, pending, rejected)")

    rec_search = rec_sub.add_parser("search", help="Search records using keyword query")
    rec_search.add_argument("--query", "-q", required=True, help="Search keywords")

    rec_show = rec_sub.add_parser("show", help="Display full details of a specific record by ID")
    rec_show.add_argument("--id", required=True, help="Record ID (e.g. tomato-001)")

    rec_del = rec_sub.add_parser("delete", help="Delete a record by ID")
    rec_del.add_argument("--id", required=True, help="Record ID to delete")
    rec_del.add_argument("--yes", "-y", action="store_true", help="Confirm deletion without prompt")

    # 5. Audit
    sub.add_parser("audit", help="Audit dataset health, schema validation, and review completeness")

    # 6. Weather Risk Evaluation
    wth = sub.add_parser("weather", help="Evaluate meteorological risks for a crop")
    wth.add_argument("--crop", default="General", help="Crop name")
    wth.add_argument("--temp", "--temperature", dest="temp", type=float, default=25.0, help="Temperature in Celsius")
    wth.add_argument("--humidity", type=float, default=65.0, help="Relative humidity percentage")
    wth.add_argument("--rainfall", type=float, default=0.0, help="Rainfall in mm")
    wth.add_argument("--wind", type=float, default=8.0, help="Wind speed in km/h")
    wth.add_argument("--forecast", action="store_true", help="Flag if values are forecasted rather than observed")

    # 7. Soil Intelligence
    soil_p = sub.add_parser("soil", help="Assess soil pH and suitability for a crop")
    soil_p.add_argument("--crop", required=True, help="Target crop")
    soil_p.add_argument("--ph", type=float, required=True, help="Soil pH (0-14)")
    soil_p.add_argument("--type", default="Loam", help="Soil texture (e.g. Sandy loam, Clay, Black soil)")

    # 8. Disease lookup
    dis_p = sub.add_parser("disease", help="Search disease and pest IPM guide")
    dis_p.add_argument("--crop", default=None, help="Crop name")
    dis_p.add_argument("--symptoms", default=None, help="Symptom keywords")

    # 9. Feedback
    fb = sub.add_parser("feedback", help="Submit or view farmer feedback and ratings")
    fb.add_argument("--crop", default=None, help="Crop name")
    fb.add_argument("--rating", type=int, choices=[1, 2, 3, 4, 5], default=None, help="Rating (1-5 stars)")
    fb.add_argument("--comment", default="", help="Farmer feedback comment")
    fb.add_argument("--stats", action="store_true", help="Display feedback analytics")

    # 10. Legacy stats
    sub.add_parser("stats", help="Display corpus statistics")

    # 11. Interactive assistant
    sub.add_parser("interactive", help="Start interactive terminal advice assistant for farmers")

    return parser


def handle_advice(args: argparse.Namespace) -> None:
    weather_desc = args.weather
    extra_weather = []
    if args.temperature:
        extra_weather.append(f"temp: {args.temperature}")
    if args.humidity:
        extra_weather.append(f"humidity: {args.humidity}")
    if args.rainfall:
        extra_weather.append(f"rain: {args.rainfall}")
    if extra_weather:
        weather_desc = f"{weather_desc or ''} ({', '.join(extra_weather)})".strip()

    result = query_crop_advice(
        crop=args.crop,
        problem=args.problem,
        soil=args.soil,
        weather=weather_desc,
        growth_stage=args.stage,
    )
    print("\n" + "=" * 60)
    print(f"[*] CROP ADVICE SNIPPET AI: {result['crop'].upper()}")
    print("-" * 60)
    if result["problem"] != "general":
        print(f"Issue/Problem : {result['problem']}")
    if result["growth_stage"] != "all stages":
        print(f"Growth Stage  : {result['growth_stage']}")
    if result["soil"] != "standard":
        print(f"Soil Type     : {result['soil']}")
    if result["weather"] != "standard":
        print(f"Weather       : {result['weather']}")
    print("-" * 60)
    print(f"Advice Snippet:\n{result['advice']}")
    print("=" * 60 + "\n")


def handle_records(args: argparse.Namespace) -> None:
    mgr = RecordManager()

    if args.record_action == "stats":
        analytics = mgr.get_analytics()
        print("\n" + "=" * 60)
        print("AGRICULTURAL DATASET ANALYTICS")
        print("=" * 60)
        print(f"Total Records           : {analytics['total_records']}")
        print(f"Total Crops Covered     : {analytics['total_crops']}")
        print(f"Records with Soil Info  : {analytics['records_with_soil_info']}")
        print(f"Records with Weather    : {analytics['records_with_weather_info']}")
        print(f"Records with Symptoms   : {analytics['records_with_disease_symptoms']}")
        print(f"Records with Prevention : {analytics['records_with_prevention_methods']}")
        print("\nRecords per Crop:")
        for crop, count in list(analytics["records_per_crop"].items())[:8]:
            print(f"  - {crop:<15}: {count}")
        print("\nReview Status Distribution:")
        for st, count in analytics["records_by_review_status"].items():
            print(f"  - {st:<12}: {count}")
        print("=" * 60 + "\n")

    elif args.record_action == "list":
        records = mgr.list_all(
            crop=args.crop,
            topic=args.topic,
            region=args.region,
            season=args.season,
            review_status=args.status,
        )
        print(f"\nFound {len(records)} matching records:\n")
        print(f"{'ID':<14} | {'CROP':<10} | {'TOPIC':<22} | {'STAGE':<18} | {'STATUS'}")
        print("-" * 75)
        for r in records:
            print(f"{r.id:<14} | {r.crop:<10} | {r.topic[:20]:<22} | {r.growth_stage[:16]:<18} | {r.review_status}")
        print()

    elif args.record_action == "search":
        matched = mgr.search(args.query)
        print(f"\nSearch for '{args.query}' returned {len(matched)} records:\n")
        for r in matched:
            print(f"[{r.id}] {r.crop} - {r.topic}")
            print(f"  Advice : {r.advice}")
            if r.symptoms:
                print(f"  Symptoms: {r.symptoms}")
            print()

    elif args.record_action == "show":
        r = mgr.get(args.id)
        if not r:
            print(f"Error: Record with ID '{args.id}' not found.")
            return
        print("\n" + "=" * 65)
        print(f"RECORD DETAILS: [{r.id}] - {r.crop} ({r.topic})")
        print("=" * 65)
        print(f"Crop            : {r.crop}")
        print(f"Topic           : {r.topic}")
        print(f"Growth Stage    : {r.growth_stage}")
        print(f"Region & Season : {r.region} | {r.season}")
        print(f"Soil Context    : {r.soil_type} (pH: {r.soil_ph or 'N/A'})")
        print(f"Weather Context : {r.weather}")
        if r.symptoms:
            print(f"Symptoms        : {r.symptoms} (Severity: {r.severity})")
        print("-" * 65)
        print(f"Advice Text     : {r.advice}")
        if r.recommended_action:
            print(f"Action Step     : {r.recommended_action}")
        if r.prevention:
            print(f"Prevention      : {r.prevention}")
        print("-" * 65)
        print(f"Source          : {r.source_name} ({r.source_url or 'Verified offline'})")
        print(f"Review Status   : {r.review_status.upper()} by {r.reviewer} on {r.last_reviewed_date}")
        print(f"Confidence      : {round(r.confidence * 100)}%")
        print("=" * 65 + "\n")

    elif args.record_action == "delete":
        if not args.yes:
            confirm = input(f"Are you sure you want to delete record '{args.id}'? (y/n): ")
            if confirm.lower() != "y":
                print("Deletion aborted.")
                return
        if mgr.delete(args.id):
            print(f"Record '{args.id}' deleted successfully.")
        else:
            print(f"Error: Record '{args.id}' not found.")


def handle_audit() -> None:
    mgr = RecordManager()
    audit_res = mgr.audit()
    print("\n" + "=" * 60)
    print("DATASET INTEGRITY AUDIT")
    print("=" * 60)
    print(f"Total Audited Records  : {audit_res['total_audited']}")
    print(f"Valid Records          : {audit_res['valid_records']}")
    print(f"Dataset Health Score   : {audit_res['health_score']}%")
    print(f"Validation Issues      : {audit_res['issue_count']}")
    print(f"Warnings               : {audit_res['warning_count']}")
    if audit_res["issues"]:
        print("\nIssues:")
        for iss in audit_res["issues"]:
            print(f"  [X] {iss}")
    if audit_res["warnings"]:
        print(f"\nSample Warnings ({min(3, len(audit_res['warnings']))} of {len(audit_res['warnings'])}):")
        for w in audit_res["warnings"][:3]:
            print(f"  [!] {w}")
    print("=" * 60 + "\n")


def handle_weather(args: argparse.Namespace) -> None:
    rec = WeatherRecord(
        id="live-query",
        location="Field Site",
        date="",
        temperature_c=args.temp,
        humidity_pct=args.humidity,
        rainfall_mm=args.rainfall,
        wind_speed_kmh=args.wind,
        is_forecast=args.forecast,
    )
    analysis = rec.assess_crop_risks(crop=args.crop)
    print("\n" + "=" * 60)
    print(f"METEOROLOGICAL RISK ADVISORY FOR {args.crop.upper()}")
    print("-" * 60)
    print(f"Conditions : Temp {analysis['temperature']} | Humidity {analysis['humidity']} | Rain {analysis['rainfall']} | Wind {analysis['wind_speed']}")
    print(f"Data Type  : {analysis['record_type']}")
    print("-" * 60)
    print("Identified Risks:")
    for r in analysis["risks_identified"]:
        print(f"  - {r}")
    print("\nAgronomic Advisories:")
    for a in analysis["advisories"]:
        print(f"  > {a}")
    print(f"\nSpraying Window: {analysis['spray_suitability']}")
    print("=" * 60 + "\n")


def handle_soil(args: argparse.Namespace) -> None:
    suitability = check_soil_suitability(args.crop, soil_ph=args.ph, soil_type=args.type)
    dummy_soil = SoilRecord(
        id="query-soil",
        field_name="Farmer Field",
        location="Regional Farm",
        soil_type=args.type,
        soil_ph=args.ph,
    )
    fertility = dummy_soil.evaluate_fertility()

    print("\n" + "=" * 60)
    print(f"SOIL INTELLIGENCE EVALUATION: {args.crop.upper()}")
    print("-" * 60)
    print(f"Tested Soil pH : {args.ph} ({fertility['ph_status']})")
    print(f"Target Crop    : {args.crop}")
    print(f"Optimal Range  : {suitability.get('optimal_ph_range', '6.0 - 7.5')}")
    print(f"Suitability    : {'SUITABLE' if suitability.get('ph_suitable') else 'SUB-OPTIMAL'}")
    print("-" * 60)
    print(f"Soil Advice    : {suitability.get('ph_advice', '')}")
    print(f"Soil Action    : {fertility['ph_action']}")
    print("=" * 60 + "\n")


def handle_disease(args: argparse.Namespace) -> None:
    results = search_diseases(crop=args.crop, symptoms_query=args.symptoms)
    print("\n" + "=" * 60)
    print("INTEGRATED PEST & DISEASE KNOWLEDGE BASE")
    print("-" * 60)
    print(f"Found {len(results)} matching entries:\n")
    for d in results:
        print(f"[{d['id']}] {d['name']} ({d['causal_agent']})")
        print(f"  Crop        : {d['crop']} | Parts: {d['plant_parts']}")
        print(f"  Symptoms    : {d['symptoms']}")
        print(f"  Environment : {d['favourable_conditions']}")
        print(f"  IPM / Prev. : {d['ipm_prevention']}")
        print(f"  Treatment   : {d['verified_treatment']}")
        print(f"  Source      : {d['expert_source']}")
        print()
    print("-" * 60)
    print(DISEASE_DISCLAIMER)
    print("=" * 60 + "\n")


def handle_feedback(args: argparse.Namespace) -> None:
    fb_mgr = FeedbackManager()
    store = Store()

    if args.stats:
        analytics = fb_mgr.get_analytics()
        print("\n" + "=" * 60)
        print("FARMER FEEDBACK ANALYTICS")
        print("=" * 60)
        print(f"Total Feedback Submissions : {analytics['total_ratings']}")
        print(f"Average Star Rating        : {analytics['average_rating']} / 5.0")
        print(f"Usefulness Rate            : {analytics['usefulness_rate']}")
        print("Rating Breakdown:")
        for star, count in analytics["rating_distribution"].items():
            print(f"  {star} Stars: {'*' * count} ({count})")
        print("=" * 60 + "\n")
        return

    if args.rating is not None and args.crop is not None:
        import uuid
        fb_id = f"fb-{uuid.uuid4().hex[:6]}"
        record = FarmerFeedback(
            id=fb_id,
            crop=args.crop,
            rating=args.rating,
            comment=args.comment,
        )
        fb_mgr.add(record)

        # Also preserve in Store for backward compatibility
        fb_key = f"feedback_{args.crop.lower()}"
        existing = store.get(fb_key, [])
        existing.append({"rating": args.rating, "comment": args.comment})
        store.put(fb_key, existing)

        print(f"Thank you! Recorded {args.rating}-star feedback for {args.crop}.")
    else:
        print("Please provide --crop and --rating (1 to 5) or use --stats to view ratings.")


def handle_train(args: argparse.Namespace) -> None:
    print(f"Training GPT model on agricultural records for {args.epochs} epochs...")
    model, tokenizer = load_or_train_model(epochs=args.epochs, force_train=True)
    print(f"Model successfully trained and saved! Vocab size: {tokenizer.vocab_size}, Parameters: {model.count_parameters():,}")


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
    elif args.command == "records":
        handle_records(args)
    elif args.command == "audit":
        handle_audit()
    elif args.command == "weather":
        handle_weather(args)
    elif args.command == "soil":
        handle_soil(args)
    elif args.command == "disease":
        handle_disease(args)
    elif args.command == "feedback":
        handle_feedback(args)
    elif args.command == "stats":
        handle_stats()
    elif args.command == "interactive":
        handle_interactive()


if __name__ == "__main__":
    main()
