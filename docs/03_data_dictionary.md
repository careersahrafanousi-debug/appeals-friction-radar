# Data Dictionary — Appeals Friction Radar

All tables are synthetic. Owner column names the fictional role accountable for the field
definition.

## appeals_fact — one row per appeal

| Field | Type | Definition | Allowed values | Required | Example | Quality rule | Owner |
|---|---|---|---|---|---|---|---|
| Appeal_ID | text | Unique appeal identifier | `APL-YYYY-######` | Yes | APL-2026-000001 | DQ-01 unique | Appeals Ops Manager |
| Received_Date | date | Date the appeal arrived | — | Yes | 2026-01-05 | DQ-05 chain order | Intake Supervisor |
| Intake_Completed_Date | date | Date intake logging and validation finished | — | Yes | 2026-01-06 | DQ-05 | Intake Supervisor |
| Assigned_Date | date | Date routed to a review team | — | Yes | 2026-01-07 | DQ-05 | Intake Supervisor |
| Review_Started_Date | date | Date a reviewer opened the case | — | Yes | 2026-01-10 | DQ-05 | Clinical Review Lead |
| Decision_Date | date | Date the determination was made | — | If closed | 2026-01-19 | DQ-05 | Clinical Review Lead |
| Closed_Date | date | Date the case was closed in the system | — | If closed | 2026-01-20 | DQ-03, DQ-04, DQ-06 | Appeals Ops Manager |
| Appeal_Type | text | Category of appeal | Clinical, Administrative, Authorization, Pharmacy, Claims Payment | Yes | Clinical | reference list | Appeals Ops Manager |
| Priority | text | Handling priority | Urgent, Standard, Low | Yes | Urgent | reference list | Appeals Ops Manager |
| Payer_ID | text | Payer reference key | must exist in dim_payer | Yes | PAY-01 | DQ-08 | Data Steward |
| Initial_Team_ID | text | Team the case was first routed to | must exist in dim_team | Yes | TM-01 | DQ-09 | Data Steward |
| Final_Team_ID | text | Team that held the case at decision | must exist in dim_team | Yes | TM-03 | DQ-09 | Data Steward |
| Status | text | Current case state | Closed, In Review, Pending Information, Escalated | Yes | In Review | DQ-07 | Appeals Ops Manager |
| Outcome | text | Determination | Upheld, Overturned, Partially Overturned | If closed | Overturned | DQ-02 | Clinical Review Lead |
| SLA_Target_Days | integer | Contractual turnaround target | 7, 14, 30 | Yes | 7 | DQ-10 | Quality Lead |
| Documentation_Complete | text | Whether intake documentation was complete | Yes, No | Yes | Yes | DQ-11 | Intake Supervisor |
| Rework_Flag | text | Review had to be redone | Yes, No | Yes | No | DQ-11 | Quality Lead |
| Escalation_Flag | text | Case was escalated | Yes, No | Yes | Yes | DQ-11 | Clinical Review Lead |
| Reassignment_Count | integer | Times the case changed teams | 0–6 | Yes | 2 | DQ-12 | Appeals Ops Manager |
| Pending_Info_Days | integer | Days spent waiting on outside records | 0–60 | Yes | 7 | range check | Clinical Review Lead |
| Reason_Code | text | Primary driver reason code | must exist in dim_reason_code | Yes | RC-01 | reference list | Quality Lead |
| Final_Routing_Correct | text | Initial routing was never corrected | Yes, No | Yes | No | DQ-11 | Intake Supervisor |

### Derived fields added by `clean_validate.py`

| Field | Definition |
|---|---|
| Turnaround_Days | `Closed_Date - Received_Date`, closed cases only |
| Intake_Days | `Intake_Completed_Date - Received_Date` |
| Routing_Days | `Assigned_Date - Intake_Completed_Date` |
| Review_Wait_Days | `Review_Started_Date - Assigned_Date` |
| Review_Days | `Decision_Date - Review_Started_Date` |
| Closure_Days | `Closed_Date - Decision_Date` |
| SLA_Met | Yes when `Turnaround_Days <= SLA_Target_Days`, closed cases only |
| Friction_Score | Weighted sum, see README |
| Friction_Category | Low / Moderate / High / Critical band of Friction_Score |

## appeal_events — one row per workflow event

| Field | Type | Definition | Example |
|---|---|---|---|
| Event_ID | text | Unique event key | EVT-0000001 |
| Appeal_ID | text | Foreign key to appeals_fact | APL-2026-000001 |
| Event_Timestamp | datetime | When the event occurred | 2026-01-06 09:15:00 |
| Process_Stage | text | Intake, Validation, Classification, Routing, Review, Information Request, Escalation, Decision, Closure | Routing |
| Event_Type | text | Specific action recorded | Case Reassigned |
| Team_ID | text | Team holding the case at that moment | TM-03 |
| User_Role | text | Role performing the action | Reviewer |
| Delay_Reason | text | Reason code when the event represents a delay, else null | RC-04 |
| Event_Sequence | integer | Order of the event within the appeal | 6 |

## dim_payer

| Field | Definition |
|---|---|
| Payer_ID | Primary key, `PAY-##` |
| Payer_Name | Fictional payer name |
| Payer_Type | Commercial, Medicaid, Medicare Advantage |

## dim_team

| Field | Definition |
|---|---|
| Team_ID | Primary key, `TM-##` |
| Team_Name | Team label |
| Team_Function | Clinical or Administrative |
| Headcount | Reviewers assigned to the team |

## dim_reason_code

| Field | Definition |
|---|---|
| Reason_Code | Primary key, `RC-##` |
| Reason_Description | Plain-language reason |
| Reason_Category | Documentation, Intake, Authorization, Routing, Eligibility, Clinical, Coding, Capacity, Policy, Technology, Escalation |

## dim_date

| Field | Definition |
|---|---|
| Date_Key | Calendar date, primary key |
| Year, Quarter, Month_Num, Month_Name, Day_Name | Calendar attributes |
| Is_Weekend | True for Saturday and Sunday |

## dq_exceptions

| Field | Definition |
|---|---|
| Exception_ID | Primary key |
| Rule_ID | Rule that failed, see `07_data_quality_rules.md` |
| Record_ID | Appeal ID that failed |
| Severity | Critical, High, Medium, Low |
| Description | What failed, in plain language |
| Owner | Role accountable for resolution |
| Status | Open, In Progress, Resolved |
