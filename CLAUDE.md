# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Set up environment (first time)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the web app
streamlit run web_app.py

# Run the CLI tool
python reconciler.py

# Run tests
pytest test_reconciler.py
```

## Collaboration Style

- Do not edit files unless explicitly asked. Explain the current logic first, then wait for confirmation.
- Prefer small, minimal changes. Do not rewrite whole functions or files.
- After any edit, explain what changed and why.
- Explain code in simple, step-by-step terms — the goal is understanding, not just working code.
- Do not add new dependencies or change unrelated files.

## Learning / Interview Goal

I am using Claude Code to help me understand and improve this project for learning and portfolio purposes.

When explaining changes:
- Help me understand the reasoning behind the code.
- Point out what I should be able to explain in an interview.
- Prefer explanations that connect the code to the real bakery workflow.
- If there are multiple possible solutions, explain the trade-offs before choosing one.

## Architecture

Two-file design: all business logic lives in `reconciler.py`, and `web_app.py` is a pure Streamlit UI layer that imports from it.

### reconciler.py — core logic

**Payment model:** The POS system groups payments into 6 categories (`POS_METHODS`). The CAT terminal reports individual payment brands (e.g., 楽天Edy, iD, PayPay). `PAYMENT_GROUPS` maps CAT brands → POS categories.

**CAT amount format:** CAT inputs use `{method}_sales` / `{method}_cancel` keys. `reconcile_cat_amounts()` aggregates these into POS-style totals (net = sales − cancel).

**Reconciliation pipeline:**
1. `reconcile_cat_amounts(cat_amounts_temp)` → `cat_amounts` (POS-grouped totals)
2. `compare_payment_amounts(pos_amounts, cat_amounts)` → `comparison_results` (list of dicts with `method`, `pos_amount`, `cat_amount`, `difference`, `mode`)
3. `filter_mismatches(comparison_results)` → only mismatched entries
4. For corrections: `calculate_target_amount(cancelled_amount, difference, mode)` computes the re-entry target, then `find_combinations(products, target_amount)` uses recursive backtracking to find product combos summing to that target

**`find_combinations` algorithm:** Tries combinations of increasing size (1 item, 2 items, … up to `max_items=8`), allowing repeats of the same product. Stops once `max_results=3` combinations are found.

### web_app.py — Streamlit UI

Stateless except for `st.session_state["reset_count"]`, which is incremented on reset to force all widget keys to change (Streamlit's mechanism for clearing inputs).

### data/menu.json

Product catalogue with `id`, `item_name`, `price` (stored as string, cast to int on load), `category`, and `is_active`. Only `is_active: true` products are loaded by `load_menu()`.

To retire a product without deleting it, set `"is_active": false`. To add a new product, append an entry following the existing ID prefix conventions (`S` = 塩パン, `D` = デニッシュ, `N` = 生ドーナツ, `Z` = 蔬菜パン, `K` = 菓子パン, `B` = 袋).

## Correction Flow Logic

Understanding the two correction modes is essential for working on the correction tool:

- **`POS_GT_CAT`** — POS recorded more money than CAT. To fix this, the operator cancels an existing POS transaction and re-enters it at a lower amount. `target = cancelled_amount - difference`.
- **`CAT_GT_POS`** — CAT recorded more money than POS. The operator either adds the missing amount to POS, or cancels a transaction and re-enters it at a higher amount. `target = cancelled_amount + difference`.

`find_combinations()` then searches `data/menu.json` for product combinations whose prices sum exactly to `target_amount`. This is a bounded subset-sum search; results with fewer items are returned first.

## Entry Points

| Entry point | Purpose |
|---|---|
| `streamlit run web_app.py` | Full UI, intended for daily use |
| `python reconciler.py` | CLI tool for quick checks (difference checker or correction helper) |

The CLI functions (`run_difference_checker`, `run_correction_helper`) are defined inside the `if __name__ == "__main__"` block and are never called by the web app.

## Communication Style

Always explain and respond in **Traditional Chinese (Hong Kong style)**. Keep technical terms and programming keywords in English (e.g. branch, commit, session_state, function). Explain reasoning behind every change — the goal is learning and portfolio building, not just working code.

## Reference Repo

A second repo exists at `../ww-golf-miniapp-backend` and is **read-only**. Do not edit any files in it. Use it only to understand engineering practices (pre-commit setup, gitignore conventions, requirements pinning). Do not copy its architecture — it is a FastAPI backend and structurally different from this Streamlit app.

## Current Work in Progress

Active branch: `feat/web-app`

Goal: Improve project structure by borrowing engineering practices from the reference repo, without changing the app architecture.

| Step | Task | Status |
|---|---|---|
| 1 | Fix `.gitignore` (add `venv/`, `__pycache__/`, `.env`) | ✅ Done |
| 2 | Improve `web_app.py` (add `st.set_page_config`, remove unnecessary `if __name__` guard) | 🔄 In Progress |
| 3 | Pin `requirements.txt` with exact versions | ⏳ Pending |
| 4 | Add `.pre-commit-config.yaml` (black + pytest) | ⏳ Pending |

### Step 2 Notes
`web_app.py` already exists and is well structured. Only two small fixes needed:
- `st.set_page_config` is missing — should be the very first Streamlit call at the top of the file
- `if __name__ == "__main__":` guard wrapping the main flow is unnecessary in Streamlit and should be removed
