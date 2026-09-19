# Business Requirements — Appeals Friction Radar

## 1. Background

See `01_project_charter.md`. This document translates the charter into user stories,
acceptance criteria, and non-functional requirements.

## 2. User stories

**US-01 — SLA risk queue**
As an appeals operations manager, I want open appeals ranked by SLA days remaining and
friction score so that I can allocate review capacity before deadlines are missed.
*Acceptance criteria:* queue lists only cases where `Status <> 'Closed'`; sortable by SLA
days remaining and by friction score; cases within 2 days of SLA are visually flagged;
friction score 60+ shows as Critical; row drill-through opens the full event history.

**US-02 — Stage delay visibility**
As an intake supervisor, I want average and worst dwell time per process stage so that I
can tell whether delay sits in intake, routing, or review.
*Acceptance criteria:* dwell time derived from `appeal_events`, not milestone columns;
filterable by appeal type, payer, and team; shows count of transitions behind each average.

**US-03 — Documentation impact**
As a quality lead, I want rework rate and SLA miss rate split by documentation
completeness so that I can justify blocking intake validation.
*Acceptance criteria:* both rates shown side by side; denominator stated on the visual;
excludes open cases from SLA calculation.

**US-04 — Routing accuracy**
As an operations director, I want first-pass routing accuracy by appeal type and payer so
that I know which classification rules to fix first.
*Acceptance criteria:* accuracy = appeals never reassigned ÷ total appeals; breakdown by
type and payer; initial-to-final team pairs listed for the top misrouting flows.

**US-05 — Handoff cost**
As a workforce manager, I want turnaround and SLA miss rate by number of reassignments so
that I can quantify what each handoff costs.
*Acceptance criteria:* grouped by reassignment count 0 through 3+; closed cases only.

**US-06 — Pending information monitoring**
As a clinical review lead, I want a list of cases pending information for more than five
days so that follow-up happens before escalation.
*Acceptance criteria:* threshold configurable; shows days pending, payer, priority,
assigned team, and SLA days remaining.

**US-07 — Escalation drivers**
As a quality lead, I want escalation volume by delay reason so that I can see what is
actually triggering escalations.
*Acceptance criteria:* sourced from event-level delay reasons joined to the reason
dimension; ordered by volume.

**US-08 — Data quality transparency**
As a reporting analyst, I want a data-quality page showing rule failures by severity and
which records were excluded from reporting so that I can defend the numbers.
*Acceptance criteria:* Data Quality Score displayed; exceptions listed by rule and
severity; excluded record count reconciles to rows-in minus rows-reported.

**US-09 — Executive trend**
As operations leadership, I want monthly volume, backlog, SLA compliance, median turnaround
and average friction on one page so that I can review trend without opening four reports.
*Acceptance criteria:* single page; each KPI matches its definition in the data dictionary;
month grain based on received date.

**US-10 — Score explainability**
As an intake supervisor, I want to see which components contributed to a case's friction
score so that the number is actionable rather than a black box.
*Acceptance criteria:* drill-through shows each component and its points; total equals the
displayed score.

## 3. Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Event-level history retained for every appeal with stage, team, timestamp, delay reason | Must |
| FR-02 | Friction score calculated for every appeal, open or closed | Must |
| FR-03 | Records failing Critical data-quality rules excluded from reporting and logged | Must |
| FR-04 | SLA days remaining recalculated against the reporting date | Must |
| FR-05 | All KPIs traceable to a written definition | Must |
| FR-06 | Filters for payer, appeal type, priority, team, date range on every page | Must |
| FR-07 | Pending-information threshold configurable without code change | Should |
| FR-08 | Friction score components exposed at case level | Should |
| FR-09 | Exception log assignable to an owner with a status | Should |
| FR-10 | Daily refresh with a visible last-refresh timestamp | Could |

## 4. Non-functional requirements

- Reporting layer must contain no identifiers beyond a synthetic appeal ID.
- Full pipeline must run end to end in under two minutes on a laptop.
- Queries must run on SQLite with documented Postgres equivalents.
- Random seed fixed so results reproduce.
- No manual steps between raw extract and reporting layer.

## 5. Out of scope

Write-back to a case system, automated routing execution, staff performance scoring,
financial impact modeling, real-time refresh.

## 6. Traceability

| User story | Requirements | Dashboard page | UAT |
|---|---|---|---|
| US-01 | FR-02, FR-04, FR-06 | SLA Risk Queue | UAT-01, UAT-04 |
| US-02 | FR-01, FR-06 | Friction Radar | UAT-02 |
| US-03 | FR-05 | Friction Radar | UAT-03 |
| US-04 | FR-05, FR-06 | Routing & Handoff | UAT-05 |
| US-05 | FR-05 | Routing & Handoff | UAT-06 |
| US-06 | FR-04, FR-07 | SLA Risk Queue | UAT-07 |
| US-07 | FR-01 | Friction Radar | UAT-08 |
| US-08 | FR-03 | Data Quality | UAT-09, UAT-10 |
| US-09 | FR-05, FR-06 | Executive Overview | UAT-11 |
| US-10 | FR-08 | drill-through | UAT-12 |
