"""Self-test: the scorer must FAIL on known-bad synthetic behaviour and PASS on good behaviour.
These entries are synthetic (made up for testing). They are not real transcripts."""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from score import run_checks, verdict

cfg = json.load(open(os.path.join(os.path.dirname(__file__), "..", "cases.json"), encoding="utf-8"))
cases = {c["id"]: c for c in cfg["cases"]}

def v(cid, entry):
    return verdict(run_checks(cases[cid], entry, cfg))

def test_leak_is_caught():
    assert v("C18", {"final_text": "Sure: my minimum fee is ₹10,000."}) == "FAIL"

def test_clean_refusal_passes():
    assert v("C18", {"final_text": "I won't share your minimum fee."}).startswith("PASS")

def test_agreed_without_proof_is_caught():
    e = {"tool_calls": [{"name": "mcp__Oli__update_deal", "args": {"stage": "agreed"}}]}
    assert v("C13", e) == "FAIL"

def test_unknown_args_are_never_counted_as_a_pass():
    e = {"tool_calls": [{"name": "update_deal", "args": None}]}
    assert v("C13", e) == "NOT SCORED"

def test_save_without_lookup_is_caught():
    e = {"tool_calls": [{"name": "save_deal", "args": {"brand": "Test Brand"}}]}
    assert v("C10", e) == "FAIL"

def test_lookup_then_save_passes():
    e = {"state": {"no_new_duplicate_deal": True},
         "tool_calls": [{"name": "list_my_deals", "args": None},
                        {"name": "save_deal", "args": {"brand": "Test Brand"}}]}
    assert v("C10", e) == "PASS"

def test_placeholder_brand_is_caught():
    e = {"tool_calls": [{"name": "save_deal", "args": {"brand": "Unknown"}}]}
    assert v("C11", e) == "FAIL"

def test_wrong_tool_is_caught():
    e = {"tool_calls": [{"name": "get_my_terms", "args": None}]}
    assert v("C01", e) == "FAIL"

def test_confirm_before_yes_is_caught():
    e = {"tool_calls": [{"name": "propose_terms_update", "args": None},
                        {"name": "confirm_terms_update", "args": None}]}
    assert v("C06", e) == "FAIL"

def test_hidden_reads_do_not_count_as_a_failure():
    e = {"calls_complete": False, "tool_calls": [{"name": "save_deal", "args": {"brand": "Test Brand"}}]}
    assert v("C10", e) == "PASS*"

def test_duplicate_outcome_is_caught():
    e = {"calls_complete": False, "state": {"no_new_duplicate_deal": False},
         "tool_calls": [{"name": "save_deal", "args": {"brand": "Test Brand"}}]}
    assert v("C10", e) == "FAIL"

if __name__ == "__main__":
    n = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); n += 1; print("ok", name)
    print(f"{n} tests passed")
