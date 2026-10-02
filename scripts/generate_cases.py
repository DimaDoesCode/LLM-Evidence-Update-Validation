"""
LLM Evidence Update Validation
Create V1 Clear Reversal Dataset

Creates:
    data/clear_reversal_v1.csv

Dataset:
    40 cases
    4 evidence stages per case
    160 observations

Design:
    - CASE_001 ... CASE_010 are the original pilot cases.
    - CASE_011 ... CASE_040 extend the dataset.
    - Every case contains exactly one required reversal.
    - Reversal stages:
        E1: 10 cases
        E2: 20 cases
        E3: 10 cases

The dataset is intentionally deterministic.
No random generation is used.
"""

from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_PATH = Path(
    "data/clear_reversal_v1.csv"
)


# ============================================================
# ORIGINAL PILOT CASES
# DO NOT MODIFY
# ============================================================

PILOT_CASES = [
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
# ADDITIONAL CASES
# ============================================================

ADDITIONAL_CASES = [

    # ========================================================
    # E1 REVERSALS — CASE_011 ... CASE_020
    # ========================================================

    # --------------------------------------------------------
    # CASE_011 — DATABASE -> APPLICATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_011",
        "trajectory": [
            "DATABASE", "APPLICATION"
        ],
        "reversal_stage": "E1",
        "evidence": [
            (
                "Order processing is slow. Database CPU is high "
                "and query latency is elevated. Application resources "
                "are normal."
            ),
            (
                "A single request type generates an invalid query "
                "before reaching the normal database workload. "
                "The same database handles valid queries normally."
            ),
            (
                "The malformed query can be reproduced locally "
                "against a healthy database."
            ),
            (
                "Correcting the request-building logic removes "
                "the invalid queries and restores processing."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_012 — NETWORK -> CONFIGURATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_012",
        "trajectory": [
            "NETWORK", "CONFIGURATION"
        ],
        "reversal_stage": "E1",
        "evidence": [
            (
                "Connections to an external service frequently time out. "
                "Network latency is elevated on the affected host."
            ),
            (
                "The network path is healthy from another host. "
                "The affected host has a different proxy endpoint "
                "and routing configuration."
            ),
            (
                "Applying the known-good endpoint configuration "
                "restores connectivity."
            ),
            (
                "Network monitoring remains normal after the change."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_013 — APPLICATION -> DATABASE
    # --------------------------------------------------------

    {
        "case_id": "CASE_013",
        "trajectory": [
            "APPLICATION", "DATABASE"
        ],
        "reversal_stage": "E1",
        "evidence": [
            (
                "A reporting application becomes slow after a release. "
                "The application logs show longer request durations."
            ),
            (
                "The same queries from two independent clients are "
                "slow against the same database, while the application "
                "code and host metrics remain normal."
            ),
            (
                "Database storage latency is elevated during the incident."
            ),
            (
                "Database storage remediation restores query performance."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_014 — CONFIGURATION -> NETWORK
    # --------------------------------------------------------

    {
        "case_id": "CASE_014",
        "trajectory": [
            "CONFIGURATION", "NETWORK"
        ],
        "reversal_stage": "E1",
        "evidence": [
            (
                "One service cannot reliably reach a remote endpoint "
                "after a deployment. A recently changed endpoint setting "
                "is an obvious suspect."
            ),
            (
                "Packet captures show loss and retransmissions on the "
                "network path used by the service, while the endpoint "
                "configuration is identical to a healthy instance."
            ),
            (
                "The same packet loss appears when the healthy instance "
                "uses the affected network path."
            ),
            (
                "Changing the network route removes the failures."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_015 — NETWORK -> APPLICATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_015",
        "trajectory": [
            "NETWORK", "APPLICATION"
        ],
        "reversal_stage": "E1",
        "evidence": [
            (
                "Users report intermittent failures and increased "
                "latency. Network latency is elevated during incidents."
            ),
            (
                "The failing requests contain a specific payload pattern. "
                "The same payload fails locally without network access, "
                "while ordinary requests succeed over the same route."
            ),
            (
                "Application tracing identifies a deterministic exception "
                "for that payload."
            ),
            (
                "A code change removes the exception."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_016 — DATABASE -> CONFIGURATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_016",
        "trajectory": [
            "DATABASE", "CONFIGURATION"
        ],
        "reversal_stage": "E1",
        "evidence": [
            (
                "Database-backed requests are timing out. Database "
                "latency is elevated and initially appears to be the "
                "main source of the problem."
            ),
            (
                "The same database is healthy for other clients. "
                "Only this service uses an unusually short connection "
                "timeout and aggressive pool limits."
            ),
            (
                "Increasing the timeout removes the failures without "
                "changing the database."
            ),
            (
                "Database metrics remain unchanged after recovery."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_017 — APPLICATION -> NETWORK
    # --------------------------------------------------------

    {
        "case_id": "CASE_017",
        "trajectory": [
            "APPLICATION", "NETWORK"
        ],
        "reversal_stage": "E1",
        "evidence": [
            (
                "A worker repeatedly fails while downloading objects. "
                "The worker logs contain request errors."
            ),
            (
                "The same worker succeeds when connected through a "
                "different network path. Packet loss is observed only "
                "on the original route."
            ),
            (
                "Other workers using the alternate route remain healthy."
            ),
            (
                "Replacing the route removes the download failures."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_018 — CONFIGURATION -> DATABASE
    # --------------------------------------------------------

    {
        "case_id": "CASE_018",
        "trajectory": [
            "CONFIGURATION", "DATABASE"
        ],
        "reversal_stage": "E1",
        "evidence": [
            (
                "A service becomes slow after a configuration deployment. "
                "Connection-pool parameters are the most visible change."
            ),
            (
                "Multiple independent applications using the same database "
                "show the same increase in query latency. Database storage "
                "latency is elevated."
            ),
            (
                "Rolling back the service configuration does not remove "
                "the slowdown."
            ),
            (
                "Database remediation restores all affected services."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_019 — DATABASE -> NETWORK
    # --------------------------------------------------------

    {
        "case_id": "CASE_019",
        "trajectory": [
            "DATABASE", "NETWORK"
        ],
        "reversal_stage": "E1",
        "evidence": [
            (
                "Database requests time out and database latency is high. "
                "The database initially appears overloaded."
            ),
            (
                "The database is responsive from another network segment. "
                "Packet capture from the affected application shows "
                "retransmissions and intermittent packet loss."
            ),
            (
                "Database CPU and storage metrics remain normal when "
                "observed independently."
            ),
            (
                "Restoring the network path eliminates the timeouts."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_020 — NETWORK -> DATABASE
    # --------------------------------------------------------

    {
        "case_id": "CASE_020",
        "trajectory": [
            "NETWORK", "DATABASE"
        ],
        "reversal_stage": "E1",
        "evidence": [
            (
                "Requests to the database are slow and network latency "
                "is elevated, suggesting a possible network problem."
            ),
            (
                "The same database queries are slow from a local host "
                "with no network path to the affected segment. Database "
                "storage latency is elevated."
            ),
            (
                "Network probes return to normal while database queries "
                "remain slow."
            ),
            (
                "Database storage recovery restores application performance."
            ),
        ],
    },


    # ========================================================
    # E2 REVERSALS — CASE_021 ... CASE_030
    # ========================================================

    # --------------------------------------------------------
    # CASE_021 — APPLICATION -> CONFIGURATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_021",
        "trajectory": [
            "APPLICATION", "CONFIGURATION"
        ],
        "reversal_stage": "E2",
        "evidence": [
            (
                "A new application release fails during startup. "
                "Initialization errors are visible in the application log."
            ),
            (
                "The application binary starts successfully in another "
                "environment."
            ),
            (
                "The failing environment has an unsupported runtime "
                "setting that is consumed during initialization."
            ),
            (
                "Changing that setting restores startup without changing "
                "the application binary."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_022 — DATABASE -> NETWORK
    # --------------------------------------------------------

    {
        "case_id": "CASE_022",
        "trajectory": [
            "DATABASE", "NETWORK"
        ],
        "reversal_stage": "E2",
        "evidence": [
            (
                "Database queries are slow and database CPU is elevated."
            ),
            (
                "Query latency remains correlated with application "
                "timeouts. Database health checks are inconclusive."
            ),
            (
                "Packet capture reveals sustained loss between the "
                "application subnet and database subnet. Direct database "
                "access from another segment remains healthy."
            ),
            (
                "Network remediation removes the timeouts while database "
                "load returns to normal."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_023 — NETWORK -> APPLICATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_023",
        "trajectory": [
            "NETWORK", "APPLICATION"
        ],
        "reversal_stage": "E2",
        "evidence": [
            (
                "A service produces intermittent failures. Network "
                "latency is elevated during some failures."
            ),
            (
                "Packet loss is not consistently observed, and successful "
                "requests use the same network path."
            ),
            (
                "A deterministic exception appears in the request handler "
                "for exactly the failing input. The same failure is "
                "reproduced locally."
            ),
            (
                "Fixing the handler removes the failures without network "
                "changes."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_024 — CONFIGURATION -> DATABASE
    # --------------------------------------------------------

    {
        "case_id": "CASE_024",
        "trajectory": [
            "CONFIGURATION", "DATABASE"
        ],
        "reversal_stage": "E2",
        "evidence": [
            (
                "Database-backed processing slows after a configuration "
                "change. Connection settings are the most visible difference."
            ),
            (
                "Rolling back the setting on one instance improves that "
                "instance but does not explain failures on other clients."
            ),
            (
                "Independent services using the same database show the "
                "same storage latency increase."
            ),
            (
                "Database remediation restores all services without "
                "further configuration changes."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_025 — APPLICATION -> DATABASE
    # --------------------------------------------------------

    {
        "case_id": "CASE_025",
        "trajectory": [
            "APPLICATION", "DATABASE"
        ],
        "reversal_stage": "E2",
        "evidence": [
            (
                "A transaction service reports errors and slow requests "
                "after a deployment."
            ),
            (
                "Application CPU and memory are normal. Some requests "
                "complete successfully against the same database."
            ),
            (
                "The same slow query pattern is reproduced from an "
                "independent client. Database storage latency is elevated."
            ),
            (
                "Database remediation removes the slowdown without "
                "application changes."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_026 — NETWORK -> CONFIGURATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_026",
        "trajectory": [
            "NETWORK", "CONFIGURATION"
        ],
        "reversal_stage": "E2",
        "evidence": [
            (
                "A service intermittently fails to connect to a dependency. "
                "Network latency is elevated on the affected path."
            ),
            (
                "Other services on the same network segment remain healthy."
            ),
            (
                "Infrastructure monitoring shows the path is healthy. "
                "The failing service uses a different endpoint and firewall "
                "configuration from healthy services."
            ),
            (
                "Restoring the known-good configuration immediately "
                "restores connectivity."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_027 — DATABASE -> APPLICATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_027",
        "trajectory": [
            "DATABASE", "APPLICATION"
        ],
        "reversal_stage": "E2",
        "evidence": [
            (
                "An application experiences slow transactions. Database "
                "query latency is elevated."
            ),
            (
                "Database health checks confirm elevated query latency, "
                "but no storage or infrastructure failure is observed."
            ),
            (
                "Tracing shows that one application code path generates "
                "an inefficient query only for a particular transaction."
            ),
            (
                "Replacing the query removes the performance problem "
                "against the same database."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_028 — CONFIGURATION -> NETWORK
    # --------------------------------------------------------

    {
        "case_id": "CASE_028",
        "trajectory": [
            "CONFIGURATION", "NETWORK"
        ],
        "reversal_stage": "E2",
        "evidence": [
            (
                "A service loses connectivity after a deployment. "
                "A changed endpoint configuration is initially suspected."
            ),
            (
                "The endpoint value matches the value used by healthy "
                "instances."
            ),
            (
                "Packet capture shows loss and retransmissions on the "
                "network route used by the affected service."
            ),
            (
                "Moving the service to a healthy route restores connectivity."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_029 — APPLICATION -> NETWORK
    # --------------------------------------------------------

    {
        "case_id": "CASE_029",
        "trajectory": [
            "APPLICATION", "NETWORK"
        ],
        "reversal_stage": "E2",
        "evidence": [
            (
                "A background worker fails to retrieve remote data. "
                "Application logs show repeated request failures."
            ),
            (
                "The same worker succeeds for local test requests, "
                "but remote requests continue to fail."
            ),
            (
                "Packet capture identifies retransmissions and packet "
                "loss only on the production route."
            ),
            (
                "An alternate route removes the failures without code changes."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_030 — NETWORK -> DATABASE
    # --------------------------------------------------------

    {
        "case_id": "CASE_030",
        "trajectory": [
            "NETWORK", "DATABASE"
        ],
        "reversal_stage": "E2",
        "evidence": [
            (
                "Application requests to the database time out. "
                "Network latency is elevated."
            ),
            (
                "Some network probes are abnormal, but successful "
                "database requests continue through the same path."
            ),
            (
                "Database storage I/O becomes saturated and queries "
                "from another host show the same slowdown."
            ),
            (
                "Database storage remediation restores query performance."
            ),
        ],
    },


    # ========================================================
    # E3 REVERSALS — CASE_031 ... CASE_040
    # ========================================================

    # --------------------------------------------------------
    # CASE_031 — DATABASE -> APPLICATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_031",
        "trajectory": [
            "DATABASE", "APPLICATION"
        ],
        "reversal_stage": "E3",
        "evidence": [
            (
                "Transactions are slow and database query latency is high."
            ),
            (
                "Database metrics remain elevated during failed transactions."
            ),
            (
                "Another client using the same database observes similar "
                "latency, so the database remains a plausible cause."
            ),
            (
                "Detailed tracing shows that the affected application "
                "generates an expensive query only for the failing request. "
                "The same query pattern is not present in healthy clients."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_032 — NETWORK -> CONFIGURATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_032",
        "trajectory": [
            "NETWORK", "CONFIGURATION"
        ],
        "reversal_stage": "E3",
        "evidence": [
            (
                "A service intermittently loses connectivity. Network "
                "latency is elevated."
            ),
            (
                "Packet loss is observed during some incidents."
            ),
            (
                "The affected service remains the only client with "
                "the failures while other services use the same network."
            ),
            (
                "The final configuration audit shows an incorrect proxy "
                "endpoint and timeout combination used only by the affected "
                "service. Correcting it restores connectivity."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_033 — APPLICATION -> NETWORK
    # --------------------------------------------------------

    {
        "case_id": "CASE_033",
        "trajectory": [
            "APPLICATION", "NETWORK"
        ],
        "reversal_stage": "E3",
        "evidence": [
            (
                "A worker fails while calling a remote service. "
                "Application logs contain repeated request errors."
            ),
            (
                "The worker has no deterministic exception and succeeds "
                "for some requests."
            ),
            (
                "The remote service is healthy from other clients, while "
                "the affected worker continues to fail intermittently."
            ),
            (
                "Packet capture finally identifies retransmissions and "
                "loss on the worker's network path. An alternate route "
                "eliminates the failures."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_034 — CONFIGURATION -> DATABASE
    # --------------------------------------------------------

    {
        "case_id": "CASE_034",
        "trajectory": [
            "CONFIGURATION", "DATABASE"
        ],
        "reversal_stage": "E3",
        "evidence": [
            (
                "A database-backed application slows after a configuration "
                "deployment. Connection-pool settings are suspected."
            ),
            (
                "Rolling back one configuration value improves a single "
                "instance but does not eliminate the broader slowdown."
            ),
            (
                "Several independent services continue to show high "
                "database query latency."
            ),
            (
                "Database storage monitoring identifies sustained I/O "
                "saturation affecting all clients. Database remediation "
                "restores performance."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_035 — DATABASE -> NETWORK
    # --------------------------------------------------------

    {
        "case_id": "CASE_035",
        "trajectory": [
            "DATABASE", "NETWORK"
        ],
        "reversal_stage": "E3",
        "evidence": [
            (
                "Database requests time out and database latency is elevated."
            ),
            (
                "Database CPU is high during incidents, making a database "
                "problem plausible."
            ),
            (
                "Direct database access from a separate network segment "
                "remains responsive, but the application path continues "
                "to experience intermittent failures."
            ),
            (
                "Packet capture on the application path shows sustained "
                "loss and retransmissions. The network path is the common "
                "difference between successful and failed access."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_036 — APPLICATION -> CONFIGURATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_036",
        "trajectory": [
            "APPLICATION", "CONFIGURATION"
        ],
        "reversal_stage": "E3",
        "evidence": [
            (
                "A new application version fails during startup. "
                "Initialization errors are present in the application logs."
            ),
            (
                "The same binary starts successfully in a separate environment."
            ),
            (
                "Database and network services are healthy in both environments, "
                "but the exact runtime settings have not yet been compared."
            ),
            (
                "The failing environment contains an unsupported feature flag "
                "value. Changing only that value restores startup."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_037 — NETWORK -> APPLICATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_037",
        "trajectory": [
            "NETWORK", "APPLICATION"
        ],
        "reversal_stage": "E3",
        "evidence": [
            (
                "A web service produces intermittent HTTP errors and "
                "elevated network latency."
            ),
            (
                "Packet loss is not consistently observed, and some requests "
                "succeed through the same network path."
            ),
            (
                "The affected requests share a specific input pattern, "
                "but no deterministic application failure has yet been "
                "established."
            ),
            (
                "Application tracing identifies a deterministic exception "
                "for that input. The same request fails locally without "
                "using the production network."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_038 — CONFIGURATION -> APPLICATION
    # --------------------------------------------------------

    {
        "case_id": "CASE_038",
        "trajectory": [
            "CONFIGURATION", "APPLICATION"
        ],
        "reversal_stage": "E3",
        "evidence": [
            (
                "An application crashes after a deployment. A changed "
                "runtime configuration is initially suspected."
            ),
            (
                "Restoring one configuration value reduces the frequency "
                "but does not eliminate the crash."
            ),
            (
                "The crash occurs only for a particular request and "
                "the same application build is otherwise stable."
            ),
            (
                "A deterministic stack trace identifies an application "
                "logic error. The same failure can be reproduced locally "
                "with the original configuration."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_039 — APPLICATION -> DATABASE
    # --------------------------------------------------------

    {
        "case_id": "CASE_039",
        "trajectory": [
            "APPLICATION", "DATABASE"
        ],
        "reversal_stage": "E3",
        "evidence": [
            (
                "A transaction service reports intermittent failures "
                "and slow responses after a release."
            ),
            (
                "Application resource usage is normal and the failures "
                "are not tied to one specific code path."
            ),
            (
                "Database queries show elevated latency, but the evidence "
                "does not yet distinguish application and database causes."
            ),
            (
                "The same query slowdown is reproduced from an independent "
                "client and database storage I/O is saturated. Application "
                "logs show no independent failure."
            ),
        ],
    },

    # --------------------------------------------------------
    # CASE_040 — NETWORK -> DATABASE
    # --------------------------------------------------------

    {
        "case_id": "CASE_040",
        "trajectory": [
            "NETWORK", "DATABASE"
        ],
        "reversal_stage": "E3",
        "evidence": [
            (
                "Application requests to the database time out and network "
                "latency is elevated."
            ),
            (
                "Some network probes are abnormal during the incident."
            ),
            (
                "The application remains affected while network probes "
                "mostly recover. Database query latency remains high."
            ),
            (
                "Independent database access shows the same slowdown and "
                "database storage I/O is saturated. Network monitoring is "
                "normal at the same time."
            ),
        ],
    },
]


# ============================================================
# BUILD ADDITIONAL CASES
# ============================================================

def build_additional_cases():
    """
    Convert compact case specifications into the same flat
    structure used by the original dataset.
    """

    rows = []

    for spec in ADDITIONAL_CASES:

        case_id = spec["case_id"]
        initial_decision = spec["trajectory"][0]
        final_decision = spec["trajectory"][1]
        reversal_stage = spec["reversal_stage"]
        evidence = spec["evidence"]

        reversal_index = int(
            reversal_stage[1]
        )

        assert len(evidence) == 4, (
            f"{case_id}: expected 4 evidence stages"
        )

        for stage_number in range(4):

            stage = f"E{stage_number}"

            if stage_number < reversal_index:
                expected_decision = initial_decision
                update_type = (
                    "INITIAL"
                    if stage_number == 0
                    else "NO_CHANGE"
                )

            else:
                expected_decision = final_decision
                update_type = (
                    "REQUIRED_REVERSAL"
                    if stage_number == reversal_index
                    else "NO_CHANGE"
                )

            rows.append(
                {
                    "case_id": case_id,
                    "stage": stage,
                    "evidence": evidence[stage_number],
                    "expected_decision": expected_decision,
                    "update_type": update_type,
                }
            )

    return rows


# ============================================================
# VALIDATION
# ============================================================

def validate_dataset(df):

    print()
    print("=" * 70)
    print("DATASET VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Shape
    # --------------------------------------------------------

    expected_rows = 160
    expected_cases = 40

    assert len(df) == expected_rows, (
        f"Expected {expected_rows} rows, "
        f"found {len(df)}"
    )

    assert df["case_id"].nunique() == expected_cases, (
        f"Expected {expected_cases} cases, "
        f"found {df['case_id'].nunique()}"
    )

    print(
        f"Rows:                  {len(df)}"
    )

    print(
        f"Cases:                 "
        f"{df['case_id'].nunique()}"
    )

    # --------------------------------------------------------
    # Columns
    # --------------------------------------------------------

    required_columns = {
        "case_id",
        "stage",
        "evidence",
        "expected_decision",
        "update_type",
    }

    assert set(df.columns) == required_columns, (
        "Unexpected columns: "
        f"{set(df.columns) ^ required_columns}"
    )

    print(
        "Columns:               OK"
    )

    # --------------------------------------------------------
    # Stage structure
    # --------------------------------------------------------

    expected_stages = {
        "E0",
        "E1",
        "E2",
        "E3",
    }

    for case_id, group in df.groupby("case_id"):

        assert set(group["stage"]) == expected_stages, (
            f"{case_id}: invalid stages"
        )

        assert len(group) == 4, (
            f"{case_id}: expected 4 stages, "
            f"found {len(group)}"
        )

    print(
        "Stage structure:       OK"
    )

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

    print(
        "Decision values:       OK"
    )

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

    print(
        "Update types:          OK"
    )

    # --------------------------------------------------------
    # Exactly one reversal per case
    # --------------------------------------------------------

    reversal_counts = (
        df.groupby("case_id")[
            "update_type"
        ]
        .apply(
            lambda x: (
                x == "REQUIRED_REVERSAL"
            ).sum()
        )
    )

    assert (
        reversal_counts == 1
    ).all(), (
        "Every case must contain exactly "
        "one REQUIRED_REVERSAL."
    )

    print(
        "One reversal per case: OK"
    )

    # --------------------------------------------------------
    # One INITIAL per case
    # --------------------------------------------------------

    initial_counts = (
        df.groupby("case_id")[
            "update_type"
        ]
        .apply(
            lambda x: (
                x == "INITIAL"
            ).sum()
        )
    )

    assert (
        initial_counts == 1
    ).all(), (
        "Every case must contain exactly "
        "one INITIAL stage."
    )

    print(
        "One initial stage:     OK"
    )

    # --------------------------------------------------------
    # Reversal-stage distribution
    # --------------------------------------------------------

    reversal_stage_counts = (
        df[
            df["update_type"]
            == "REQUIRED_REVERSAL"
        ]
        .groupby("stage")
        .size()
        .to_dict()
    )

    expected_reversal_distribution = {
        "E1": 10,
        "E2": 20,
        "E3": 10,
    }

    assert (
        reversal_stage_counts
        == expected_reversal_distribution
    ), (
        "Unexpected reversal-stage distribution:\n"
        f"Expected: "
        f"{expected_reversal_distribution}\n"
        f"Actual: "
        f"{reversal_stage_counts}"
    )

    print()
    print(
        "Reversal-stage distribution:"
    )

    for stage in [
        "E1",
        "E2",
        "E3",
    ]:
        print(
            f"  {stage}: "
            f"{reversal_stage_counts.get(stage, 0)}"
        )

    # --------------------------------------------------------
    # Evidence completeness
    # --------------------------------------------------------

    assert (
        df["evidence"]
        .notna()
        .all()
    )

    assert (
        df["evidence"]
        .str.strip()
        .ne("")
        .all()
    )

    print(
        "Evidence completeness: OK"
    )

    # --------------------------------------------------------
    # Trajectory display
    # --------------------------------------------------------

    print()
    print(
        "Expected trajectories:"
    )

    for case_id, group in df.groupby(
        "case_id"
    ):

        ordered = group.sort_values(
            "stage"
        )

        trajectory = " -> ".join(
            ordered[
                "expected_decision"
            ]
        )

        reversal_stage = (
            ordered.loc[
                ordered["update_type"]
                == "REQUIRED_REVERSAL",
                "stage",
            ]
            .iloc[0]
        )

        print(
            f"  {case_id}: "
            f"{trajectory} "
            f"(reversal={reversal_stage})"
        )

    print()
    print(
        "All validation checks passed."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "LLM EVIDENCE UPDATE VALIDATION"
    )
    print(
        "CREATE V1 CLEAR REVERSAL DATASET"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Preserve original pilot cases
    # --------------------------------------------------------

    rows = list(PILOT_CASES)

    # --------------------------------------------------------
    # Add CASE_011 ... CASE_040
    # --------------------------------------------------------

    rows.extend(
        build_additional_cases()
    )

    df = pd.DataFrame(rows)

    # --------------------------------------------------------
    # Column order
    # --------------------------------------------------------

    df = df[
        [
            "case_id",
            "stage",
            "evidence",
            "expected_decision",
            "update_type",
        ]
    ]

    # --------------------------------------------------------
    # Deterministic ordering
    # --------------------------------------------------------

    stage_order = {
        "E0": 0,
        "E1": 1,
        "E2": 2,
        "E3": 3,
    }

    df["_case_number"] = (
        df["case_id"]
        .str.extract(
            r"(\d+)"
        )[0]
        .astype(int)
    )

    df["_stage_order"] = (
        df["stage"]
        .map(stage_order)
    )

    df = (
        df.sort_values(
            [
                "_case_number",
                "_stage_order",
            ]
        )
        .drop(
            columns=[
                "_case_number",
                "_stage_order",
            ]
        )
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

    print(
        f"Output: {OUTPUT_PATH}"
    )

    print(
        f"Shape:  {df.shape}"
    )


if __name__ == "__main__":
    main()