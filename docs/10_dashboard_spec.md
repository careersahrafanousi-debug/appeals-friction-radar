# Dashboard Specification — Appeals Friction Radar

Target tool: Power BI. The `.pbix` is intentionally not committed — it is a binary that
does not diff in git. Everything needed to rebuild it is here: model, measures, pages,
and interactions.

## Model

Star schema. `appeals_fact` and `appeal_events` are the fact tables. `dim_payer`,
`dim_team`, `dim_reason_code`, and `dim_date` are single-direction one-to-many
relationships filtering the facts. `appeal_events` joins to `appeals_fact` on `Appeal_ID`
and to `dim_team` on `Team_ID`. `dim_date` joins to `Received_Date` with an inactive
relationship to `Closed_Date` for closure-based reporting via `USERELATIONSHIP`.

## Core measures (DAX)

```
Appeals = COUNTROWS(appeals_fact)

Open Backlog = CALCULATE([Appeals], appeals_fact[Status] <> "Closed")

Closed Appeals = CALCULATE([Appeals], appeals_fact[Status] = "Closed")

Median TAT = MEDIAN(appeals_fact[Turnaround_Days])

SLA Compliance % =
DIVIDE(
    CALCULATE([Appeals], appeals_fact[SLA_Met] = "Yes"),
    [Closed Appeals]
)

First Pass Routing % =
DIVIDE(
    CALCULATE([Appeals], appeals_fact[Final_Routing_Correct] = "Yes"),
    [Appeals]
)

Rework Rate % =
DIVIDE(CALCULATE([Appeals], appeals_fact[Rework_Flag] = "Yes"), [Appeals])

Avg Friction Score = AVERAGE(appeals_fact[Friction_Score])

Critical Friction Open =
CALCULATE([Appeals],
    appeals_fact[Status] <> "Closed",
    appeals_fact[Friction_Category] = "Critical friction")

SLA Days Remaining =
appeals_fact[SLA_Target_Days] - DATEDIFF(appeals_fact[Received_Date], TODAY(), DAY)
```

## Pages

### 1. Executive Overview
Cards: appeals received, open backlog, SLA compliance %, median turnaround, first-pass
routing %, rework rate, average friction score.
Visuals: monthly volume column chart with SLA compliance on a secondary line; backlog
aging bar; friction category donut.
Filters: date range, payer, appeal type, priority.

### 2. Friction Radar
Average friction score by appeal type, payer, team, and priority (small multiples).
Stage-delay heat map: process stage on rows, appeal type on columns, average dwell days as
the value, sourced from `appeal_events`.
Delay-reason bar chart ordered descending, joined to `dim_reason_code`.
Scatter: friction score versus turnaround days, one point per closed appeal, coloured by
SLA met — this is the visual that shows whether the score is doing any work.

### 3. Routing & Handoff Analysis
Initial-to-final team matrix with appeal counts; diagonal is correct routing.
First-pass accuracy by appeal type and payer.
Turnaround and SLA miss rate by reassignment count.
Table of top misrouting pairs with volume and average added days.

### 4. SLA Risk Queue
Operational table, open cases only: appeal ID, payer, type, priority, assigned team, days
open, SLA days remaining, friction score, friction category, documentation flag, escalation
flag, days pending information.
Conditional formatting: SLA days remaining ≤ 2 red, ≤ 5 amber. Critical friction bold red.
Default sort: SLA days remaining ascending, then friction score descending.
Drill-through to an event-history page filtered to the selected appeal.

### 5. Data Quality
Data Quality Score card. Exceptions by severity column chart. Exceptions by rule bar chart.
Table of open exceptions with owner and status. Reconciliation card: rows in extract, rows
in reporting layer, records blocked — these must tie.

### 6. Event History (drill-through only)
Timeline table for one appeal: sequence, timestamp, stage, event type, team, role, delay
reason. Gantt-style bar of time per stage. Friction score component breakdown so the total
is explainable.

## Interaction rules

- All slicers sync across pages 1 to 5 except the operational queue, which is always
  restricted to open cases regardless of the status slicer.
- Every visual with a rate shows its denominator in the tooltip.
- Any visual built on a filtered subset states the filter in the title.
