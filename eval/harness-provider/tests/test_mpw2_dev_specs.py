"""Memory proof wave 2: every dev and confirmation spec sets its knobs explicitly (2026-10-11 addendum)."""
import json
from pathlib import Path

import pytest

CELLS = Path(__file__).resolve().parents[1] / "cells/mpw2"
SPECS = sorted(p for stage in ("dev", "confirm") for p in (CELLS / stage).glob("*.json") if p.name != "order.json")
W5_SPECS = sorted(p for p in (CELLS / "w5").glob("*.json") if p.name != "order.json")
READ_KEYS = {"search.mode", "search.reranker.enabled", "search.reranker.model", "search.reranker.gate", "search.reranker.gate_min_gap",
             "search.query_facts_arm", "search.temporal_fact_reserve", "search.evidence_date_header", "search.entity_anchoring",
             "recall.question_admission", "search.tokenBudget", "search.page_rank_budget_ratio"}
INGEST_KEYS = {"extraction.date_grounding", "facts.attribution", "facts.supersession_thresholds"}


def test_dev_specs_exist():
    assert len([p for p in SPECS if p.parent.name == "dev"]) == 29


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
    assert pc["search_config"]["search.tokenBudget"] == ("4000" if spec["lane"] == "raw" else "10000000")
    assert pc["search_config"]["search.page_rank_budget_ratio"] == ("0.4" if path.stem.endswith("-v2-w5") else "0")
    assert "extraction_model" not in pc
    if spec["lane"] != "raw":
        assert pc["extraction_source"] == "measured_default" and spec["gbrain_credentials"] == ["voyage", "anthropic"]
    GbrainMemoryProvider({"gbrain_cli": "unused", "child_env": {}, "lane": spec["lane"], **pc})


def test_w5_tuning_arms():
    from mpw.gbrain_provider import GbrainMemoryProvider

    ratios = {}
    for path in W5_SPECS:
        spec = json.loads(path.read_text())
        sc = spec["provider_config"]["search_config"]
        assert set(sc) == READ_KEYS and spec["lane"] == "filler-removed" and spec["provider_config"]["token_budget"] == 8100
        assert sc["search.tokenBudget"] == ("4000" if sc["search.mode"] == "conservative" else "10000000")
        ratios[path.stem.removeprefix("lme-")] = (sc["search.mode"], sc["search.page_rank_budget_ratio"])
        GbrainMemoryProvider({"gbrain_cli": "unused", "child_env": {}, "lane": spec["lane"], **spec["provider_config"]})
    assert ratios == {"b": ("tokenmax", "0"), "d": ("conservative", "0"), "w5-0.40": ("tokenmax", "0.4"), "w5-0.50": ("tokenmax", "0.5"),
                      "w5-0.75": ("tokenmax", "0.75"), "w5-1.00": ("tokenmax", "1")}
