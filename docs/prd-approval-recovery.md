# PRD · Recover stalled approvals

**Status:** proposed discovery and pilot. **Owner:** Workflow PM. **Partners:** workflow engineering, design, support operations, security and analytics. **Decision basis:** synthetic feedback analysis. Product telemetry and customer validation are pilot prerequisites.

## Problem and target user

A purchase, launch, or other workflow may wait for sign-off after its assigned approver loses access. The requester can see a pending state but may need to start over to move the work forward. Recreating a request can lose context, duplicate work and make its history difficult to reconstruct. Workspace admins need a way to reassign the pending step within existing approval policy.

In the decision cohort, 469 reports discussed approval handoffs. There were 394 identified reporters across 235 accounts, and the classifier flagged 164 possible blockers. The category includes delegation and routing requests that may fall outside this release. Discovery must establish the eligible fraction and baseline recovery rate.

## Scope

For a single pending approval step whose assigned user has become inactive or lost required access, an authorized workflow admin can select an eligible replacement. The change preserves the request, attachments, policy version, and audit history. The initial rollout covers an explicit allowlist of workspaces and approval policies. Future work may include vacation scheduling, automatic reassignment, multi-step or parallel quorum changes, and bulk operations.

### User stories and acceptance criteria

| ID | User story | Acceptance criteria |
|---|---|---|
| PRD-01 | As a requester, I can see why my approval has stalled. | If an assigned approver loses access while a request is pending, the requester sees “Approver unavailable” and a route to contact an admin. Existing access rules apply to all visible details. |
| PRD-02 | As an authorized admin, I can replace the assignee. | The picker lists only active, eligible approvers for the current request. The server re-checks admin permission, tenant, separation-of-duties rules, pending status, candidate eligibility, and current version before writing. An empty list offers a support path. |
| PRD-03 | As a requester, I keep the original request and context. | Successful reassignment changes only the assignee and version. Request ID, policy version, submitted fields, attachments, prior state history and original submission time stay available. |
| PRD-04 | As the new approver, I am told where action is needed. | A notification is queued after commit. Delivery retries are idempotent. A delivery failure is surfaced to operations and the pending step remains available in the app. |
| PRD-05 | As the former assignee, I can no longer action the request. | An existing link can read only what current permissions allow. A stale approval attempt fails server-side and writes a denied-action audit entry. |
| PRD-06 | As an auditor, I can reconstruct the reassignment. | An append-only event records request ID, step ID, policy version, workspace, old and new assignees, admin actor, reason and timestamp. It follows existing audit access and retention. |
| PRD-07 | As an admin, I can recover from retries and concurrent changes. | Repeated submission with the same idempotency key returns the prior result. A competing reassignment or terminal decision causes a version conflict and prompts refresh. The reassignment and audit event commit atomically. |

## Workflow and failure states

1. A pending step becomes eligible when the current assignee is inactive or no longer authorized. Preserve the original assignee on the step until an authorized reassignment commits.
2. The admin opens recovery from the request detail, selects an eligible approver, enters a reason code, and confirms.
3. The server validates policy and request version at write time. Commit the assignee change, audit event and notification outbox entry together. The request remains pending.
4. The new approver proceeds through the existing approve/reject workflow. The requester sees the updated approver only if entitled to view that information.

Reject cross-tenant identities and self-approval that violates policy. An eligibility change, stale version or terminal step returns a clear error and leaves the last valid state intact. Avoid including raw customer feedback or request contents in analytics events. Use opaque IDs, policy versions and enumerated reason codes. Security validates access checks and audit visibility before any rollout.

## Instrumentation and measurement

| Event | Trigger | Required attributes |
|---|---|---|
| `approval_recovery_eligible` | First transition to unavailable on an eligible pending step | workspace and step IDs, policy version, incident key, eligibility time and reason |
| `approval_reassignment_attempted` | Server receives a confirmed recovery command | incident key, step ID, rollout arm, actor role, request version, reason code |
| `approval_reassignment_result` | Command accepts, fails or conflicts | incident key, outcome and error code, latency, idempotency key |
| `approval_decision_recorded` | Valid approval or rejection commits | incident key, step ID, decision type and time |
| `approval_recovery_notification_result` | Delivery attempt resolves | incident key, outcome, retry number |

**Primary metric:** share of first eligible incidents per step with a valid approval or rejection within 24 hours of eligibility. Count both arms using the same server-side eligibility event. Include incidents with a full 24-hour observation window and treat a canceled step without a decision as unsuccessful. Deduplicate by step and incident key.

**Secondary:** time to valid decision among recovered steps, manual workaround frequency from interviews, reassignment acceptance rate, duplicate notifications and support contacts per eligible incident. Report counts and uncertainty alongside rates. Time among recovered steps is descriptive because recovery changes who enters that group.

**Proposed success gate:** at least **+15 percentage points** in 24-hour resolution for eligible incidents, with an interval that excludes zero if the pilot has adequate power. Establish baseline and size the workspace-randomized pilot after two weeks of telemetry. Small pilots can establish usability and reliability and inform a later efficacy test. Evaluate using assignment to pilot arm and account for clustering at workspace level.

**Safety gates:** any confirmed unauthorized reassignment, cross-tenant disclosure or missing audit event stops the pilot. Investigate notification failure above 2% of committed recoveries or repeated duplicate deliveries. Establish an acceptable error baseline and minimum observation window with engineering before ramping.

## Rollout and ownership

- **Discovery:** Workflow PM reviews report samples and interviews admins. Analytics verifies eligibility and estimates the baseline. Engineering estimates state-machine and policy changes. Security checks the threat model.
- **Internal QA:** test inactive and reactivated approvers, expired sessions, concurrent admin actions, terminal races, permission loss, cross-tenant IDs, audit completeness, and outbox retries. Verify state invariants and event joins.
- **Opt-in pilot:** allowlist workspaces and retain a workspace-level comparison group where feasible. Support documents the recovery path. Analytics reports the primary and safety metrics weekly.
- **Ramp:** proceed after the evidence and safety gates are met. A kill switch disables new reassignment commands. Keep already committed reassignments and their audit events. Existing support escalation stays available.

**Open decisions:** Which policy families are allowed in the first pilot? Should loss of delegated reviewer access use the same eligibility event? What existing event data can separate a temporarily absent approver from an account that has lost permissions? Workflow PM and security own those decisions before engineering commitment.
