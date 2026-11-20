"""Unit tests for Advanced Agricultural Records and Intelligence modules."""

import pytest

from app.cli import main
from app.crop_intel import check_soil_suitability, get_crop_profile, list_supported_crops
from app.disease_db import DISCLAIMER, search_diseases
from app.feedback import FarmerFeedback, FeedbackManager
from app.records import AgriculturalRecord, RecordManager
from app.soil_intel import SoilRecord
from app.weather_intel import WeatherRecord


def test_agricultural_record_validation():
    # Valid record
    rec = AgriculturalRecord(
        id="test-001",
        crop="Wheat",
        topic="Disease",
        advice="Apply fungicide.",
        source_name="ICAR",
        source_url="https://icar.gov.in/wheat",
        soil_ph=6.5,
        confidence=0.92,
        severity="High",
        review_status="verified",
    )
    assert rec.crop == "Wheat"
    assert rec.soil_ph == 6.5

    # Invalid pH
    with pytest.raises(ValueError, match="Soil pH must be between"):
        AgriculturalRecord(
            id="bad-ph",
            crop="Rice",
            topic="Soil",
            advice="Test",
            source_name="ICAR",
            soil_ph=15.5,
        )

    # Invalid confidence
    with pytest.raises(ValueError, match="Confidence score must be between"):
        AgriculturalRecord(
            id="bad-conf",
            crop="Rice",
            topic="Soil",
            advice="Test",
            source_name="ICAR",
            confidence=1.5,
        )

    # Invalid URL
    with pytest.raises(ValueError, match="Invalid source URL format"):
        AgriculturalRecord(
            id="bad-url",
            crop="Rice",
            topic="Soil",
            advice="Test",
            source_name="ICAR",
            source_url="not-a-valid-url",
        )


def test_record_manager_operations(tmp_path):
    storage_path = tmp_path / "test_records.jsonl"
    mgr = RecordManager(storage_path)

    r1 = AgriculturalRecord(
        id="r-001",
        crop="Tomato",
        topic="Blight Management",
        advice="Use copper spray.",
        source_name="IIVR",
        source_url="https://iivr.icar.gov.in/tomato",
        region="North India",
        season="Rabi",
    )
    r2 = AgriculturalRecord(
        id="r-002",
        crop="Rice",
        topic="Water Management",
        advice="Practice AWD.",
        source_name="NRRI",
        source_url="https://nrri.icar.gov.in/rice",
        region="East India",
        season="Kharif",
    )
    mgr.add(r1)
    mgr.add(r2)

    # Retrieve
    assert mgr.get("r-001") is not None
    assert mgr.get("r-001").crop == "Tomato"

    # Search & filters
    assert len(mgr.list_all(crop="Tomato")) == 1
    assert len(mgr.list_all(season="Kharif")) == 1
    assert len(mgr.search("copper")) == 1

    # Analytics
    analytics = mgr.get_analytics()
    assert analytics["total_records"] == 2
    assert analytics["total_crops"] == 2

    # Audit
    audit_res = mgr.audit()
    assert audit_res["total_audited"] == 2
    assert audit_res["health_score"] == 100.0

    # Delete
    assert mgr.delete("r-001") is True
    assert mgr.get("r-001") is None


def test_crop_intelligence():
    wheat = get_crop_profile("Wheat")
    assert wheat is not None
    assert "DBW 187" in wheat["varieties"]
    assert len(wheat["growth_stages"]) >= 5

    # Soil suitability
    res = check_soil_suitability("Wheat", soil_ph=6.8, soil_type="Loam")
    assert res["ph_suitable"] is True

    # Acidic check
    res_acidic = check_soil_suitability("Wheat", soil_ph=4.5, soil_type="Red soil")
    assert res_acidic["ph_suitable"] is False


def test_disease_database():
    results = search_diseases(crop="Tomato", symptoms_query="concentric rings")
    assert len(results) > 0
    assert results[0]["name"] == "Early Blight"
    assert "Alternaria" in results[0]["causal_agent"]
    assert "DISCLAIMER" in DISCLAIMER


def test_weather_intelligence():
    # Fungal risk test
    w = WeatherRecord(
        id="w-01",
        location="Farm 1",
        date="2026-04-10",
        temperature_c=22.0,
        humidity_pct=92.0,
        rainfall_mm=2.0,
        wind_speed_kmh=8.0,
    )
    risks = w.assess_crop_risks("Tomato")
    assert any("Fungal" in r for r in risks["risks_identified"])

    # High wind test
    w_wind = WeatherRecord(
        id="w-02",
        location="Farm 1",
        date="2026-04-10",
        temperature_c=25.0,
        humidity_pct=50.0,
        wind_speed_kmh=22.0,
    )
    risks_wind = w_wind.assess_crop_risks("Wheat")
    assert "UNFAVOURABLE" in risks_wind["spray_suitability"]


def test_soil_intelligence():
    soil = SoilRecord(
        id="s-01",
        field_name="Plot A",
        location="Varanasi",
        soil_type="Alluvial loam",
        soil_ph=8.2,
        organic_carbon_pct=0.4,
    )
    fertility = soil.evaluate_fertility()
    assert "Alkaline" in fertility["ph_status"]
    assert "Low" in fertility["organic_carbon"]


def test_feedback_manager(tmp_path):
    fb_path = tmp_path / "feedback.jsonl"
    mgr = FeedbackManager(fb_path)

    mgr.add(FarmerFeedback(id="fb-1", crop="Tomato", rating=5, was_useful=True))
    mgr.add(FarmerFeedback(id="fb-2", crop="Tomato", rating=4, was_useful=True))

    analytics = mgr.get_analytics()
    assert analytics["total_ratings"] == 2
    assert analytics["average_rating"] == 4.5
    assert analytics["usefulness_rate"] == "100.0%"


def test_120_plus_crop_registry():
    from app.crops.registry import CropRegistry
    reg = CropRegistry()
    crops = reg.list_crops()
    assert len(crops) >= 120, f"Expected >= 120 crops, got {len(crops)}"

    # Check categories
    categories = {c.category for c in crops}
    expected_categories = {"Cereals", "Millets", "Pulses", "Oilseeds", "Vegetables", "Fruits", "Spices", "Plantation", "Commercial", "Fodder"}
    for exp_cat in expected_categories:
        assert exp_cat in categories, f"Category '{exp_cat}' missing from registry"

    # Search and alias lookup
    mango = reg.get_crop("mango")
    assert mango is not None
    assert mango.name == "Mango"
    assert "Mangifera" in mango.scientific_name

    # Regional alias lookup
    ragi = reg.get_crop("ragi")
    assert ragi is not None
    assert ragi.name == "Finger Millet"

    # Category filter
    veggies = reg.filter_by_category("Vegetables")
    assert len(veggies) >= 20

    # Stats
    stats = reg.get_crop_stats()
    assert stats["total_crops"] >= 120


def test_pest_database_search():
    from app.knowledge.pests import search_pests
    rice_pests = search_pests(crop="Rice")
    assert len(rice_pests) >= 2
    pest_names = [p["name"] for p in rice_pests]
    assert any("Stem Borer" in n for n in pest_names)


def test_crops_cli_commands(capsys):
    # 1. crops list
    main(["crops", "list"])
    out = capsys.readouterr().out
    assert "Registered Crops" in out

    # 2. crops search --query mango
    main(["crops", "search", "--query", "mango"])
    out = capsys.readouterr().out
    assert "Mango" in out

    # 3. crops category vegetables
    main(["crops", "category", "Vegetables"])
    out = capsys.readouterr().out
    assert "Crops in category 'Vegetables'" in out

    # 4. crops show --id tomato
    main(["crops", "show", "--id", "tomato"])
    out = capsys.readouterr().out
    assert "CROP PROFILE: TOMATO" in out

    # 5. crops stats
    main(["crops", "stats"])
    out = capsys.readouterr().out
    assert "120+ CROP REGISTRY DATABASE STATISTICS" in out
    assert "Total Unique Crops" in out

    # 6. disease search --crop tomato
    main(["disease", "search", "--crop", "tomato"])
    out = capsys.readouterr().out
    assert "INTEGRATED DISEASE KNOWLEDGE BASE (tomato)" in out

    # 7. pest search --crop rice
    main(["pest", "search", "--crop", "rice"])
    out = capsys.readouterr().out
    assert "AGRICULTURAL PEST & IPM DATABASE (rice)" in out
    assert "Yellow Stem Borer" in out


def test_cli_advanced_commands(capsys):
    # 1. records stats
    main(["records", "stats"])
    out = capsys.readouterr().out
    assert "AGRICULTURAL DATASET ANALYTICS" in out

    # 2. records list
    main(["records", "list", "--crop", "tomato"])
    out = capsys.readouterr().out
    assert "tomato-001" in out

    # 3. records search
    main(["records", "search", "--query", "irrigation"])
    out = capsys.readouterr().out
    assert "Search for 'irrigation'" in out

    # 4. records show
    main(["records", "show", "--id", "tomato-002"])
    out = capsys.readouterr().out
    assert "RECORD DETAILS: [tomato-002]" in out

    # 5. audit
    main(["audit"])
    out = capsys.readouterr().out
    assert "DATASET INTEGRITY AUDIT" in out

    # 6. weather
    main(["weather", "--crop", "wheat", "--temp", "34", "--humidity", "40"])
    out = capsys.readouterr().out
    assert "METEOROLOGICAL RISK ADVISORY" in out

    # 7. soil
    main(["soil", "--crop", "rice", "--ph", "7.8"])
    out = capsys.readouterr().out
    assert "SOIL INTELLIGENCE EVALUATION" in out

    # 8. disease
    main(["disease", "--crop", "tomato", "--symptoms", "blight"])
    out = capsys.readouterr().out
    assert "INTEGRATED PEST & DISEASE KNOWLEDGE BASE" in out

    # 9. feedback stats
    main(["feedback", "--stats"])
    out = capsys.readouterr().out
    assert "FARMER FEEDBACK ANALYTICS" in out


def test_dataset_batch_includes_valid_shifted_targets_and_rejects_tiny_input():
    from app.core import AgriculturalDataset
    dataset = AgriculturalDataset(list(range(6)), block_size=4)
    x, y = dataset.get_batch(batch_size=32)
    assert x.shape == (32, 4)
    assert y.shape == (32, 4)
    assert torch.all(x[:, 1:] == y[:, :-1])
    assert int(x.max()) <= 5
    with pytest.raises(ValueError, match="At least two tokens"):
        AgriculturalDataset([1], block_size=4).get_batch(1)


def test_training_validates_arguments_and_writes_checkpoint(tmp_path, monkeypatch):
    from app.core import GPTLanguageModel, train_gpt_model
    import app.core as core
    monkeypatch.setattr(core, "TRAINING_HISTORY_PATH", tmp_path / "history.json")
    model = GPTLanguageModel(vocab_size=20, n_embd=16, n_head=2, n_layer=1, block_size=8)
    checkpoint = tmp_path / "model.pt"
    result = train_gpt_model(
        model, list(range(20)) * 5, epochs=3, batch_size=2,
        save_path=checkpoint, seed=7,
    )
    assert checkpoint.exists()
    assert result["epochs"] == 3
    assert result["val_losses"]
    with pytest.raises(ValueError, match="epochs"):
        train_gpt_model(model, list(range(30)), epochs=0)
