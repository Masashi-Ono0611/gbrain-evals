"""Memory proof wave 2: the mode isolation on LongMemEval-S dev (exploratory, 2026-10-11 addendum).

    python3 eval/harness-provider/mpw2-iso-specs.py

Every arm reads the measured-default LongMemEval-S dev store at the dev pin with the explicit knob set of
`mpw2-dev-specs.py`, then changes one tokenmax component to its conservative value. `iso-b` (tokenmax) runs first and
builds the store, so the store's pages are embedded under tokenmax's inline contextual-retrieval tier, as step 0's
combined store was.
"""
import json
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
dev = runpy.run_path(str(HERE / "mpw2-dev-specs.py"))
OUT = HERE / "cells/mpw2/iso"

ARMS = {
    "b": ("tokenmax", {}),
    "d": ("conservative", {}),
    "comb": ("tokenmax", {}),
    "t-rerank-off": ("tokenmax", {"search.reranker.enabled": "false"}),
    "t-limit-10": ("tokenmax", {"search.searchLimit": "10"}),
    "t-relational-off": ("tokenmax", {"search.relational_retrieval": "false", "search.relational_planner": "false"}),
    "t-graph-off": ("tokenmax", {"search.graph_signals": "false"}),
    "t-cr-none": ("tokenmax", {"search.contextual_retrieval": "none"}),
    "c-rerank-on": ("conservative", {"search.reranker.enabled": "true"}),
}
CAP_USD = 23

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for i, (arm, (mode, flips)) in enumerate(ARMS.items()):
        spec = dev["spec"]("lme", "v1" if arm == "comb" else "filler")
        pc = spec["provider_config"]
        pc["search_config"] = {**dev["read_knobs"](mode), **flips}
        spec["budget_usd"] = 12 if i == 0 else 2
        spec["note"] = f"memory proof wave 2 mode isolation (exploratory), arm {arm}: see the 2026-10-11 addendum"
        (OUT / f"lme-iso-{arm}.json").write_text(json.dumps(spec, indent=1) + "\n")
    (OUT / "order.json").write_text(json.dumps({"cap_usd": CAP_USD, "order": list(ARMS)}, indent=1) + "\n")
