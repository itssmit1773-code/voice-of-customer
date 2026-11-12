# A recovery path for stalled approvals

**Role demonstrated:** AI Business Analyst. **Product:** Relayboard, a fictional SaaS for distributed operations teams. **Deliverables:** a reproducible Python and SQL analysis, a feedback dashboard, a ranking with scenario stress tests, and a product requirements document. All product data are simulated.

## The quarterly decision

Relayboard's Workflow PM has enough capacity to prototype one improvement. Support reports, in-app requests and reviews each tell part of the story. Counting all messages equally can overstate issues that move between channels or generate repeated complaints. I used the case to answer which problem warranted discovery and what evidence would make the proposal worth building.

## Evidence

The pipeline generated **3,933 source events**, mapped **423 cross-channel duplicates** to their canonical reports, and retained **3,510** reports for six months of context. The decision quarter contains **1,854** reports from **1,386 identified reporters** across **349 accounts**. It includes **190 reports without a known user ID**. Report share and reach have different grains, so I used report share to compare themes and known distinct reporters to score reach.

- **Approval handoffs** were 469 reports (25.3%), ahead of notification overload at 351 (18.9%). Approvals reached 394 identified reporters across 235 accounts in the sample.
- Approval share rose from **79 of 530** in April (**14.9%**) to **179 of 640** in September (**28.0%**). The simulator deliberately creates upward pressure on approvals, so this validates the analysis flow for a changing mix.
- In July–September, approval handoffs were **29.7%** of Mid-market feedback, **28.2%** of Enterprise feedback and **19.8%** of Small business feedback. These shares use all feedback within each segment as their denominator. The generator's sampling weights and reporting behavior affect those denominators.
- **164** approval reports carried a possible blocker label and **60** had uncertain severity. Those labels describe the text, so they are leads for incident review and interviews.

## Recommendation

Prototype admin reassignment of pending approval requests whose approver has lost access. Keep the original request, policy and audit history intact. In the base scenario it scores **144.1 RICE**, compared with **35.0** for bundling comment notifications. The notification digest can lead if approval eligibility and impact fall while effort rises. The case therefore supports an instrumented prototype and a validation checkpoint before committing engineering capacity.

Guest-access exposure follows the incident process. Keep investigation of permission leaks separate from the discretionary backlog item for access preview.

## How I would validate it

First, review sampled approval and unclassified reports to estimate solution eligibility. Then pair customer interviews with approval workflow events to establish how often the assignee becomes unavailable, how often existing workarounds succeed and how long requests remain pending. The proposed pilot measures whether eligible requests reach a valid approval decision within 24 hours while protecting authorization and audit integrity. See the [PRD](prd-approval-recovery.md) for the rollout and stop criteria.

## What the project shows

The warehouse keeps source evidence, review flags, and decision assumptions traceable. The text model comparison showed why an explicit taxonomy was easier to defend for a small, bounded portfolio corpus. The taxonomy classified 18 audit topics correctly, correctly routed two ambiguous examples and abstained on four other topics. Its known misses guide review. A larger, independently labeled corpus and actual product telemetry would be needed to evaluate generalization and delivery impact.

[Decision method](prioritization.md) · [Model audit](model-evaluation.md) · [Data lineage](data-dictionary.md)
