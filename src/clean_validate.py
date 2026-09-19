"""
Cleans the raw appeals extract and writes out a data-quality exception log.

Two outputs:
  data/clean/appeals_fact.csv        - analysis-ready
  data/clean/dq_exceptions.csv       - every rule failure, one row each

Run after generate_data.py:  python src/clean_validate.py
"""

import os

import pandas as pd

RAW = os.path.join("data", "raw")
CLEAN = os.path.join("data", "clean")

DATE_COLS = [
    "Received_Date",
    "Intake_Completed_Date",
    "Assigned_Date",
    "Review_Started_Date",
    "Decision_Date",
    "Closed_Date",
]

YES_NO_COLS = ["Documentation_Complete", "Rework_Flag", "Escalation_Flag", "Final_Routing_Correct"]

VALID_STATUS = {"Closed", "In Review", "Pending Information", "Escalated"}

exceptions = []


def log(rule_id, record_id, severity, description):
    exceptions.append(
        {
            "Exception_ID": f"EX-{len(exceptions) + 1:05d}",
            "Rule_ID": rule_id,
            "Record_ID": record_id,
            "Severity": severity,
            "Description": description,
            "Owner": "Reporting Analyst",
            "Status": "Open",
        }
    )


def standardize(df):
    df = df.copy()

    df["Payer_ID"] = df["Payer_ID"].astype(str).str.strip().str.upper()

    df["Status"] = df["Status"].astype(str).str.strip().str.title()
    df["Status"] = df["Status"].replace({"In Review": "In Review", "Pending Information": "Pending Information"})

    for c in YES_NO_COLS:
        df[c] = (
            df[c]
            .astype(str)
            .str.strip()
            .str.upper()
            .replace({"Y": "Yes", "N": "No", "YES": "Yes", "NO": "No", "TRUE": "Yes", "FALSE": "No"})
        )

    for c in DATE_COLS:
        df[c] = pd.to_datetime(df[c], errors="coerce")

    return df


def run_rules(df):
    # DQ-01 duplicate appeal IDs
    dupe_ids = df[df.duplicated("Appeal_ID", keep="first")]["Appeal_ID"].tolist()
    for aid in dupe_ids:
        log("DQ-01", aid, "High", "Duplicate Appeal_ID in extract; kept first occurrence")
    df = df.drop_duplicates("Appeal_ID", keep="first")

    # DQ-02 closed cases must have an outcome
    bad = df[(df["Status"] == "Closed") & (df["Outcome"].isna())]
    for aid in bad["Appeal_ID"]:
        log("DQ-02", aid, "Critical", "Status is Closed but Outcome is blank")

    # DQ-03 closed cases must have a closed date
    bad = df[(df["Status"] == "Closed") & (df["Closed_Date"].isna())]
    for aid in bad["Appeal_ID"]:
        log("DQ-03", aid, "Critical", "Status is Closed but Closed_Date is blank")

    # DQ-04 open cases should not carry a closed date
    bad = df[(df["Status"] != "Closed") & (df["Closed_Date"].notna())]
    for aid in bad["Appeal_ID"]:
        log("DQ-04", aid, "High", "Open status but Closed_Date is populated")

    # DQ-05 date chain must move forward
    chain = ["Received_Date", "Intake_Completed_Date", "Assigned_Date", "Review_Started_Date", "Decision_Date", "Closed_Date"]
    for a, b in zip(chain, chain[1:]):
        bad = df[df[a].notna() & df[b].notna() & (df[b] < df[a])]
        for aid in bad["Appeal_ID"]:
            log("DQ-05", aid, "Critical", f"{b} is earlier than {a}")

    # DQ-06 negative turnaround
    tat = (df["Closed_Date"] - df["Received_Date"]).dt.days
    for aid in df.loc[tat < 0, "Appeal_ID"]:
        log("DQ-06", aid, "Critical", "Negative turnaround time")

    # DQ-07 status must be an approved value
    bad = df[~df["Status"].isin(VALID_STATUS)]
    for aid in bad["Appeal_ID"]:
        log("DQ-07", aid, "Medium", "Status value not in approved list")

    # DQ-08 payer must exist in reference data
    payers = set(pd.read_csv(os.path.join(RAW, "dim_payer.csv"))["Payer_ID"])
    bad = df[~df["Payer_ID"].isin(payers)]
    for aid in bad["Appeal_ID"]:
        log("DQ-08", aid, "High", "Payer_ID not found in dim_payer")

    # DQ-09 team must exist in reference data
    teams = set(pd.read_csv(os.path.join(RAW, "dim_team.csv"))["Team_ID"])
    bad = df[~df["Initial_Team_ID"].isin(teams) | ~df["Final_Team_ID"].isin(teams)]
    for aid in bad["Appeal_ID"]:
        log("DQ-09", aid, "High", "Team_ID not found in dim_team")

    # DQ-10 SLA target must be populated and positive
    bad = df[df["SLA_Target_Days"].isna() | (df["SLA_Target_Days"] <= 0)]
    for aid in bad["Appeal_ID"]:
        log("DQ-10", aid, "Medium", "SLA_Target_Days missing or not positive")

    # DQ-11 yes/no fields must be Yes or No after standardizing
    for c in YES_NO_COLS:
        bad = df[~df[c].isin(["Yes", "No"])]
        for aid in bad["Appeal_ID"]:
            log("DQ-11", aid, "Medium", f"{c} is not a valid Yes/No value")

    # DQ-12 reassignment count sanity
    bad = df[(df["Reassignment_Count"] < 0) | (df["Reassignment_Count"] > 6)]
    for aid in bad["Appeal_ID"]:
        log("DQ-12", aid, "Low", "Reassignment_Count outside expected range 0-6")

    return df


def drop_unusable(df):
    """Records with critical failures come out of the reporting layer. They
    stay in the exception log so nothing disappears silently."""
    critical_ids = {e["Record_ID"] for e in exceptions if e["Severity"] == "Critical"}
    kept = df[~df["Appeal_ID"].isin(critical_ids)].copy()
    return kept, critical_ids


def add_measures(df):
    df = df.copy()
    df["Turnaround_Days"] = (df["Closed_Date"] - df["Received_Date"]).dt.days
    df["Intake_Days"] = (df["Intake_Completed_Date"] - df["Received_Date"]).dt.days
    df["Routing_Days"] = (df["Assigned_Date"] - df["Intake_Completed_Date"]).dt.days
    df["Review_Wait_Days"] = (df["Review_Started_Date"] - df["Assigned_Date"]).dt.days
    df["Review_Days"] = (df["Decision_Date"] - df["Review_Started_Date"]).dt.days
    df["Closure_Days"] = (df["Closed_Date"] - df["Decision_Date"]).dt.days

    df["SLA_Met"] = None
    closed = df["Status"] == "Closed"
    df.loc[closed, "SLA_Met"] = (df.loc[closed, "Turnaround_Days"] <= df.loc[closed, "SLA_Target_Days"]).map(
        {True: "Yes", False: "No"}
    )

    # Friction Score - prototype triage weights, not calibrated against anything real
    score = 0
    score = score + (df["Documentation_Complete"] == "No") * 25
    score = score + (df["Final_Routing_Correct"] == "No") * 20
    score = score + df["Reassignment_Count"].clip(upper=4) * 10
    score = score + (df["Escalation_Flag"] == "Yes") * 15
    score = score + (df["Pending_Info_Days"] > 5) * 20
    score = score + (df["Closure_Days"].fillna(0) > 2) * 10
    df["Friction_Score"] = score.astype(int)

    df["Friction_Category"] = pd.cut(
        df["Friction_Score"],
        bins=[-1, 19, 39, 59, 999],
        labels=["Low friction", "Moderate friction", "High friction", "Critical friction"],
    )
    return df


def main():
    os.makedirs(CLEAN, exist_ok=True)
    raw = pd.read_csv(os.path.join(RAW, "appeals_fact_raw.csv"))
    total_in = len(raw)

    df = standardize(raw)
    df = run_rules(df)
    kept, critical_ids = drop_unusable(df)
    kept = add_measures(kept)

    ex = pd.DataFrame(exceptions)
    ex.to_csv(os.path.join(CLEAN, "dq_exceptions.csv"), index=False)
    kept.to_csv(os.path.join(CLEAN, "appeals_fact.csv"), index=False)

    dq_score = 100 * (1 - ex["Record_ID"].nunique() / total_in)

    print(f"rows in:              {total_in}")
    print(f"rows to reporting:    {len(kept)}")
    print(f"exceptions logged:    {len(ex)}")
    print(f"records blocked:      {len(critical_ids)}")
    print(f"Data Quality Score:   {dq_score:.2f}%")
    if len(ex):
        print("\nby severity:")
        print(ex["Severity"].value_counts().to_string())


if __name__ == "__main__":
    main()
