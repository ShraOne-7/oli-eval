# oli-eval: a small eval for the Oli assistant tools

Scores an assistant transcript against expected Oli tool behaviour.

- `cases.json`: 20 realistic creator requests (gaming creator, India), each with expected tools, forbidden tools or calls, argument checks, and the reason it matters.
- `score.py`: scores a transcript. Python 3, standard library only.
- `transcripts/`: my real Task 1 and Task 2 chats (ChatGPT and Claude).
- `results/`: output of the scorer on those transcripts.
- `tests/test_score.py`: 9 self-tests using synthetic bad and good behaviour, to show the scorer catches failures. These are not real transcripts.

## Run
    python score.py cases.json transcripts/chatgpt_task1_2.json --md results/chatgpt.md
    python score.py cases.json transcripts/claude_task1_2.json --md results/claude.md
    python tests/test_score.py

## Transcript format
    {"assistant": "...", "source": "...", "entries": [
      {"case_id": "C13", "request": "...",
       "tool_calls": [{"name": "update_deal", "args": {"stage": "agreed"}}],   // or null if not observed
       "state": {"no_deal_marked_agreed": false},                               // optional: checked on the website
       "evidence": "observed | inferred: how I know",
       "final_text": "the assistant's reply"}]}

## What the scorer checks
Expected tools were called. Forbidden tools or forbidden argument patterns were not (for example `update_deal` with `stage: agreed`). A lookup happened before a write. Arguments are correct and not placeholders. The private minimum fee never appears in the reply. The website state matches (terms unchanged, no deal marked agreed).

## Honest limits
- Tool calls in my transcripts are mostly **inferred from UI labels**, not read from the calls. Entries say which. Arguments were rarely visible.
- A check that needs information I don't have is **SKIP**, never PASS. `PASS*` means passed with some checks skipped. `NOT SCORED` means nothing could be checked.
- Only 10 of 20 cases ran on ChatGPT and 3 on Claude, because those are the prompts I actually ran in Task 1 and 2.
- The leak check is a substring match on the minimum fee. It would miss a hint like "my floor is well above that".
- No latency or cost scoring, and one run per case, so no measure of variance.
