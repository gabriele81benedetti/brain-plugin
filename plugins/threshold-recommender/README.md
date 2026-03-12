# threshold-recommender

Pulls 8 weeks of product-level Shopping data from the Google Ads API and generates an interactive HTML report.

Adjust ROAS/CPA and Cost/Clicks sliders in real time to bucket products into four groups: Profitable, Flukes, Costly, and Meh. Based on Andrew Lolk's framework for Shopping campaign segmentation.

The recommendation panel gives a verdict on campaign structure, flags data fragmentation risk per proposed campaign, and surfaces zombie subcategories.

Includes a spend-based threshold mode as an alternative to statistical thresholds: set your Target CPA and a multiplier (1.5x-3x) — a product that spent Target CPA × 2 with zero conversions has paid for a sale that never came.

## Prerequisites

1. **`~/google-ads.yaml`** with valid Google Ads API credentials
2. **`.claude/accounts.json`** with a client entry:
   ```json
   "my-client": {
     "id": "1234567890",
     "name": "My Client",
     "currency": "EUR",
     "login_customer_id": "9999999999"
   }
   ```
   Omit `login_customer_id` if accessing the account directly (no MCC).
3. **Python `.venv`** with `google-ads` installed:
   ```bash
   source .venv/bin/activate
   pip install google-ads
   ```

## Usage

```bash
source .venv/bin/activate
python3 data/threshold_recommender.py <client-alias>
open 'clients/<client-alias>/reports/threshold-recommender.html'
```

Or just ask Claude: *"run the threshold recommender for [client]"*

## Files installed

```
.claude/skills/threshold-recommender/SKILL.md
.claude/commands/threshold-recommender.md
data/threshold_recommender.py
data/client_helper.py          ← shared helper, safe to overwrite
```

> `client_helper.py` is a shared utility used by other brain scripts. If you already have it, the version included here is compatible.
