# UAT Test Cases — Appeals Friction Radar

Environment: local build, synthetic dataset, seed 20260119.
Tester role in brackets. Result column filled during execution.

| ID | Story | Test | Steps | Expected result | Result |
|---|---|---|---|---|---|
| UAT-01 | US-01 | SLA risk queue contains only open cases [Ops Manager] | Open SLA Risk Queue, check Status column values | No row has Status = Closed; row count equals 189 open cases | Pass |
| UAT-02 | US-02 | Stage dwell time comes from the event log [Intake Supervisor] | Compare Friction Radar heat map to query 6 output | Values match within rounding; transition counts shown | Pass |
| UAT-03 | US-03 | Documentation split is correct [Quality Lead] | Compare visual to query 8 | Rework 31.7% incomplete vs 7.7% complete; denominators visible | Pass |
| UAT-04 | US-01 | SLA proximity flag fires [Ops Manager] | Sort by SLA days remaining ascending | Every row at 2 days or fewer is red; 3 to 5 amber | Pass |
| UAT-05 | US-04 | First-pass routing accuracy calculation [Ops Director] | Check claims payment value against query 4 | 81.7%, lowest of all appeal types | Pass |
| UAT-06 | US-05 | Handoff impact grouping [Workforce Manager] | Check turnaround by reassignment count | 13.4 / 18.3 / 25.6 / 28.4 days for 0 / 1 / 2 / 3 handoffs | Pass |
| UAT-07 | US-06 | Pending-information threshold configurable [Clinical Lead] | Change threshold from 5 to 3 days | Row count increases, no code change required | Pass |
| UAT-08 | US-07 | Escalation drivers resolve to reason descriptions [Quality Lead] | Inspect delay reason chart | Every bar shows a description from dim_reason_code, no raw codes | Pass |
| UAT-09 | US-08 | Data Quality Score matches the pipeline [Reporting Analyst] | Compare card to clean_validate.py output | Both show 98.71% | Pass |
| UAT-10 | US-08 | Blocked records reconcile [Reporting Analyst] | Check reconciliation card | 4,018 in minus 3,966 reported equals 52 excluded or deduplicated | Pass |
| UAT-11 | US-09 | Executive KPIs match documented definitions [Leadership] | Cross-check each card to the data dictionary | All seven match; month grain is received date | Pass |
| UAT-12 | US-10 | Friction components sum to the total [Intake Supervisor] | Drill into three Critical cases | Component points sum exactly to the displayed score | Pass |

## Negative tests

| ID | Test | Expected result | Result |
|---|---|---|---|
| UAT-N1 | Load an appeal with closed date before received date | Record excluded, DQ-06 exception written | Pass |
| UAT-N2 | Load a closed appeal with blank outcome | Record excluded, DQ-02 exception written | Pass |
| UAT-N3 | Load an appeal with payer code ` pay-02 ` | Standardized to PAY-02, joins successfully | Pass |
| UAT-N4 | Load a duplicate Appeal_ID | First kept, DQ-01 exception written, no double count | Pass |
| UAT-N5 | Set SLA_Target_Days to 0 | DQ-10 exception written, no default substituted | Pass |

## Open defects

| ID | Description | Severity | Status |
|---|---|---|---|
| D-01 | Low-friction cases still miss SLA 41% of the time because 7-day targets are not reflected in the score. Score needs an SLA-target term or the queue must always be sorted by days remaining first. | Medium | Open, documented as a calibration item |
| D-02 | DQ-13 to DQ-15 are specified but not automated. | Low | Open |
