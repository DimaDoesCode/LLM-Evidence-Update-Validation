"""
LLM Evidence Update Validation
Create V1 Clear Reversal Dataset

Creates:
    data/clear_reversal_v1.csv

Dataset:
    10 cases
    4 evidence stages per case
    40 observations

Expected trajectories:
    CASE_001: DATABASE       -> DATABASE       -> NETWORK        -> NETWORK
    CASE_002: NETWORK        -> NETWORK        -> APPLICATION    -> APPLICATION
    CASE_003: APPLICATION    -> APPLICATION    -> CONFIGURATION  -> CONFIGURATION
    CASE_004: CONFIGURATION  -> CONFIGURATION  -> DATABASE       -> DATABASE
    CASE_005: DATABASE       -> DATABASE       -> APPLICATION    -> APPLICATION
    CASE_006: NETWORK        -> NETWORK        -> CONFIGURATION  -> CONFIGURATION
    CASE_007: APPLICATION    -> APPLICATION    -> NETWORK        -> NETWORK
    CASE_008: CONFIGURATION  -> CONFIGURATION  -> APPLICATION    -> APPLICATION
    CASE_009: DATABASE       -> DATABASE       -> CONFIGURATION  -> CONFIGURATION
    CASE_010: NETWORK        -> NETWORK        -> DATABASE       -> DATABASE
"""

from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_PATH = Path("data/clear_reversal_v1.csv")


# ============================================================
# DATASET
# ============================================================

DATA = [
    # --------------------------------------------------------
    # CASE_001 — DATABASE -> NETWORK
    # --------------------------------------------------------

    {
        "case_id": "CASE_001",
        "stage": "E0",
        "evidence": (
            "API requests intermittently time out. "
            "DB CPU is approximately 90%, and DB query latency "
            "has increased from 20–30 ms to 300–400 ms. "
            "Application CPU and memory are normal. "
            "No recent application deployment or configuration "
            "change has been recorded."
        ),
        "expected_decision": "DATABASE",
        "update_type": "INITIAL",
    },
    {
        "case_id": "CASE_001",
        "stage": "E1",
        "evidence": (
            "DB latency increases at exactly the same times as "
            "API timeouts. The same DB, queried directly from "
            "a maintenance host, is also slow during the incident. "
            "No packet loss or abnormal network latency is observed."
        ),
        "expected_decision": "DATABASE",
        "update_type": "NO_CHANGE",
    },
    {
        "case_id": "CASE_001",
        "stage": "E2",
        "evidence": (
            "Packet capture shows sustained approximately 35% "
            "packet loss between the application servers and "
            "the DB subnet. The maintenance host reaches the DB "
            "through a different network path and remains stable."
        ),
        "expected_decision": "NETWORK",
        "update_type": "REQUIRED_REVERSAL",
    },
    {
        "case_id": "CASE_001",
        "stage": "E3",
        "evidence": (
            "Network monitoring confirms that packet loss coincides "
            "with every application timeout. DB health checks from "
            "the maintenance host remain normal."
        ),
        "expected_decision": "NETWORK",
        "update_type": "NO_CHANGE",
    },

    # --------------------------------------------------------
    # CASE_002 — NETWORK -> APPLICATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_002",
        "stage": "E0",
        "evidence": (
            "Requests to the service show intermittent latency "
            "and HTTP 500 responses. Network latency between the "
            "client and service is elevated. No recent configuration "
            "change is recorded."
        ),
        "expected_decision": "NETWORK",
        "update_type": "INITIAL",
    },
    {
        "case_id": "CASE_002",
        "stage": "E1",
        "evidence": (
            "Network latency remains elevated during failed requests, "
            "while successful requests use the same route. "
            "Packet loss is not observed."
        ),
        "expected_decision": "NETWORK",
        "update_type": "NO_CHANGE",
    },
    {
        "case_id": "CASE_002",
        "stage": "E2",
        "evidence": (
            "Application logs show a deterministic NullPointerException "
            "in the request handler for exactly the failing request "
            "pattern. Network probes remain healthy."
        ),
        "expected_decision": "APPLICATION",
        "update_type": "REQUIRED_REVERSAL",
    },
    {
        "case_id": "CASE_002",
        "stage": "E3",
        "evidence": (
            "The same request fails locally on the application host "
            "with the same stack trace, without traversing the "
            "production network path."
        ),
        "expected_decision": "APPLICATION",
        "update_type": "NO_CHANGE",
    },

    # --------------------------------------------------------
    # CASE_003 — APPLICATION -> CONFIGURATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_003",
        "stage": "E0",
        "evidence": (
            "A newly deployed application version starts returning "
            "errors immediately after deployment. Application logs "
            "contain repeated initialization failures. No database "
            "or network anomaly is observed."
        ),
        "expected_decision": "APPLICATION",
        "update_type": "INITIAL",
    },
    {
        "case_id": "CASE_003",
        "stage": "E1",
        "evidence": (
            "The same application binary starts successfully in "
            "a separate environment using the same database and "
            "network services."
        ),
        "expected_decision": "APPLICATION",
        "update_type": "NO_CHANGE",
    },
    {
        "case_id": "CASE_003",
        "stage": "E2",
        "evidence": (
            "The failing environment uses a different runtime "
            "configuration. One feature flag required during "
            "initialization is set to an unsupported value."
        ),
        "expected_decision": "CONFIGURATION",
        "update_type": "REQUIRED_REVERSAL",
    },
    {
        "case_id": "CASE_003",
        "stage": "E3",
        "evidence": (
            "Changing the feature flag to the supported value "
            "restores normal application startup without changing "
            "the application binary."
        ),
        "expected_decision": "CONFIGURATION",
        "update_type": "NO_CHANGE",
    },

    # --------------------------------------------------------
    # CASE_004 — CONFIGURATION -> DATABASE
    # --------------------------------------------------------

    {
        "case_id": "CASE_004",
        "stage": "E0",
        "evidence": (
            "A database-backed service becomes significantly slower "
            "shortly after a configuration change. The changed "
            "connection-pool settings are the main recent difference."
        ),
        "expected_decision": "CONFIGURATION",
        "update_type": "INITIAL",
    },
    {
        "case_id": "CASE_004",
        "stage": "E1",
        "evidence": (
            "Rolling back the connection-pool setting on one instance "
            "reduces its latency, while other instances remain slow."
        ),
        "expected_decision": "CONFIGURATION",
        "update_type": "NO_CHANGE",
    },
    {
        "case_id": "CASE_004",
        "stage": "E2",
        "evidence": (
            "An unrelated service using the same database also "
            "experiences the same slowdown. DB-side storage latency "
            "is elevated, while network and application metrics "
            "are normal."
        ),
        "expected_decision": "DATABASE",
        "update_type": "REQUIRED_REVERSAL",
    },
    {
        "case_id": "CASE_004",
        "stage": "E3",
        "evidence": (
            "DB storage I/O returns to normal after a database-side "
            "remediation, without further application configuration "
            "changes. Both services recover."
        ),
        "expected_decision": "DATABASE",
        "update_type": "NO_CHANGE",
    },

    # --------------------------------------------------------
    # CASE_005 — DATABASE -> APPLICATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_005",
        "stage": "E0",
        "evidence": (
            "Transaction processing becomes slow. DB CPU and query "
            "latency are elevated, and transactions frequently "
            "time out. Application CPU remains normal."
        ),
        "expected_decision": "DATABASE",
        "update_type": "INITIAL",
    },
    {
        "case_id": "CASE_005",
        "stage": "E1",
        "evidence": (
            "Slow transactions correlate with high DB latency. "
            "Database health checks show elevated query time "
            "but no infrastructure failure."
        ),
        "expected_decision": "DATABASE",
        "update_type": "NO_CHANGE",
    },
    {
        "case_id": "CASE_005",
        "stage": "E2",
        "evidence": (
            "Application logs reveal malformed SQL generated only "
            "for one transaction type. The same database accepts "
            "valid versions of the query normally."
        ),
        "expected_decision": "APPLICATION",
        "update_type": "REQUIRED_REVERSAL",
    },
    {
        "case_id": "CASE_005",
        "stage": "E3",
        "evidence": (
            "Reproducing the transaction locally generates the same "
            "malformed SQL against a healthy database. Correcting "
            "the application query removes the failure."
        ),
        "expected_decision": "APPLICATION",
        "update_type": "NO_CHANGE",
    },

    # --------------------------------------------------------
    # CASE_006 — NETWORK -> CONFIGURATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_006",
        "stage": "E0",
        "evidence": (
            "One application environment intermittently fails to "
            "connect to a dependency. Connection attempts frequently "
            "time out."
        ),
        "expected_decision": "NETWORK",
        "update_type": "INITIAL",
    },
    {
        "case_id": "CASE_006",
        "stage": "E1",
        "evidence": (
            "Network latency and packet loss are elevated on the "
            "affected path, while other environments remain healthy."
        ),
        "expected_decision": "NETWORK",
        "update_type": "NO_CHANGE",
    },
    {
        "case_id": "CASE_006",
        "stage": "E2",
        "evidence": (
            "Network infrastructure monitoring shows the path is healthy. "
            "The affected environment uses a different firewall rule "
            "and dependency endpoint configuration from healthy "
            "environments."
        ),
        "expected_decision": "CONFIGURATION",
        "update_type": "REQUIRED_REVERSAL",
    },
    {
        "case_id": "CASE_006",
        "stage": "E3",
        "evidence": (
            "Restoring the endpoint and firewall configuration "
            "immediately restores connectivity without network "
            "infrastructure changes."
        ),
        "expected_decision": "CONFIGURATION",
        "update_type": "NO_CHANGE",
    },

    # --------------------------------------------------------
    # CASE_007 — APPLICATION -> NETWORK
    # --------------------------------------------------------

    {
        "case_id": "CASE_007",
        "stage": "E0",
        "evidence": (
            "A background job repeatedly fails while retrieving data "
            "from a remote service. Application logs show request "
            "failures and retries."
        ),
        "expected_decision": "APPLICATION",
        "update_type": "INITIAL",
    },
    {
        "case_id": "CASE_007",
        "stage": "E1",
        "evidence": (
            "Failures occur only for one job implementation, while "
            "another application using the same service succeeds."
        ),
        "expected_decision": "APPLICATION",
        "update_type": "NO_CHANGE",
    },
    {
        "case_id": "CASE_007",
        "stage": "E2",
        "evidence": (
            "Packet capture shows repeated TCP retransmissions and "
            "packet loss on the route used by the failing application. "
            "An alternate network path completes the same requests "
            "successfully."
        ),
        "expected_decision": "NETWORK",
        "update_type": "REQUIRED_REVERSAL",
    },
    {
        "case_id": "CASE_007",
        "stage": "E3",
        "evidence": (
            "Moving the job to the alternate network path removes "
            "the failures without changing application code."
        ),
        "expected_decision": "NETWORK",
        "update_type": "NO_CHANGE",
    },

    # --------------------------------------------------------
    # CASE_008 — CONFIGURATION -> APPLICATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_008",
        "stage": "E0",
        "evidence": (
            "Application crashes immediately after a configuration "
            "or deployment change. No network or database anomaly "
            "is observed."
        ),
        "expected_decision": "CONFIGURATION",
        "update_type": "INITIAL",
    },
    {
        "case_id": "CASE_008",
        "stage": "E1",
        "evidence": (
            "The crash disappears after restoring the previous "
            "configuration on one instance."
        ),
        "expected_decision": "CONFIGURATION",
        "update_type": "NO_CHANGE",
    },
    {
        "case_id": "CASE_008",
        "stage": "E2",
        "evidence": (
            "The same application crashes with the original resource "
            "configuration when a specific request is processed. "
            "The stack trace points to deterministic application logic."
        ),
        "expected_decision": "APPLICATION",
        "update_type": "REQUIRED_REVERSAL",
    },
    {
        "case_id": "CASE_008",
        "stage": "E3",
        "evidence": (
            "Applying the application fix removes the crash while "
            "keeping the original configuration unchanged."
        ),
        "expected_decision": "APPLICATION",
        "update_type": "NO_CHANGE",
    },

    # --------------------------------------------------------
    # CASE_009 — DATABASE -> CONFIGURATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_009",
        "stage": "E0",
        "evidence": (
            "Application experiences database connection failures "
            "and elevated query latency. DB health metrics are "
            "also degraded."
        ),
        "expected_decision": "DATABASE",
        "update_type": "INITIAL",
    },
    {
        "case_id": "CASE_009",
        "stage": "E1",
        "evidence": (
            "Connection failures correlate with periods of elevated "
            "DB latency. Network connectivity to the DB remains available."
        ),
        "expected_decision": "DATABASE",
        "update_type": "NO_CHANGE",
    },
    {
        "case_id": "CASE_009",
        "stage": "E2",
        "evidence": (
            "The database is healthy when accessed by another service. "
            "The affected service has a different connection-pool "
            "configuration, including an excessively low timeout."
        ),
        "expected_decision": "CONFIGURATION",
        "update_type": "REQUIRED_REVERSAL",
    },
    {
        "case_id": "CASE_009",
        "stage": "E3",
        "evidence": (
            "Restoring the connection-pool parameters resolves the "
            "failures while the database remains unchanged."
        ),
        "expected_decision": "CONFIGURATION",
        "update_type": "NO_CHANGE",
    },

    # --------------------------------------------------------
    # CASE_010 — NETWORK -> DATABASE
    # --------------------------------------------------------

    {
        "case_id": "CASE_010",
        "stage": "E0",
        "evidence": (
            "Application intermittently times out while communicating "
            "with the database. Network latency is elevated and some "
            "connection attempts fail."
        ),
        "expected_decision": "NETWORK",
        "update_type": "INITIAL",
    },
    {
        "case_id": "CASE_010",
        "stage": "E1",
        "evidence": (
            "Network probes show intermittent latency spikes coinciding "
            "with application timeouts."
        ),
        "expected_decision": "NETWORK",
        "update_type": "NO_CHANGE",
    },
    {
        "case_id": "CASE_010",
        "stage": "E2",
        "evidence": (
            "Database storage I/O becomes saturated and DB query latency "
            "increases sharply, while network probes remain normal. "
            "Queries from another host show the same database-side slowdown."
        ),
        "expected_decision": "DATABASE",
        "update_type": "REQUIRED_REVERSAL",
    },
    {
        "case_id": "CASE_010",
        "stage": "E3",
        "evidence": (
            "Database storage I/O returns to normal and query latency "
            "recovers without network changes. Application timeouts disappear."
        ),
        "expected_decision": "DATABASE",
        "update_type": "NO_CHANGE",
    },
]


# ============================================================
# VALIDATION
# ============================================================

def validate_dataset(df):
    """Run structural sanity checks."""

    print()
    print("=" * 70)
    print("DATASET VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Shape
    # --------------------------------------------------------

    expected_rows = 40
    expected_cases = 10
    expected_stages = 4

    assert len(df) == expected_rows, (
        f"Expected {expected_rows} rows, "
        f"found {len(df)}"
    )

    assert df["case_id"].nunique() == expected_cases, (
        f"Expected {expected_cases} cases, "
        f"found {df['case_id'].nunique()}"
    )

    print(f"Rows:                  {len(df)}")
    print(f"Cases:                 {df['case_id'].nunique()}")

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    required_columns = {
        "case_id",
        "stage",
        "evidence",
        "expected_decision",
        "update_type",
    }

    assert set(df.columns) == required_columns, (
        f"Unexpected columns: "
        f"{set(df.columns) ^ required_columns}"
    )

    print("Columns:               OK")

    # --------------------------------------------------------
    # Stage structure
    # --------------------------------------------------------

    expected_stage_set = {
        "E0",
        "E1",
        "E2",
        "E3",
    }

    for case_id, group in df.groupby("case_id"):

        stages = set(group["stage"])

        assert stages == expected_stage_set, (
            f"{case_id}: invalid stages {stages}"
        )

        assert len(group) == expected_stages, (
            f"{case_id}: expected 4 stages, "
            f"found {len(group)}"
        )

    print("Stage structure:       OK")

    # --------------------------------------------------------
    # Valid decisions
    # --------------------------------------------------------

    valid_decisions = {
        "DATABASE",
        "NETWORK",
        "APPLICATION",
        "CONFIGURATION",
        "UNCERTAIN",
    }

    invalid_decisions = (
        set(df["expected_decision"])
        - valid_decisions
    )

    assert not invalid_decisions, (
        f"Invalid decisions: {invalid_decisions}"
    )

    print("Decision values:       OK")

    # --------------------------------------------------------
    # Valid update types
    # --------------------------------------------------------

    valid_update_types = {
        "INITIAL",
        "NO_CHANGE",
        "REQUIRED_REVERSAL",
    }

    invalid_update_types = (
        set(df["update_type"])
        - valid_update_types
    )

    assert not invalid_update_types, (
        f"Invalid update types: {invalid_update_types}"
    )

    print("Update types:          OK")

    # --------------------------------------------------------
    # Expected distribution
    # --------------------------------------------------------

    expected_distribution = {
        "INITIAL": 10,
        "NO_CHANGE": 20,
        "REQUIRED_REVERSAL": 10,
    }

    actual_distribution = (
        df["update_type"]
        .value_counts()
        .to_dict()
    )

    assert actual_distribution == expected_distribution, (
        "Unexpected update_type distribution:\n"
        f"Expected: {expected_distribution}\n"
        f"Actual:   {actual_distribution}"
    )

    print()
    print("Update type distribution:")
    for key, value in expected_distribution.items():
        print(f"  {key:<20} {value}")

    # --------------------------------------------------------
    # Check trajectory
    # --------------------------------------------------------

    print()
    print("Expected trajectories:")

    for case_id, group in df.groupby("case_id"):

        ordered = group.sort_values("stage")

        trajectory = " -> ".join(
            ordered["expected_decision"]
        )

        print(
            f"  {case_id}: {trajectory}"
        )

    print()
    print("All validation checks passed.")


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("LLM EVIDENCE UPDATE VALIDATION")
    print("CREATE V1 CLEAR REVERSAL DATASET")
    print("=" * 70)

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    df = pd.DataFrame(DATA)

    # Ensure predictable column order
    df = df[
        [
            "case_id",
            "stage",
            "evidence",
            "expected_decision",
            "update_type",
        ]
    ]

    # Ensure deterministic ordering
    df["stage_order"] = (
        df["stage"]
        .map(
            {
                "E0": 0,
                "E1": 1,
                "E2": 2,
                "E3": 3,
            }
        )
    )

    df = (
        df.sort_values(
            ["case_id", "stage_order"]
        )
        .drop(columns=["stage_order"])
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_dataset(df)

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print("=" * 70)
    print("DATASET CREATED")
    print("=" * 70)

    print(f"Output: {OUTPUT_PATH}")
    print(f"Shape:  {df.shape}")


if __name__ == "__main__":
    main()