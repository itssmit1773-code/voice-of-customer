# Decision brief

Relayboard is a fictional work-management SaaS used by distributed operations teams. Its product managers review support tickets, in-app feedback and public reviews before quarterly planning. The channels overlap, report volumes vary by segment, and users who complain repeatedly can dominate raw message counts. The Workflow PM has capacity to prototype one improvement before asking engineering for a delivery commitment.

**Decision owner:** Workflow PM. **Decision cohort:** 1 July to 30 September 2026. **Trend context:** April to September 2026. **Decision requested:** choose a prototype, identify its verification gates, and give the other opportunities owners and next steps.

| Stakeholder | Question | Evidence or action |
|---|---|---|
| Product leadership | Which work should enter discovery first and what could change the ranking? | Ranked RICE inputs, downside and runner-up upside stress tests |
| Workflow PM | Which failure is frequent enough to investigate and where does it concentrate? | Theme share, segment denominators, identified reporters and row-level examples |
| Support operations | Which messages need someone to check the classification or severity? | Review reasons and filtered evidence export |
| Security | Could a guest access report indicate an exposure? | Expedite flagged records through existing incident triage |
| Engineering | What behavior should the first approval recovery prototype support? | State transitions, permissions, event contract, QA and rollout gates in the PRD |
| Analytics | Do counts reconcile, and how often does the classifier abstain? | Source-to-canonical audit, SQL tests and holdout validation |

## Analyst requirements

| ID | User story | Acceptance criterion |
|---|---|---|
| BA-01 | As an analyst, I can trace a report back to the channel extract. | Each source ID appears once as a retained report or a mapped duplicate. Canonical source fields follow the first event. |
| BA-02 | As a PM, I can distinguish report volume from reach. | Distinct users use known IDs only. Report share uses all filtered canonical reports, including unclassified. Distinct counts can overlap by theme. |
| BA-03 | As a PM, I can compare the same theme across regions, channels and segments. | Filters intersect and constrain charts, counts and exports. Segment share uses all reports in the respective filtered segment. |
| BA-04 | As a support lead, I can inspect suspect labels. | Ambiguous labels, possible blockers and selected access phrases produce review flags with a reason. |
| BA-05 | As a decision owner, I can challenge a candidate score. | Score input units, low/base/high assumptions and ranking sensitivity are visible and exportable. |
| BA-06 | As an engineering lead, I can review the proposed work before committing. | Top candidate has acceptance tests, telemetry and a staged release proposal. |
| BA-07 | As a reviewer, I can reproduce the cohort on a clean checkout. | One command rebuilds the warehouse from the authored source library. A separate test command checks decision values and app behavior. |

## Metric contract

- **Feedback reports** count deduplicated canonical records in scope. **Theme share** divides a theme's reports by all reports in the same scope.
- **Identified reporters** count distinct non-null user IDs. **Reporting accounts** count distinct account IDs and include records without a user ID.
- **Reported blockers** in this project are predicted text labels. They count reports with an explicit indication of interrupted work. The dashboard also shows uncertain severity for the selected theme.
- **Monthly share** recomputes its denominator for each month and filter selection. Months with zero in-scope reports have no defined share.
- **Review workload** counts reports with one or more flags. It includes flags even where the theme was classified.
- **Modeled reach** starts with identified reporters in the decision quarter and applies a candidate-specific eligibility assumption.
