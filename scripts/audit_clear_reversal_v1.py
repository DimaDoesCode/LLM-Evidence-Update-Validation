import pandas as pd
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

DATA_PATH = Path("data/clear_reversal_v1.csv")
REPORT_PATH = Path("results/v1_clear_reversal_dataset_audit.csv")

EXPECTED_COLUMNS = [
    "case_id",
    "stage",
    "evidence",
    "expected_decision",
    "update_type",
]

VALID_DECISIONS = {
    "DATABASE",
    "NETWORK",
    "APPLICATION",
    "CONFIGURATION",
    "UNCERTAIN",
}

VALID_UPDATE_TYPES = {
    "INITIAL",
    "NO_CHANGE",
    "REQUIRED_REVERSAL",
}

EXPECTED_STAGES = ["E0", "E1", "E2", "E3"]

EXPECTED_CASE_COUNT = 40
EXPECTED_ROW_COUNT = 160

EXPECTED_REVERSAL_DISTRIBUTION = {
    "E1": 10,
    "E2": 20,
    "E3": 10,
}


# ============================================================
# HELPERS
# ============================================================

audit_rows = []


def add_check(check, status, details):
    audit_rows.append(
        {
            "check": check,
            "status": status,
            "details": details,
        }
    )


def fail(check, details):
    add_check(check, "FAIL", details)


def passed(check, details):
    add_check(check, "PASS", details)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("LLM EVIDENCE UPDATE VALIDATION — V1 DATASET INTEGRITY AUDIT")
print("=" * 70)

print("\n[1] LOADING DATA")

if not DATA_PATH.exists():
    print(f"ERROR: Dataset not found: {DATA_PATH}")
    raise SystemExit(1)

df = pd.read_csv(DATA_PATH)

print(f"Dataset shape: {df.shape}")


# ============================================================
# BASIC STRUCTURE
# ============================================================

print("\n[2] BASIC STRUCTURE")

if list(df.columns) == EXPECTED_COLUMNS:
    passed(
        "Required columns",
        "Columns match expected schema",
    )
    print("Required columns: OK")
else:
    fail(
        "Required columns",
        f"Expected {EXPECTED_COLUMNS}, got {list(df.columns)}",
    )
    print("Required columns: FAIL")


if len(df) == EXPECTED_ROW_COUNT:
    passed(
        "Row count",
        f"{EXPECTED_ROW_COUNT} rows",
    )
    print(f"Rows: {len(df)} — OK")
else:
    fail(
        "Row count",
        f"Expected {EXPECTED_ROW_COUNT}, got {len(df)}",
    )
    print(f"Rows: {len(df)} — FAIL")


case_count = df["case_id"].nunique()

if case_count == EXPECTED_CASE_COUNT:
    passed(
        "Case count",
        f"{EXPECTED_CASE_COUNT} unique cases",
    )
    print(f"Cases: {case_count} — OK")
else:
    fail(
        "Case count",
        f"Expected {EXPECTED_CASE_COUNT}, got {case_count}",
    )
    print(f"Cases: {case_count} — FAIL")


# ============================================================
# VALUE VALIDATION
# ============================================================

print("\n[3] VALUE VALIDATION")

invalid_decisions = sorted(
    set(df["expected_decision"].dropna()) - VALID_DECISIONS
)

if not invalid_decisions:
    passed(
        "Decision values",
        "All expected_decision values are valid",
    )
    print("Decision values: OK")
else:
    fail(
        "Decision values",
        f"Invalid values: {invalid_decisions}",
    )
    print(f"Decision values: FAIL — {invalid_decisions}")


invalid_update_types = sorted(
    set(df["update_type"].dropna()) - VALID_UPDATE_TYPES
)

if not invalid_update_types:
    passed(
        "Update types",
        "All update_type values are valid",
    )
    print("Update types: OK")
else:
    fail(
        "Update types",
        f"Invalid values: {invalid_update_types}",
    )
    print(f"Update types: FAIL — {invalid_update_types}")


# ============================================================
# CASE-LEVEL AUDIT
# ============================================================

print("\n[4] CASE-LEVEL INTEGRITY")

case_failures = []

for case_id, group in df.groupby("case_id", sort=True):

    group = group.sort_values("stage")

    # --------------------------------------------------------
    # Stage structure
    # --------------------------------------------------------

    stages = group["stage"].tolist()

    if stages != EXPECTED_STAGES:
        case_failures.append(
            (
                case_id,
                "Invalid stage structure",
                f"Expected {EXPECTED_STAGES}, got {stages}",
            )
        )
        continue

    # --------------------------------------------------------
    # Exactly one INITIAL
    # --------------------------------------------------------

    initial_count = (group["update_type"] == "INITIAL").sum()

    if initial_count != 1:
        case_failures.append(
            (
                case_id,
                "INITIAL count",
                f"Expected 1, got {initial_count}",
            )
        )

    # --------------------------------------------------------
    # Exactly one REQUIRED_REVERSAL
    # --------------------------------------------------------

    reversal_rows = group[
        group["update_type"] == "REQUIRED_REVERSAL"
    ]

    reversal_count = len(reversal_rows)

    if reversal_count != 1:
        case_failures.append(
            (
                case_id,
                "REQUIRED_REVERSAL count",
                f"Expected 1, got {reversal_count}",
            )
        )

    # --------------------------------------------------------
    # Evidence completeness
    # --------------------------------------------------------

    empty_evidence = group["evidence"].isna() | (
        group["evidence"].astype(str).str.strip() == ""
    )

    if empty_evidence.any():
        bad_stages = group.loc[empty_evidence, "stage"].tolist()

        case_failures.append(
            (
                case_id,
                "Evidence completeness",
                f"Empty evidence at {bad_stages}",
            )
        )

    # --------------------------------------------------------
    # Duplicate evidence inside case
    # --------------------------------------------------------

    evidence_count = group["evidence"].nunique()

    if evidence_count != len(group):
        case_failures.append(
            (
                case_id,
                "Duplicate evidence",
                "Evidence rows are not unique within case",
            )
        )

    # --------------------------------------------------------
    # Expected trajectory
    # --------------------------------------------------------

    decisions = group["expected_decision"].tolist()

    changes = []

    for i in range(1, len(decisions)):
        if decisions[i] != decisions[i - 1]:
            changes.append(i)

    if len(changes) != 1:
        case_failures.append(
            (
                case_id,
                "Trajectory changes",
                f"Expected exactly 1 decision change, got {len(changes)}",
            )
        )
        continue

    reversal_index = changes[0]
    reversal_stage = EXPECTED_STAGES[reversal_index]

    # --------------------------------------------------------
    # INITIAL position
    # --------------------------------------------------------

    initial_stage = group.iloc[0]["update_type"]

    if initial_stage != "INITIAL":
        case_failures.append(
            (
                case_id,
                "INITIAL position",
                "INITIAL must occur at E0",
            )
        )

    # --------------------------------------------------------
    # Update type consistency
    # --------------------------------------------------------

    for i, row in group.reset_index(drop=True).iterrows():

        expected_update_type = (
            "INITIAL"
            if i == 0
            else "REQUIRED_REVERSAL"
            if i == reversal_index
            else "NO_CHANGE"
        )

        actual_update_type = row["update_type"]

        if actual_update_type != expected_update_type:
            case_failures.append(
                (
                    case_id,
                    "Update type consistency",
                    (
                        f"{row['stage']}: expected "
                        f"{expected_update_type}, got "
                        f"{actual_update_type}"
                    ),
                )
            )

    # --------------------------------------------------------
    # Reversal stage must be E1/E2/E3
    # --------------------------------------------------------

    if reversal_stage not in {"E1", "E2", "E3"}:
        case_failures.append(
            (
                case_id,
                "Reversal stage",
                f"Invalid reversal stage: {reversal_stage}",
            )
        )

    # --------------------------------------------------------
    # Initial != final
    # --------------------------------------------------------

    initial_decision = decisions[0]
    final_decision = decisions[-1]

    if initial_decision == final_decision:
        case_failures.append(
            (
                case_id,
                "Initial/final decision",
                f"Initial and final are both {initial_decision}",
            )
        )


if not case_failures:
    passed(
        "Case-level integrity",
        "All 40 cases passed structural validation",
    )
    print("Case-level integrity: OK")
else:
    fail(
        "Case-level integrity",
        f"{len(case_failures)} case-level issues detected",
    )

    print(
        f"Case-level integrity: FAIL "
        f"({len(case_failures)} issues)"
    )

    for case_id, check, details in case_failures:
        print(f"  {case_id} | {check} | {details}")


# ============================================================
# REVERSAL DISTRIBUTION
# ============================================================

print("\n[5] REVERSAL DISTRIBUTION")

reversal_distribution = (
    df[df["update_type"] == "REQUIRED_REVERSAL"]
    .groupby("stage")
    .size()
    .to_dict()
)

distribution_ok = True

for stage, expected_count in EXPECTED_REVERSAL_DISTRIBUTION.items():

    actual_count = reversal_distribution.get(stage, 0)

    if actual_count != expected_count:
        distribution_ok = False

        fail(
            f"Reversal distribution {stage}",
            f"Expected {expected_count}, got {actual_count}",
        )

        print(
            f"{stage}: {actual_count} "
            f"(expected {expected_count}) — FAIL"
        )
    else:
        passed(
            f"Reversal distribution {stage}",
            f"{actual_count} cases",
        )

        print(
            f"{stage}: {actual_count} "
            f"(expected {expected_count}) — OK"
        )


# ============================================================
# REVERSAL DIRECTIONS
# ============================================================

print("\n[6] REVERSAL DIRECTION DIVERSITY")

direction_rows = []

for case_id, group in df.groupby("case_id", sort=True):

    group = group.sort_values("stage")

    decisions = group["expected_decision"].tolist()

    initial_decision = decisions[0]
    final_decision = decisions[-1]

    direction_rows.append(
        {
            "case_id": case_id,
            "initial_decision": initial_decision,
            "final_decision": final_decision,
            "direction": (
                f"{initial_decision} -> {final_decision}"
            ),
        }
    )

directions = pd.DataFrame(direction_rows)

direction_counts = (
    directions["direction"]
    .value_counts()
    .sort_index()
)

for direction, count in direction_counts.items():
    print(f"{direction}: {count}")

if len(direction_counts) >= 4:
    passed(
        "Direction diversity",
        f"{len(direction_counts)} unique reversal directions",
    )
else:
    fail(
        "Direction diversity",
        f"Only {len(direction_counts)} unique reversal directions",
    )


# ============================================================
# GLOBAL DUPLICATES
# ============================================================

print("\n[7] GLOBAL DUPLICATE CHECKS")

duplicate_rows = df.duplicated(
    subset=[
        "case_id",
        "stage",
        "evidence",
        "expected_decision",
        "update_type",
    ]
).sum()

if duplicate_rows == 0:
    passed(
        "Duplicate rows",
        "No exact duplicate observations",
    )
    print("Exact duplicate rows: NONE")
else:
    fail(
        "Duplicate rows",
        f"{duplicate_rows} duplicate observations",
    )
    print(f"Exact duplicate rows: {duplicate_rows}")


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)
print("FINAL AUDIT RESULT")
print("=" * 70)

audit_df = pd.DataFrame(audit_rows)

fail_count = (audit_df["status"] == "FAIL").sum()
pass_count = (audit_df["status"] == "PASS").sum()

print(f"PASS: {pass_count}")
print(f"FAIL: {fail_count}")

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
audit_df.to_csv(REPORT_PATH, index=False)

print(f"\nAudit report saved to:")
print(REPORT_PATH)

if fail_count == 0:
    print("\nDATASET INTEGRITY AUDIT: PASSED")
else:
    print("\nDATASET INTEGRITY AUDIT: FAILED")

print("=" * 70)

if fail_count > 0:
    raise SystemExit(1)