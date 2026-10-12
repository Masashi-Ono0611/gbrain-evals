"""W5's page_rank_cut is checked against the cell's search.page_rank_budget_ratio."""
import pytest


def _p(**search_config):
    from mpw.gbrain_provider import GbrainMemoryProvider

    return GbrainMemoryProvider({"gbrain_cli": "unused", "child_env": {}, "search_config": search_config})


PAGE = {"query": "q", "token_budget": 8100, "return_unit": "page"}


def test_cut_must_match_the_arms_ratio_and_mode_cut():
    from mpw.gbrain_provider import GbrainRetrieveError

    p = _p(**{"search.tokenBudget": "10000000", "search.page_rank_budget_ratio": "0.4"})
    cut = {"ratio": 0.4, "caller_budget": 8100, "mode_cut": 10000000, "applied_cut": 3240, "candidates": 47, "kept": 8}
    assert p._check_page_rank_cut(PAGE, cut) == cut
    for bad in (None, {**cut, "applied_cut": 4050}, {**cut, "ratio": 0.5}, {**cut, "caller_budget": 6300}):
        with pytest.raises(GbrainRetrieveError, match="page_rank_cut"):
            p._check_page_rank_cut(PAGE, bad)
    capped = _p(**{"search.tokenBudget": "4000", "search.page_rank_budget_ratio": "0.75"})
    assert capped._check_page_rank_cut(PAGE, {"ratio": 0.75, "caller_budget": 8100, "mode_cut": 4000, "applied_cut": 4000})


def test_off_ratio_must_report_no_cut():
    from mpw.gbrain_provider import GbrainRetrieveError

    for off in ("0", "-1", "inf", "nan", "x"):
        p = _p(**{"search.tokenBudget": "10000000", "search.page_rank_budget_ratio": off})
        assert p._check_page_rank_cut(PAGE, None) is None
        with pytest.raises(GbrainRetrieveError, match="ratio off"):
            p._check_page_rank_cut(PAGE, {"ratio": 1, "caller_budget": 8100, "mode_cut": None, "applied_cut": 8100})
    assert _p(**{"search.page_rank_budget_ratio": "0.5"})._check_page_rank_cut({"query": "q", "return_unit": "chunk", "token_budget": 8100}, None) is None
