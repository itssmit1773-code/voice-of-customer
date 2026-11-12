# Dataset and lineage

The source is a seeded simulator in `voc/generate.py` (seed **4726**) using original fictional phrases in `data/feedback_library.json`. There are no scraped reviews, customer records, or external data transfers. The simulator creates **360 accounts**, **5,420 members**, **3,933 source events** and **3,510 canonical reports** across April–September 2026. It emits 423 copies across channels to model escalations and repeated intake.

## Source files

| File in `artifacts/raw/` | Grain | Fields |
|---|---|---|
| accounts.csv | One account | `account_id` synthetic account key. `segment` Small business, Mid-market or Enterprise. `region` Americas, EMEA or APAC. |
| members.csv | One member on one account | `user_id` synthetic stable member key. `account_id` foreign key. The roster is static and has no activity data. |
| feedback.csv | One channel event | `event_id` stable source record key. `thread_key` cross-channel linkage token. `date` ISO calendar date. `channel` Support, In-app or Review. `account_id` known for all records by scenario design. `user_id` may be blank. `text` original generated report. |
| simulation_truth.csv | One simulated thread | `thread_key` links to feedback. `topic`, `sentiment`, `severity` are latent simulator labels, used only for evaluation. |

**Generation details.** Support has a higher negative-tone mix and public reviews omit user IDs more frequently. Account selection overrepresents Mid-market and Enterprise relative to their roster sizes. Approval reports increase in later months by construction. Text combines channel-specific phrasing, issue text and optional context, plus independently sampled sentiment and severity cues. Some cues are deliberately omitted. Synthetic latent sentiment or severity may therefore be undetectable from the text. Train phrases, live phrases and authored audit examples have separate sources. The phrase library represents a narrow, templated English distribution.

**Canonicalization.** Group by account ID, thread key and case-folded, whitespace-normalized text. Keep the earliest date and then the lowest event ID. Recover a unique known user ID from confirmed copies when possible. Conflicting identities raise an error. Distinct wording and unrelated threads are retained. A source event that loses the tie appears in `artifacts/duplicate_audit.csv` with its retained event ID. Channel metrics use the retained source channel and describe canonical attribution.

## Warehouse

See `sql/schema.sql` for executable DDL, keys and constraints. The `account` and `member` tables match the source fields. `feedback` contains the canonical source fields and the following derived attributes.

| Field | Type | Meaning |
|---|---|---|
| user_id | Nullable text | Missing IDs become SQL NULL. The member/account pair must exist when known. |
| topic | Text | `approval`, `notifications`, `export`, `permissions`, `search`, `sync`, `other` or `review` |
| sentiment | Text | `negative`, `neutral`, `positive` or `review` |
| severity | Text | `low`, `moderate`, `blocking` or `review` |
| needs_review | Integer 0/1 | One or more reasons for human review |
| review_reason | Text | Uncertain axis, possible blocker or possible access exposure. Empty if no flags apply. |
| segment, region, month | View fields | Account attributes and YYYY-MM reporting month in the `evidence` view |

**Derived artifacts.** `overview`, `theme`, `segments`, `trend`, and `reach` CSV files describe July–September. `history.csv` covers all six months. `roadmap.csv` includes all assumption inputs and three scenario scores. `sensitivity.csv` holds shared one-factor changes and joint top-two stresses. `evaluation.json` holds confusion matrices and per-class metrics. Prediction/error CSVs retain text and expected versus predicted labels. `manifest.json` records lineage counts, date window, seed and SHA-256 hashes.
