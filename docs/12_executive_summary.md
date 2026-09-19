# Executive Summary — Appeals Friction Radar

**Pathway Appeals Services (fictional) | Prepared by the reporting analyst | 2026-09-30**

## Why this was done

SLA misses were visible in monthly reporting, but no one could say which step caused them.
Intake, routing, and clinical review each pointed at a different cause. This analysis
rebuilt the appeals workflow at event level — about 35,000 events across 3,966 appeals — so
delay could be attributed to a specific stage instead of debated.

## What the data shows

**1. Intake documentation is the root cause, not reviewer speed.**
Appeals arriving with incomplete documentation had a 31.7% rework rate. Appeals arriving
complete had 7.7%. Average friction score was 47.5 versus 7.2. Roughly a quarter of intake
volume is incomplete, and nearly everything downstream traces back to it.

**2. Every handoff costs about five days.**
Average turnaround was 13.4 days with no reassignment, 18.3 with one, 25.6 with two, and
28.4 with three. SLA miss rate went from 46% to 83% across the same range. Handoffs are a
consequence of weak intake and judgment-based routing, so they are addressable.

**3. A third of closed-case time is not review work.**
Of 14.9 average days, 9.1 are review and 5.8 are intake, routing, waiting for a reviewer to
pick the case up, and closure. The wait between assignment and review start alone averages
1.6 days.

**4. Claims payment appeals are misrouted most.**
First-pass routing accuracy was 81.7% for claims payment against 87–89% elsewhere. That is
a classification rule gap at intake, not a reviewer capability issue.

**5. Risk is predictable before the deadline is missed.**
The prototype friction score separates outcomes cleanly: SLA miss rate of 41% for Low
friction, 56% Moderate, 75% High, 91% Critical. Cases can be triaged while still open.

## Recommendations

| Priority | Action | Rationale |
|---|---|---|
| 1 | Make intake validation blocking, with a named-owner exception queue | Addresses the root driver behind rework, handoffs, and escalation |
| 2 | Replace judgment routing with documented rules, starting with claims payment | Lowest first-pass accuracy, clearest rule gap |
| 3 | Mandate day 3 and day 5 follow-up on records requests | Escalations concentrate past day 5 |
| 4 | Give supervisors a daily Critical-friction queue sorted by SLA days remaining | Turns the score into an action rather than a report |
| 5 | Add first-pass routing accuracy to the weekly quality review | Keeps routing rules calibrated |

## What this does not claim

No savings figure is attached to any recommendation. The dataset is synthetic, the
relationships in it were modeled deliberately, and the friction score weights came from the
process map rather than from fitting to outcomes. Before operational use the score needs
calibration against real outcomes, sign-off from intake and clinical review, and a defined
review cycle. The score also under-weights short-SLA work: cases with a 7-day target miss
SLA at meaningful rates even when friction is Low, so the operational queue must sort by
SLA days remaining first and friction second.

## Next steps

1. Validate the intake completeness definition with the intake supervisor.
2. Calibrate score weights against a historical sample and re-test category separation.
3. Pilot the routing rules on claims payment appeals for one month.
4. Stand up the data-quality exception log with named owners before the dashboard is
   distributed to leadership.
