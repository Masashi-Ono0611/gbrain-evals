"""Memory proof wave 2: every dev and confirmation spec sets its knobs explicitly (2026-10-11 addendum)."""
import json
from pathlib import Path

import pytest

CELLS = Path(__file__).resolve().parents[1] / "cells/mpw2"
SPECS = sorted(p for stage in ("dev", "confirm") for p in (CELLS / stage).glob("*.json") if p.name != "order.json")
READ_KEYS = {"search.mode", "search.reranker.enabled", "search.reranker.model", "search.reranker.gate", "search.reranker.gate_min_gap",
             "search.query_facts_arm", "search.temporal_fact_reserve", "search.evidence_date_header", "search.entity_anchoring",
             "recall.question_admission"}
INGEST_KEYS = {"extraction.date_grounding", "facts.attribution", "facts.supersession_thresholds"}


def test_dev_specs_exist():
    assert len([p for p in SPECS if p.parent.name == "dev"]) == 30


@pytest.mark.parametrize("path", SPECS, ids=lambda p: f"{p.parent.name}/{p.stem}")
def test_spec_sets_every_knob_and_validates(path):
    from mpw.gbrain_provider import GbrainMemoryProvider

    spec = json.loads(path.read_text())
    pc = spec["provider_config"]
    assert set(pc["search_config"]) == READ_KEYS
    assert set(pc["gbrain_config"]) == INGEST_KEYS
    assert pc["search_config"]["search.mode"] == ("conservative" if spec["lane"] == "raw" else "tokenmax")
    assert pc["search_config"]["search.reranker.enabled"] == ("false" if spec["lane"] == "raw" else "true")
    assert pc["search_config"]["search.query_facts_arm"] == "true" and pc["search_config"]["search.temporal_fact_reserve"] == "false"
    if spec["lane"] != "raw" and "extraction_model" not in pc:
        assert pc["extraction_source"] == "measured_default" and spec["gbrain_credentials"] == ["voyage", "anthropic"]
    GbrainMemoryProvider({"gbrain_cli": "unused", "child_env": {}, "lane": spec["lane"], **pc})
