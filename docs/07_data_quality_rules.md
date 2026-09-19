# Data Quality Rules — Appeals Friction Radar

Severity meaning:

- **Critical** — the record cannot be used for leadership reporting. Excluded from the
  reporting layer and logged.
- **High** — material risk of a wrong KPI. Record stays in reporting, flagged for the owner.
- **Medium** — inconsistency that needs correcting but will not move a KPI.
- **Low** — cosmetic or non-material.

| Rule | Check | Severity | Action | Owner |
|---|---|---|---|---|
| DQ-01 | `Appeal_ID` is unique in the reporting layer | High | Keep first occurrence, log the duplicate | Data Steward |
| DQ-02 | Closed appeals have an outcome | Critical | Exclude, return to review team | Clinical Review Lead |
| DQ-03 | Closed appeals have a closed date | Critical | Exclude | Appeals Ops Manager |
| DQ-04 | Open appeals do not carry a closed date | High | Flag for status correction | Appeals Ops Manager |
| DQ-05 | Date chain moves forward: received ≤ intake ≤ assigned ≤ review start ≤ decision ≤ closed | Critical | Exclude | Data Steward |
| DQ-06 | Turnaround is not negative | Critical | Exclude | Data Steward |
| DQ-07 | `Status` is one of the four approved values | Medium | Standardize case, log if unmappable | Appeals Ops Manager |
| DQ-08 | `Payer_ID` exists in `dim_payer` | High | Trim and upper-case, log if still unmatched | Data Steward |
| DQ-09 | `Initial_Team_ID` and `Final_Team_ID` exist in `dim_team` | High | Log for reference-data fix | Data Steward |
| DQ-10 | `SLA_Target_Days` is populated and positive | Medium | Log, default not applied | Quality Lead |
| DQ-11 | Yes/No fields contain only Yes or No after standardizing | Medium | Map Y/N/TRUE/FALSE, log remainder | Reporting Analyst |
| DQ-12 | `Reassignment_Count` is between 0 and 6 | Low | Log only | Appeals Ops Manager |

Rules that are specified but not yet automated, kept here so the gap is visible rather than
forgotten:

| Rule | Check | Severity |
|---|---|---|
| DQ-13 | Every appeal has at least one Intake event and, if closed, a Closure event | High |
| DQ-14 | Event sequence has no gaps or repeats within an appeal | Medium |
| DQ-15 | Reporting layer refresh is no more than 24 hours old | High |

## Data Quality Score

```
Data Quality Score = distinct records with no rule failure / total records in extract x 100
```

Last run: `(4018 - 52) / 4018 = 98.71%`. Reported on the Data Quality page alongside the
count of blocked records so the two always reconcile.
