# Roadmap decision and sensitivity

Score discretionary initiatives using [Intercom’s RICE framework](https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers). The adapted reach input is **distinct known reporters in the July–September feedback cohort × the share estimated to be eligible for the proposed fix**. A person reporting the same theme several times contributes one unit. An anonymous report remains evidence and adds zero to identified-user reach. A user can count for multiple candidates. The cohort is a proxy for observed demand. Reach is neither an active-user denominator nor a forecast of how many people will use the feature.

**Impact per eligible reporter:** 0.25 minimal, 0.5 small, 1 medium, 2 high, 3 massive. Restore a blocked core workflow at the high end. Use small impact for reducing interruptions where work continues. Impact is a planning judgment. **Confidence:** a discount for evidence, fix fit and delivery uncertainty. It is distinct from classifier accuracy. **Effort:** total person-months across product, design, engineering and QA. Values are scenario estimates for this fictional case.

| Rank | Proposed work | Identified reporters | Base eligibility | Base impact | Base confidence | Base effort | Base RICE |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Recover stalled approvals | 394 | 80% | 2 | 80% | 3.5 | 144.1 |
| 2 | Bundle comment notifications | 292 | 80% | 0.5 | 75% | 2.5 | 35.0 |
| 3 | Show sync status and recovery | 220 | 65% | 1 | 65% | 4.0 | 23.2 |
| 4 | Make large exports resumable | 224 | 55% | 1 | 65% | 3.5 | 22.9 |
| 5 | Preview guest access | 132 | 60% | 1 | 60% | 3.0 | 15.8 |
| 6 | Boost exact task matches | 159 | 60% | 0.5 | 65% | 2.5 | 12.4 |

### What changes the decision

Approval recovery's base reach proxy is **315.2 reporter-equivalents** (394 × 0.80). Fractional values preserve the scenario arithmetic. The low/base/high scores are **19.9 / 144.1 / 404.2**. The model combines low reach, impact and confidence with high effort for the downside. The upside reverses those assumptions. These are planning scenarios.

Approval leads all eight shared one-factor stresses. The runner-up wins at base against approval's downside (**35.0 vs 19.9**) and at its own upside against approval's base (**157.2 vs 144.1**). At approval's base impact, confidence and effort, eligibility would have to drop below **19.5%** for notifications to win at their base score. This is a one-input threshold. Sync and export are nearly tied, so investigate delivery risk before allocating either team.

| Opportunity | Owner and next step | Evidence to request |
|---|---|---|
| Approval recovery | Workflow PM · Prototype admin reassignment | Audit failed approval transitions. Verify which reports describe an unavailable assignee and how often current delegation works. |
| Comment digest | Engagement PM · Discovery | Review opt-outs and interview users about time-sensitive alerts. Protect urgent alerts from batching. |
| Sync recovery | Integrations PM · Technical spike | Separate delayed updates from duplicate writes. Measure each connector's failure modes. |
| Resumable exports | Reporting PM · Technical spike | Quantify interrupted jobs by size. Keep field mapping and date format defects in their own work items. |
| Guest access preview | Platform PM · Security review | Confirm which cases stem from setup confusion. Route suspected access exposure directly to incident triage. |
| Exact search matches | Discovery PM · Discovery | Run known-title and task-ID retrieval checks. Separate relevance from indexing delays. |

Before seeking delivery approval, manually review a proposed stratified sample of 50 approval reports and 30 unclassified reports, including segment and channel diversity. Verify eligibility, manually search for misses, and compare projected scope with event telemetry. Interview five workflow administrators and obtain an engineering estimate. Re-run the decision if verified eligibility, effort, or safety requirements change. Those sample sizes are a proposed discovery budget.
