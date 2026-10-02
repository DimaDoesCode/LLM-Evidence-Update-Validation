"""
LLM Evidence Update Validation — V1 Analysis

Analyzes sequential decision trajectories and classifies
each transition between evidence stages.

Transition classes:

    CORRECT_MAINTENANCE
    CORRECT_REVERSAL
    MISSED_REVERSAL
    PREMATURE_REVERSAL
    RECOVERY_FROM_INITIAL_ERROR
    RECOVERY_FROM_PREMATURE_ERROR
    PERSISTENT_ERROR
"""

from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RESULTS_PATH = Path(
    "results/v1_clear_reversal.csv"
)

ANALYSIS_PATH = Path(
    "results/v1_clear_reversal_analysis.csv"
)


# ============================================================
# STAGES
# ============================================================

STAGES = ["e0", "e1", "e2", "e3"]


# ============================================================
# TRANSITION CLASSIFICATION
# ============================================================

def classify_transition(
    expected_prev,
    expected_curr,
    model_prev,
    model_curr,
    had_premature_reversal,
):
    """
    Classify one transition.

    Important distinction:

    RECOVERY_FROM_INITIAL_ERROR
        The model was already wrong at E0 and later
        reaches the expected decision.

    RECOVERY_FROM_PREMATURE_ERROR
        The model was initially correct, then made a
        premature reversal, and later returns to the
        expected trajectory.

    Every transition must belong to exactly one class.
    """

    expected_changed = (
        expected_prev != expected_curr
    )

    model_changed = (
        model_prev != model_curr
    )

    model_prev_correct = (
        model_prev == expected_prev
    )

    model_curr_correct = (
        model_curr == expected_curr
    )

    # --------------------------------------------------------
    # Model was correct before the transition
    # --------------------------------------------------------

    if model_prev_correct:

        # Expected decision remains unchanged
        if not expected_changed:

            if not model_changed:
                return "CORRECT_MAINTENANCE"

            return "PREMATURE_REVERSAL"

        # Expected decision changes
        if (
            model_changed
            and model_curr_correct
        ):
            return "CORRECT_REVERSAL"

        if not model_changed:
            return "MISSED_REVERSAL"

        return "PERSISTENT_ERROR"

    # --------------------------------------------------------
    # Model was incorrect before the transition
    # --------------------------------------------------------

    else:

        # Model reaches the expected decision
        if model_curr_correct:

            if had_premature_reversal:
                return "RECOVERY_FROM_PREMATURE_ERROR"

            return "RECOVERY_FROM_INITIAL_ERROR"

        # Model remains incorrect
        return "PERSISTENT_ERROR"


# ============================================================
# ANALYZE CASE
# ============================================================

def analyze_case(row):
    """
    Analyze all three transitions for one case.

    The flag `had_premature_reversal` tracks whether the
    current case has previously experienced a premature
    reversal.

    This allows us to distinguish:

        INITIAL ERROR -> RECOVERY

    from:

        PREMATURE REVERSAL -> RECOVERY
    """

    transitions = []

    had_premature_reversal = False

    for i in range(len(STAGES) - 1):

        prev_stage = STAGES[i]
        curr_stage = STAGES[i + 1]

        expected_prev = row[
            f"expected_{prev_stage}"
        ]

        expected_curr = row[
            f"expected_{curr_stage}"
        ]

        model_prev = row[
            f"decision_{prev_stage}"
        ]

        model_curr = row[
            f"decision_{curr_stage}"
        ]

        transition_type = classify_transition(
            expected_prev=expected_prev,
            expected_curr=expected_curr,
            model_prev=model_prev,
            model_curr=model_curr,
            had_premature_reversal=(
                had_premature_reversal
            ),
        )

        transitions.append(
            {
                "case_id": row["case_id"],
                "transition": (
                    f"{prev_stage.upper()}->"
                    f"{curr_stage.upper()}"
                ),
                "expected_prev": expected_prev,
                "expected_curr": expected_curr,
                "model_prev": model_prev,
                "model_curr": model_curr,
                "transition_type": transition_type,
            }
        )

        # Once a premature reversal occurred,
        # remember it for subsequent transitions.
        if (
            transition_type
            == "PREMATURE_REVERSAL"
        ):
            had_premature_reversal = True

    return transitions


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "LLM EVIDENCE UPDATE VALIDATION — V1 ANALYSIS"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Load results
    # --------------------------------------------------------

    print()
    print("[1] LOADING RESULTS")

    if not RESULTS_PATH.exists():
        raise FileNotFoundError(
            f"Results file not found: {RESULTS_PATH}"
        )

    df = pd.read_csv(
        RESULTS_PATH
    )

    required_columns = {
        "case_id",

        "expected_e0",
        "expected_e1",
        "expected_e2",
        "expected_e3",

        "decision_e0",
        "decision_e1",
        "decision_e2",
        "decision_e3",
    }

    missing = (
        required_columns
        - set(df.columns)
    )

    if missing:
        raise ValueError(
            "Missing required columns: "
            f"{sorted(missing)}"
        )

    # --------------------------------------------------------
    # Keep only complete cases
    # --------------------------------------------------------

    decision_columns = [
        f"decision_{stage}"
        for stage in STAGES
    ]

    complete_mask = (
        df[decision_columns]
        .notna()
        .all(axis=1)
    )

    df = df.loc[
        complete_mask
    ].copy()

    print(
        f"Complete cases: {len(df)}"
    )

    if len(df) == 0:
        raise ValueError(
            "No complete cases available."
        )

    # --------------------------------------------------------
    # Analyze transitions
    # --------------------------------------------------------

    print()
    print(
        "[2] CLASSIFYING TRANSITIONS"
    )

    all_transitions = []

    for _, row in df.iterrows():

        transitions = analyze_case(
            row
        )

        all_transitions.extend(
            transitions
        )

    analysis_df = pd.DataFrame(
        all_transitions
    )

    # --------------------------------------------------------
    # Save detailed analysis
    # --------------------------------------------------------

    ANALYSIS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    analysis_df.to_csv(
        ANALYSIS_PATH,
        index=False,
    )

    # --------------------------------------------------------
    # Transition counts
    # --------------------------------------------------------

    counts = (
        analysis_df[
            "transition_type"
        ]
        .value_counts()
        .to_dict()
    )

    correct_maintenance = counts.get(
        "CORRECT_MAINTENANCE",
        0,
    )

    correct_reversal = counts.get(
        "CORRECT_REVERSAL",
        0,
    )

    missed_reversal = counts.get(
        "MISSED_REVERSAL",
        0,
    )

    premature_reversal = counts.get(
        "PREMATURE_REVERSAL",
        0,
    )

    recovery_initial = counts.get(
        "RECOVERY_FROM_INITIAL_ERROR",
        0,
    )

    recovery_premature = counts.get(
        "RECOVERY_FROM_PREMATURE_ERROR",
        0,
    )

    persistent_error = counts.get(
        "PERSISTENT_ERROR",
        0,
    )

    total_transitions = len(
        analysis_df
    )

    classified_transitions = (
        correct_maintenance
        + correct_reversal
        + missed_reversal
        + premature_reversal
        + recovery_initial
        + recovery_premature
        + persistent_error
    )

    # --------------------------------------------------------
    # Initial decision accuracy
    # --------------------------------------------------------

    initial_correct = (
        df["decision_e0"]
        == df["expected_e0"]
    )

    initial_correct_count = (
        initial_correct.sum()
    )

    initial_error_count = (
        len(df)
        - initial_correct_count
    )

    initial_accuracy = (
        initial_correct_count
        / len(df)
        * 100
    )

    # --------------------------------------------------------
    # Final decision accuracy
    # --------------------------------------------------------

    final_correct = (
        df["decision_e3"]
        == df["expected_e3"]
    )

    final_correct_count = (
        final_correct.sum()
    )

    final_accuracy = (
        final_correct_count
        / len(df)
        * 100
    )

    # --------------------------------------------------------
    # Required reversal analysis
    # --------------------------------------------------------

    expected_changes = (
        analysis_df[
            analysis_df[
                "expected_prev"
            ]
            != analysis_df[
                "expected_curr"
            ]
        ]
    )

    required_reversal_count = len(
        expected_changes
    )

    correct_reversal_count = (
        expected_changes[
            "transition_type"
        ]
        == "CORRECT_REVERSAL"
    ).sum()

    missed_reversal_count = (
        expected_changes[
            "transition_type"
        ]
        == "MISSED_REVERSAL"
    ).sum()

    if required_reversal_count > 0:

        required_reversal_accuracy = (
            correct_reversal_count
            / required_reversal_count
            * 100
        )

    else:

        required_reversal_accuracy = 100.0

    # --------------------------------------------------------
    # Missed reversal rate
    # --------------------------------------------------------

    if required_reversal_count > 0:

        missed_reversal_rate = (
            missed_reversal_count
            / required_reversal_count
            * 100
        )

    else:

        missed_reversal_rate = 0.0

    # --------------------------------------------------------
    # Premature reversal rate
    #
    # Denominator:
    # transitions where:
    #
    #   1. model was correct before transition
    #   2. expected decision should remain unchanged
    #
    # --------------------------------------------------------

    premature_opportunities = (
        analysis_df[
            (
                analysis_df[
                    "expected_prev"
                ]
                ==
                analysis_df[
                    "expected_curr"
                ]
            )
            &
            (
                analysis_df[
                    "model_prev"
                ]
                ==
                analysis_df[
                    "expected_prev"
                ]
            )
        ]
    )

    premature_denominator = len(
        premature_opportunities
    )

    if premature_denominator > 0:

        premature_reversal_rate = (
            premature_reversal
            / premature_denominator
            * 100
        )

    else:

        premature_reversal_rate = 0.0

    # --------------------------------------------------------
    # Recovery from INITIAL error
    #
    # Denominator:
    # cases with an incorrect E0 decision.
    #
    # Numerator:
    # those cases that have a
    # RECOVERY_FROM_INITIAL_ERROR transition.
    # --------------------------------------------------------

    initial_error_cases = df[
        ~initial_correct
    ]

    initial_error_case_ids = set(
        initial_error_cases[
            "case_id"
        ]
    )

    recovered_initial_case_ids = set(
        analysis_df[
            analysis_df[
                "transition_type"
            ]
            == "RECOVERY_FROM_INITIAL_ERROR"
        ]["case_id"]
    )

    recovered_initial_case_ids = (
        recovered_initial_case_ids
        & initial_error_case_ids
    )

    recovered_initial_cases = len(
        recovered_initial_case_ids
    )

    if initial_error_count > 0:

        recovery_initial_rate = (
            recovered_initial_cases
            / initial_error_count
            * 100
        )

    else:

        recovery_initial_rate = 100.0

    # --------------------------------------------------------
    # Recovery from premature reversal
    #
    # This is a separate phenomenon and is NOT included
    # in recovery from initial error.
    # --------------------------------------------------------

    premature_cases = set(
        analysis_df[
            analysis_df[
                "transition_type"
            ]
            == "PREMATURE_REVERSAL"
        ]["case_id"]
    )

    recovered_premature_cases = set(
        analysis_df[
            analysis_df[
                "transition_type"
            ]
            == "RECOVERY_FROM_PREMATURE_ERROR"
        ]["case_id"]
    )

    recovered_premature_cases = (
        recovered_premature_cases
        & premature_cases
    )

    recovery_premature_case_count = len(
        recovered_premature_cases
    )

    if len(premature_cases) > 0:

        recovery_premature_rate = (
            recovery_premature_case_count
            / len(premature_cases)
            * 100
        )

    else:

        recovery_premature_rate = 0.0

    # --------------------------------------------------------
    # Validation checks
    # --------------------------------------------------------

    print()
    print(
        "[3] VALIDATION CHECKS"
    )

    print(
        f"Total transitions:       "
        f"{total_transitions}"
    )

    print(
        f"Classified transitions:  "
        f"{classified_transitions}"
    )

    if (
        classified_transitions
        != total_transitions
    ):
        raise AssertionError(
            "Transition classification mismatch: "
            "not every transition belongs to exactly "
            "one category."
        )

    print(
        "Transition coverage:     OK"
    )

    if (
        recovered_initial_cases
        > initial_error_count
    ):
        raise AssertionError(
            "Initial recovery count exceeds "
            "initial error count."
        )

    print(
        "Initial recovery check:   OK"
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "V1 VALIDATION SUMMARY"
    )
    print("=" * 70)

    print()
    print(
        f"Complete cases: "
        f"{len(df)}"
    )

    print()
    print(
        f"Initial Decision Accuracy:          "
        f"{initial_accuracy:.1f}%"
    )

    print(
        f"Final Decision Accuracy:            "
        f"{final_accuracy:.1f}%"
    )

    print(
        f"Required Reversal Accuracy:         "
        f"{required_reversal_accuracy:.1f}%"
    )

    print(
        f"Belief Inertia / Missed Reversal Rate: "
        f"{missed_reversal_rate:.1f}%"
    )

    print(
        f"Premature Reversal Rate:             "
        f"{premature_reversal_rate:.1f}%"
    )

    print(
        f"Recovery from Initial Error:         "
        f"{recovery_initial_rate:.1f}%"
    )

    print(
        f"Recovery from Premature Error:       "
        f"{recovery_premature_rate:.1f}%"
    )

    print()
    print("=" * 70)
    print(
        "TRANSITION COUNTS"
    )
    print("=" * 70)

    print(
        f"Correct Maintenance:          "
        f"{correct_maintenance}"
    )

    print(
        f"Correct Reversal:              "
        f"{correct_reversal}"
    )

    print(
        f"Missed Reversal:               "
        f"{missed_reversal}"
    )

    print(
        f"Premature Reversal:            "
        f"{premature_reversal}"
    )

    print(
        f"Recovery from Initial Error:   "
        f"{recovery_initial}"
    )

    print(
        f"Recovery from Premature Error: "
        f"{recovery_premature}"
    )

    print(
        f"Persistent Error:              "
        f"{persistent_error}"
    )

    print()
    print(
        f"TOTAL:                         "
        f"{classified_transitions}"
    )

    print()
    print("=" * 70)
    print(
        "INITIAL DECISION"
    )
    print("=" * 70)

    print(
        f"Initial Correct:      "
        f"{initial_correct_count}"
    )

    print(
        f"Initial Errors:       "
        f"{initial_error_count}"
    )

    print(
        f"Cases with Recovery:  "
        f"{recovered_initial_cases}"
    )

    print()
    print(
        f"Analysis saved to: "
        f"{ANALYSIS_PATH}"
    )


if __name__ == "__main__":
    main()