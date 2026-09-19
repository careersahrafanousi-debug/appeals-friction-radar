# Project Charter — Appeals Friction Radar

**Project name:** Appeals Friction Radar
**Organization:** Pathway Appeals Services (fictional)
**Prepared by:** Business analyst / reporting analyst
**Date:** 2026-01-19
**Status:** Prototype, portfolio build

## Problem statement

Pathway Appeals Services processes about 10,000 appeals per quarter. SLA misses are visible
in monthly reporting, but the organization cannot isolate which workflow step causes the
delay. Intake, routing, clinical review, and closure each blame a different step, and there
is no event-level data to settle it. Improvement work is therefore unprioritized.

## Goal

Produce a measured view of where appeals lose time, a transparent per-case friction score
that flags SLA risk while a case is still open, and a redesigned workflow with the intake
and routing controls the data supports.

## Objectives

1. Model the appeals workflow at event level rather than milestone level.
2. Quantify dwell time for each process stage.
3. Measure the effect of incomplete documentation, incorrect routing, and handoffs on
   turnaround and SLA compliance.
4. Produce a prototype friction score that ranks open cases by risk.
5. Document requirements, acceptance criteria, and UAT so the prototype is implementable.

## Users

| User | Primary use |
|---|---|
| Appeals operations manager | Capacity allocation, daily SLA risk queue |
| Intake supervisor | Intake completeness and classification accuracy |
| Clinical review lead | Queue dwell time, escalation volume |
| Quality / compliance lead | Exception tracking, documentation controls |
| Reporting analyst | KPI definitions, refresh, data quality |
| Operations leadership | Monthly trend and certified figures |

## Success measures

| Measure | Baseline (modeled) | Target direction |
|---|---|---|
| SLA compliance | 49.6% | Increase |
| First-pass routing accuracy | 87.4% overall, 81.7% claims payment | Increase |
| Rework rate | 13.5% overall | Decrease |
| Median turnaround | 14.9 days average | Decrease |
| Documentation completeness | 75.9% | Increase |
| Open Critical-friction cases | Tracked daily | Decrease |
| Data Quality Score | 98.71% | Maintain above 98% |

Baselines come from the synthetic dataset. In a real engagement these would be pulled from
production and agreed with the data owner before any target is set.

## Scope

**In scope:** first-level appeals, receipt through closure, all appeal types, all review
teams, intake and routing controls, reporting and data-quality layer.

**Out of scope:** external / independent review, grievances, member correspondence content,
claim payment amounts, staffing models, vendor systems.

## Assumptions

- SLA targets are set by appeal type and priority and do not change mid-case.
- Weekends are non-working; holidays are not modeled.
- Cases open at the reporting cutoff are not counted as SLA misses.
- Friction Score weights are provisional and require stakeholder calibration.
- No production data is used at any point.

## Constraints

- Synthetic data only; no access to a case management system.
- Single analyst, no development resource, so all logic must run in Python, SQL, and a BI tool.
- Score must stay explainable to non-technical reviewers, which rules out opaque models.

## Risks

| Risk | Mitigation |
|---|---|
| Score treated as validated before calibration | Labelled prototype in every artifact; category thresholds documented |
| Teams read the friction score as a performance rating | Score is case-level, documented as a workflow measure not a staff measure |
| Data-quality exceptions ignored | Critical failures block records from reporting rather than being auto-corrected |
| Scope creep into staffing analysis | Explicit out-of-scope list, revisited at each review |

## Deliverables

Charter, business requirements with user stories, data dictionary, synthetic dataset,
cleaning and validation script with exception log, SQL analysis library, data-quality rule
set, as-is and to-be process maps, dashboard specification, UAT test cases, executive
summary.
