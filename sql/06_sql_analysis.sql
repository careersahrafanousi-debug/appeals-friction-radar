-- Appeals Friction Radar - analysis queries
-- Pathway Appeals Services (fictional org, fully synthetic data)
-- Written for SQLite. Notes on Postgres/T-SQL differences are inline.

--------------------------------------------------------------------
-- 1. Volume by month and appeal type
--------------------------------------------------------------------
SELECT strftime('%Y-%m', Received_Date) AS receipt_month,
       Appeal_Type,
       COUNT(*)                          AS appeals
FROM appeals_fact
GROUP BY receipt_month, Appeal_Type
ORDER BY receipt_month, appeals DESC;


--------------------------------------------------------------------
-- 2. Turnaround by payer - average and median
-- SQLite has no PERCENTILE_CONT, so the median comes from a window
-- trick. In Postgres: PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ...)
--------------------------------------------------------------------
WITH closed AS (
    SELECT Payer_ID, Turnaround_Days
    FROM appeals_fact
    WHERE Status = 'Closed' AND Turnaround_Days IS NOT NULL
),
ranked AS (
    SELECT Payer_ID,
           Turnaround_Days,
           ROW_NUMBER() OVER (PARTITION BY Payer_ID ORDER BY Turnaround_Days) AS rn,
           COUNT(*)     OVER (PARTITION BY Payer_ID)                         AS n
    FROM closed
)
SELECT p.Payer_Name,
       p.Payer_Type,
       COUNT(*)                                     AS closed_appeals,
       ROUND(AVG(r.Turnaround_Days), 1)             AS avg_tat_days,
       ROUND(AVG(CASE WHEN r.rn IN ((r.n + 1) / 2, (r.n + 2) / 2)
                      THEN r.Turnaround_Days END), 1) AS median_tat_days
FROM ranked r
JOIN dim_payer p ON p.Payer_ID = r.Payer_ID
GROUP BY p.Payer_Name, p.Payer_Type
ORDER BY median_tat_days DESC;


--------------------------------------------------------------------
-- 3. SLA compliance by team and priority
--------------------------------------------------------------------
SELECT t.Team_Name,
       a.Priority,
       COUNT(*)                                                       AS closed_appeals,
       SUM(CASE WHEN a.SLA_Met = 'Yes' THEN 1 ELSE 0 END)             AS met,
       ROUND(100.0 * SUM(CASE WHEN a.SLA_Met = 'Yes' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                           AS sla_compliance_pct
FROM appeals_fact a
JOIN dim_team t ON t.Team_ID = a.Final_Team_ID
WHERE a.Status = 'Closed'
GROUP BY t.Team_Name, a.Priority
HAVING COUNT(*) >= 20
ORDER BY sla_compliance_pct;


--------------------------------------------------------------------
-- 4. First-pass routing accuracy by appeal type
--------------------------------------------------------------------
SELECT Appeal_Type,
       COUNT(*)                                                                AS appeals,
       SUM(CASE WHEN Final_Routing_Correct = 'Yes' THEN 1 ELSE 0 END)          AS routed_right,
       ROUND(100.0 * SUM(CASE WHEN Final_Routing_Correct = 'Yes' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                                    AS first_pass_pct
FROM appeals_fact
GROUP BY Appeal_Type
ORDER BY first_pass_pct;


--------------------------------------------------------------------
-- 5. Where the time actually goes - average days per stage
--------------------------------------------------------------------
SELECT ROUND(AVG(Intake_Days), 2)      AS intake,
       ROUND(AVG(Routing_Days), 2)     AS routing,
       ROUND(AVG(Review_Wait_Days), 2) AS wait_for_review,
       ROUND(AVG(Review_Days), 2)      AS review,
       ROUND(AVG(Closure_Days), 2)     AS closure
FROM appeals_fact
WHERE Status = 'Closed';


--------------------------------------------------------------------
-- 6. Stage dwell time from the event log
-- Uses LEAD() to measure the gap between consecutive events.
--------------------------------------------------------------------
WITH seq AS (
    SELECT Appeal_ID,
           Process_Stage,
           julianday(Event_Timestamp) AS ts,
           LEAD(julianday(Event_Timestamp)) OVER (
               PARTITION BY Appeal_ID ORDER BY Event_Sequence
           ) AS next_ts
    FROM appeal_events
)
SELECT Process_Stage,
       COUNT(*)                              AS transitions,
       ROUND(AVG(next_ts - ts), 2)           AS avg_dwell_days,
       ROUND(MAX(next_ts - ts), 2)           AS worst_dwell_days
FROM seq
WHERE next_ts IS NOT NULL
GROUP BY Process_Stage
ORDER BY avg_dwell_days DESC;


--------------------------------------------------------------------
-- 7. Does the number of handoffs change turnaround?
--------------------------------------------------------------------
SELECT Reassignment_Count                       AS handoffs,
       COUNT(*)                                 AS closed_appeals,
       ROUND(AVG(Turnaround_Days), 1)           AS avg_tat_days,
       ROUND(100.0 * SUM(CASE WHEN SLA_Met = 'No' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                     AS sla_miss_pct
FROM appeals_fact
WHERE Status = 'Closed'
GROUP BY Reassignment_Count
ORDER BY handoffs;


--------------------------------------------------------------------
-- 8. Documentation completeness vs rework and SLA
--------------------------------------------------------------------
SELECT Documentation_Complete,
       COUNT(*)                                                        AS appeals,
       ROUND(100.0 * SUM(CASE WHEN Rework_Flag = 'Yes' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                            AS rework_pct,
       ROUND(100.0 * SUM(CASE WHEN SLA_Met = 'No' THEN 1 ELSE 0 END)
             / SUM(CASE WHEN Status = 'Closed' THEN 1 ELSE 0 END), 1)  AS sla_miss_pct,
       ROUND(AVG(Friction_Score), 1)                                   AS avg_friction
FROM appeals_fact
GROUP BY Documentation_Complete;


--------------------------------------------------------------------
-- 9. Open cases pending information more than 5 days
--------------------------------------------------------------------
SELECT a.Appeal_ID,
       p.Payer_Name,
       a.Appeal_Type,
       a.Priority,
       a.Pending_Info_Days,
       a.Friction_Score,
       a.Friction_Category,
       a.SLA_Target_Days - CAST(julianday('2026-09-30') - julianday(a.Received_Date) AS INT)
           AS sla_days_remaining
FROM appeals_fact a
JOIN dim_payer p ON p.Payer_ID = a.Payer_ID
WHERE a.Status <> 'Closed'
  AND a.Pending_Info_Days > 5
ORDER BY sla_days_remaining, a.Friction_Score DESC
LIMIT 50;


--------------------------------------------------------------------
-- 10. Top friction reasons from the event log
--------------------------------------------------------------------
SELECT r.Reason_Category,
       r.Reason_Description,
       COUNT(*) AS delay_events
FROM appeal_events e
JOIN dim_reason_code r ON r.Reason_Code = e.Delay_Reason
GROUP BY r.Reason_Category, r.Reason_Description
ORDER BY delay_events DESC;


--------------------------------------------------------------------
-- 11. Friction category vs actual SLA outcome
-- This is the sanity check on the score. If the categories don't
-- separate SLA misses, the weights are wrong.
--------------------------------------------------------------------
SELECT Friction_Category,
       COUNT(*)                                                  AS closed_appeals,
       ROUND(AVG(Turnaround_Days), 1)                            AS avg_tat_days,
       ROUND(100.0 * SUM(CASE WHEN SLA_Met = 'No' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                      AS sla_miss_pct
FROM appeals_fact
WHERE Status = 'Closed'
GROUP BY Friction_Category
ORDER BY sla_miss_pct;


--------------------------------------------------------------------
-- 12. Backlog aging buckets
--------------------------------------------------------------------
SELECT CASE
           WHEN julianday('2026-09-30') - julianday(Received_Date) <= 7  THEN '0-7 days'
           WHEN julianday('2026-09-30') - julianday(Received_Date) <= 14 THEN '8-14 days'
           WHEN julianday('2026-09-30') - julianday(Received_Date) <= 30 THEN '15-30 days'
           ELSE '30+ days'
       END AS age_bucket,
       COUNT(*)                      AS open_appeals,
       ROUND(AVG(Friction_Score), 1) AS avg_friction
FROM appeals_fact
WHERE Status <> 'Closed'
GROUP BY age_bucket
ORDER BY open_appeals DESC;


--------------------------------------------------------------------
-- 13. Data quality exceptions by severity and rule
--------------------------------------------------------------------
SELECT Rule_ID, Severity, COUNT(*) AS exceptions
FROM dq_exceptions
GROUP BY Rule_ID, Severity
ORDER BY exceptions DESC;


--------------------------------------------------------------------
-- 14. Misrouting concentration - which initial team sends work away
--------------------------------------------------------------------
SELECT ti.Team_Name AS initial_team,
       tf.Team_Name AS final_team,
       COUNT(*)     AS appeals
FROM appeals_fact a
JOIN dim_team ti ON ti.Team_ID = a.Initial_Team_ID
JOIN dim_team tf ON tf.Team_ID = a.Final_Team_ID
WHERE a.Initial_Team_ID <> a.Final_Team_ID
GROUP BY initial_team, final_team
ORDER BY appeals DESC
LIMIT 20;
