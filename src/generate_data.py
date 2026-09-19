"""
Builds the synthetic dataset for Pathway Appeals Services (fictional org).

Everything here is made up. No employer data, no PHI. The point of the
script is to produce data that behaves like an appeals queue instead of
random noise, so the downstream analysis actually has something to find.

Run:  python src/generate_data.py
"""

import os
import random
from datetime import date, timedelta

import numpy as np
import pandas as pd

SEED = 20260119
N_APPEALS = 4000
START = date(2026, 1, 1)
END = date(2026, 9, 30)

RAW = os.path.join("data", "raw")

PAYERS = [
    ("PAY-01", "Trinity Health Plan", "Commercial", 0.22),
    ("PAY-02", "Brazos Valley Benefits", "Commercial", 0.18),
    ("PAY-03", "Statewide Medicaid MCO", "Medicaid", 0.17),
    ("PAY-04", "Silver Ridge Advantage", "Medicare Advantage", 0.16),
    ("PAY-05", "Cottonwood Mutual", "Commercial", 0.11),
    ("PAY-06", "Panhandle Care Partners", "Medicaid", 0.09),
    ("PAY-07", "Meridian Select", "Commercial", 0.07),
]

TEAMS = [
    ("TM-01", "Intake Review", "Administrative", 9),
    ("TM-02", "Clinical Review A", "Clinical", 11),
    ("TM-03", "Clinical Review B", "Clinical", 10),
    ("TM-04", "Authorization Appeals", "Administrative", 8),
    ("TM-05", "Pharmacy Appeals", "Clinical", 6),
    ("TM-06", "Complex / Escalation", "Clinical", 7),
    ("TM-07", "Medicaid Appeals", "Administrative", 8),
    ("TM-08", "Quality Audit", "Administrative", 4),
]

# reason codes; the weights decide how often each one shows up
REASONS = [
    ("RC-01", "Missing clinical documentation", "Documentation", 0.14),
    ("RC-02", "Incomplete intake form", "Intake", 0.11),
    ("RC-03", "Prior authorization not on file", "Authorization", 0.10),
    ("RC-04", "Routed to wrong review team", "Routing", 0.09),
    ("RC-05", "Awaiting provider records", "Documentation", 0.09),
    ("RC-06", "Member eligibility unclear", "Eligibility", 0.07),
    ("RC-07", "Medical necessity dispute", "Clinical", 0.07),
    ("RC-08", "Coding discrepancy", "Coding", 0.06),
    ("RC-09", "Duplicate appeal submitted", "Intake", 0.05),
    ("RC-10", "Reviewer capacity constraint", "Capacity", 0.05),
    ("RC-11", "Policy exception required", "Policy", 0.04),
    ("RC-12", "Missing member signature / AOR", "Documentation", 0.04),
    ("RC-13", "System outage delay", "Technology", 0.03),
    ("RC-14", "Escalated by provider relations", "Escalation", 0.03),
    ("RC-15", "Second-level review required", "Clinical", 0.03),
]

APPEAL_TYPES = [
    ("Clinical", 0.38, 14),
    ("Administrative", 0.27, 30),
    ("Authorization", 0.18, 7),
    ("Pharmacy", 0.10, 7),
    ("Claims Payment", 0.07, 30),
]

PRIORITIES = [("Urgent", 0.17), ("Standard", 0.68), ("Low", 0.15)]

STAGES = [
    "Intake",
    "Validation",
    "Classification",
    "Routing",
    "Review",
    "Information Request",
    "Escalation",
    "Decision",
    "Closure",
]


def pick(options):
    """options is a list of (value, weight) pairs."""
    vals = [o[0] for o in options]
    wts = [o[1] for o in options]
    return random.choices(vals, weights=wts, k=1)[0]


def business_days_later(d, n):
    """Add n calendar-ish days but skip weekends, which is how a real queue moves."""
    out = d
    added = 0
    n = max(0, int(round(n)))
    while added < n:
        out += timedelta(days=1)
        if out.weekday() < 5:
            added += 1
    return out


def make_dim_tables():
    dim_payer = pd.DataFrame(
        [(p[0], p[1], p[2]) for p in PAYERS],
        columns=["Payer_ID", "Payer_Name", "Payer_Type"],
    )
    dim_team = pd.DataFrame(
        TEAMS, columns=["Team_ID", "Team_Name", "Team_Function", "Headcount"]
    )
    dim_reason = pd.DataFrame(
        [(r[0], r[1], r[2]) for r in REASONS],
        columns=["Reason_Code", "Reason_Description", "Reason_Category"],
    )

    days = pd.date_range(START, END + timedelta(days=60), freq="D")
    dim_date = pd.DataFrame({"Date_Key": days})
    dim_date["Year"] = dim_date["Date_Key"].dt.year
    dim_date["Quarter"] = "Q" + dim_date["Date_Key"].dt.quarter.astype(str)
    dim_date["Month_Num"] = dim_date["Date_Key"].dt.month
    dim_date["Month_Name"] = dim_date["Date_Key"].dt.strftime("%b")
    dim_date["Day_Name"] = dim_date["Date_Key"].dt.strftime("%a")
    dim_date["Is_Weekend"] = dim_date["Date_Key"].dt.weekday >= 5
    dim_date["Date_Key"] = dim_date["Date_Key"].dt.date
    return dim_payer, dim_team, dim_reason, dim_date


def route_team(appeal_type, payer_id):
    if appeal_type == "Pharmacy":
        return "TM-05"
    if appeal_type == "Authorization":
        return "TM-04"
    if payer_id in ("PAY-03", "PAY-06"):
        return "TM-07"
    if appeal_type == "Clinical":
        return random.choice(["TM-02", "TM-03"])
    return "TM-01"


def build_appeals():
    rows = []
    span = (END - START).days

    for i in range(1, N_APPEALS + 1):
        appeal_id = f"APL-2026-{i:06d}"
        received = START + timedelta(days=random.randint(0, span))

        appeal_type = pick([(a[0], a[1]) for a in APPEAL_TYPES])
        sla_target = dict((a[0], a[2]) for a in APPEAL_TYPES)[appeal_type]
        priority = pick(PRIORITIES)
        if priority == "Urgent":
            sla_target = min(sla_target, 7)

        payer_id = pick([(p[0], p[3]) for p in PAYERS])

        # PAY-04 skews toward authorization problems on purpose
        if payer_id == "PAY-04" and random.random() < 0.30:
            appeal_type = "Authorization"
            sla_target = 7

        # documentation completeness is the root driver of most downstream pain
        doc_complete_p = 0.80
        if appeal_type in ("Clinical", "Pharmacy"):
            doc_complete_p -= 0.10
        if payer_id in ("PAY-03", "PAY-06"):
            doc_complete_p -= 0.07
        doc_complete = random.random() < doc_complete_p

        initial_team = route_team(appeal_type, payer_id)

        # wrong initial routing is more likely when intake docs are thin
        misroute_p = 0.09 if doc_complete else 0.24
        if appeal_type == "Claims Payment":
            misroute_p += 0.06
        routed_wrong = random.random() < misroute_p

        reassignments = 0
        if routed_wrong:
            reassignments = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
        elif random.random() < 0.12:
            reassignments = 1

        final_team = initial_team
        if reassignments:
            choices = [t[0] for t in TEAMS if t[0] != initial_team]
            final_team = random.choice(choices)

        pending_info = (not doc_complete) and random.random() < 0.72
        pending_days = 0
        if pending_info:
            pending_days = int(np.random.gamma(shape=2.2, scale=3.0)) + 1

        escalation_p = 0.06
        if pending_days > 5:
            escalation_p += 0.28
        if reassignments >= 2:
            escalation_p += 0.12
        if priority == "Urgent":
            escalation_p += 0.08
        escalated = random.random() < min(escalation_p, 0.85)

        rework_p = 0.07
        if not doc_complete:
            rework_p += 0.22
        if routed_wrong:
            rework_p += 0.10
        rework = random.random() < min(rework_p, 0.8)

        # ---- build the date chain ----
        intake_done = business_days_later(received, random.choices([0, 1, 2], weights=[0.5, 0.35, 0.15])[0])
        assign_lag = random.choices([0, 1, 2, 4], weights=[0.35, 0.35, 0.2, 0.10])[0]
        if routed_wrong:
            assign_lag += random.randint(1, 3)
        assigned = business_days_later(intake_done, assign_lag)

        review_lag = random.choices([0, 1, 2, 3], weights=[0.3, 0.35, 0.2, 0.15])[0]
        review_started = business_days_later(assigned, review_lag)

        work_days = max(1, int(np.random.gamma(shape=2.0, scale=2.2)))
        work_days += pending_days
        work_days += 2 * reassignments
        if escalated:
            work_days += random.randint(2, 6)
        if rework:
            work_days += random.randint(1, 5)
        decision = business_days_later(review_started, work_days)

        closure_lag = random.choices([0, 1, 2, 5], weights=[0.45, 0.3, 0.17, 0.08])[0]
        closed = business_days_later(decision, closure_lag)

        # anything past the cutoff is still open
        still_open = closed > END
        if still_open:
            status = random.choice(["In Review", "Pending Information", "Escalated"])
            decision_out = None
            closed_out = None
            outcome = None
        else:
            status = "Closed"
            decision_out = decision
            closed_out = closed
            # overturn odds drop when documentation was incomplete
            if doc_complete:
                outcome = random.choices(
                    ["Overturned", "Partially Overturned", "Upheld"],
                    weights=[0.34, 0.18, 0.48],
                )[0]
            else:
                outcome = random.choices(
                    ["Overturned", "Partially Overturned", "Upheld"],
                    weights=[0.19, 0.15, 0.66],
                )[0]

        reason = pick([(r[0], r[3]) for r in REASONS])
        if not doc_complete and random.random() < 0.5:
            reason = random.choice(["RC-01", "RC-05", "RC-12"])
        if routed_wrong and random.random() < 0.4:
            reason = "RC-04"

        rows.append(
            {
                "Appeal_ID": appeal_id,
                "Received_Date": received,
                "Intake_Completed_Date": intake_done,
                "Assigned_Date": assigned,
                "Review_Started_Date": review_started,
                "Decision_Date": decision_out,
                "Closed_Date": closed_out,
                "Appeal_Type": appeal_type,
                "Priority": priority,
                "Payer_ID": payer_id,
                "Initial_Team_ID": initial_team,
                "Final_Team_ID": final_team,
                "Status": status,
                "Outcome": outcome,
                "SLA_Target_Days": sla_target,
                "Documentation_Complete": "Yes" if doc_complete else "No",
                "Rework_Flag": "Yes" if rework else "No",
                "Escalation_Flag": "Yes" if escalated else "No",
                "Reassignment_Count": reassignments,
                "Pending_Info_Days": pending_days,
                "Reason_Code": reason,
                "Final_Routing_Correct": "No" if routed_wrong else "Yes",
            }
        )

    return pd.DataFrame(rows)


def build_events(appeals):
    """One row per thing that happened to an appeal. This is the table that
    makes stage-level delay analysis possible."""
    events = []
    eid = 0
    roles = {
        "Intake": "Intake Specialist",
        "Validation": "Intake Specialist",
        "Classification": "Intake Supervisor",
        "Routing": "Intake Supervisor",
        "Review": "Reviewer",
        "Information Request": "Reviewer",
        "Escalation": "Clinical Review Lead",
        "Decision": "Reviewer",
        "Closure": "Reporting Analyst",
    }

    for r in appeals.itertuples(index=False):
        seq = 0
        timeline = []

        timeline.append(("Intake", "Appeal Received", r.Received_Date, r.Initial_Team_ID, None))
        timeline.append(("Intake", "Intake Logged", r.Intake_Completed_Date, r.Initial_Team_ID, None))
        timeline.append(
            (
                "Validation",
                "Validation Completed" if r.Documentation_Complete == "Yes" else "Validation Failed",
                r.Intake_Completed_Date,
                r.Initial_Team_ID,
                None if r.Documentation_Complete == "Yes" else "RC-02",
            )
        )
        timeline.append(("Classification", "Type Assigned", r.Intake_Completed_Date, r.Initial_Team_ID, None))
        timeline.append(("Routing", "Routed to Team", r.Assigned_Date, r.Initial_Team_ID, None))

        if r.Final_Routing_Correct == "No":
            timeline.append(("Routing", "Routing Error Identified", r.Assigned_Date, r.Initial_Team_ID, "RC-04"))

        for n in range(int(r.Reassignment_Count)):
            when = business_days_later(r.Assigned_Date, n + 1)
            timeline.append(("Routing", "Case Reassigned", when, r.Final_Team_ID, "RC-04"))

        timeline.append(("Review", "Review Started", r.Review_Started_Date, r.Final_Team_ID, None))

        if r.Pending_Info_Days > 0:
            req = business_days_later(r.Review_Started_Date, 1)
            timeline.append(("Information Request", "Information Requested", req, r.Final_Team_ID, "RC-05"))
            got = business_days_later(req, int(r.Pending_Info_Days))
            timeline.append(("Information Request", "Information Received", got, r.Final_Team_ID, "RC-05"))

        if r.Rework_Flag == "Yes":
            rw = business_days_later(r.Review_Started_Date, 2)
            timeline.append(("Review", "Rework Started", rw, r.Final_Team_ID, "RC-01"))

        if r.Escalation_Flag == "Yes":
            esc = business_days_later(r.Review_Started_Date, max(1, int(r.Pending_Info_Days)))
            timeline.append(("Escalation", "Escalated", esc, "TM-06", "RC-14"))

        if r.Decision_Date is not None:
            timeline.append(("Decision", f"Decision: {r.Outcome}", r.Decision_Date, r.Final_Team_ID, None))
        if r.Closed_Date is not None:
            timeline.append(("Closure", "Case Closed", r.Closed_Date, r.Final_Team_ID, None))

        timeline = [t for t in timeline if t[2] is not None and t[2] <= END]
        timeline.sort(key=lambda t: t[2])

        for stage, etype, when, team, delay in timeline:
            eid += 1
            seq += 1
            hour = random.randint(8, 17)
            minute = random.choice([0, 7, 15, 22, 30, 38, 45, 52])
            events.append(
                {
                    "Event_ID": f"EVT-{eid:07d}",
                    "Appeal_ID": r.Appeal_ID,
                    "Event_Timestamp": f"{when} {hour:02d}:{minute:02d}:00",
                    "Process_Stage": stage,
                    "Event_Type": etype,
                    "Team_ID": team,
                    "User_Role": roles.get(stage, "Analyst"),
                    "Delay_Reason": delay,
                    "Event_Sequence": seq,
                }
            )

    return pd.DataFrame(events)


def inject_dirt(appeals):
    """Real extracts are never clean. Break a small slice on purpose so the
    cleaning script and the data-quality page have something to catch."""
    df = appeals.copy()

    dupes = df.sample(18, random_state=7)
    df = pd.concat([df, dupes], ignore_index=True)

    idx = df.sample(25, random_state=11).index
    df.loc[idx, "Documentation_Complete"] = df.loc[idx, "Documentation_Complete"].map(
        {"Yes": "Y", "No": "N"}
    )

    idx = df.sample(15, random_state=13).index
    df.loc[idx, "Status"] = "closed"

    # closed with no outcome recorded
    closed = df[df["Status"].str.lower() == "closed"].sample(20, random_state=17).index
    df.loc[closed, "Outcome"] = None

    # a handful of impossible date orders
    bad = df.dropna(subset=["Closed_Date"]).sample(12, random_state=19).index
    df.loc[bad, "Closed_Date"] = df.loc[bad, "Received_Date"] - pd.to_timedelta(2, unit="D")

    idx = df.sample(10, random_state=23).index
    df.loc[idx, "Payer_ID"] = " pay-02 "

    return df.sample(frac=1, random_state=3).reset_index(drop=True)


def main():
    random.seed(SEED)
    np.random.seed(SEED)
    os.makedirs(RAW, exist_ok=True)

    appeals = build_appeals()
    events = build_events(appeals)
    dim_payer, dim_team, dim_reason, dim_date = make_dim_tables()
    raw_appeals = inject_dirt(appeals)

    raw_appeals.to_csv(os.path.join(RAW, "appeals_fact_raw.csv"), index=False)
    events.to_csv(os.path.join(RAW, "appeal_events.csv"), index=False)
    dim_payer.to_csv(os.path.join(RAW, "dim_payer.csv"), index=False)
    dim_team.to_csv(os.path.join(RAW, "dim_team.csv"), index=False)
    dim_reason.to_csv(os.path.join(RAW, "dim_reason_code.csv"), index=False)
    dim_date.to_csv(os.path.join(RAW, "dim_date.csv"), index=False)

    with pd.ExcelWriter(os.path.join(RAW, "04_synthetic_raw_data.xlsx")) as xl:
        raw_appeals.to_excel(xl, sheet_name="appeals_fact", index=False)
        events.head(50000).to_excel(xl, sheet_name="appeal_events", index=False)
        dim_payer.to_excel(xl, sheet_name="dim_payer", index=False)
        dim_team.to_excel(xl, sheet_name="dim_team", index=False)
        dim_reason.to_excel(xl, sheet_name="dim_reason_code", index=False)

    print(f"appeals rows (with injected dupes): {len(raw_appeals)}")
    print(f"event rows: {len(events)}")
    print(f"events per appeal: {len(events) / appeals.shape[0]:.1f}")


if __name__ == "__main__":
    main()
