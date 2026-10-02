"""
LLM Evidence Update Validation — V1 Clear Reversal

Tests whether an LLM appropriately updates a diagnosis
when new evidence is introduced sequentially.

Cases:
    CASE_001 ... CASE_010

Evidence stages:
    E0
    E1
    E2
    E3

Provider: Groq
Model: openai/gpt-oss-120b
Temperature: 0
"""

from pathlib import Path
import json

import pandas as pd
from groq import Groq


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "openai/gpt-oss-120b"
TEMPERATURE = 0

DATA_PATH = Path("data/clear_reversal_v1.csv")

OUTPUT_PATH = Path(
    "results/v1_clear_reversal.csv"
)


# ============================================================
# CLIENT
# ============================================================

client = Groq()


# ============================================================
# PROMPTS
# ============================================================

SYSTEM_PROMPT = """
You are diagnosing a software incident.

Your task is to identify the most likely root cause based ONLY
on the evidence provided so far.

Possible root causes:

DATABASE
NETWORK
APPLICATION
CONFIGURATION
UNCERTAIN

Rules:

- Use only the evidence explicitly provided.
- Do not assume information that is not provided.
- Do not use hidden labels or metadata.
- Do not assume that the previous diagnosis was correct.
- Update your diagnosis when new evidence warrants it.
- Do not change your diagnosis merely because new evidence
  introduces another plausible possibility.
- If the available evidence is insufficient to distinguish
  between the hypotheses, return UNCERTAIN.

Return exactly one decision.

Return JSON in this format:

{
    "decision": "DATABASE" or "NETWORK" or "APPLICATION"
                  or "CONFIGURATION" or "UNCERTAIN",
    "rationale": "brief explanation based only on the evidence"
}
"""


# ============================================================
# BUILD PROMPT
# ============================================================

def build_prompt(case_id, evidence_history):
    """
    Build cumulative evidence for the current stage.

    The model sees all evidence available up to the current
    stage. Earlier evidence is not repeated as separate
    decisions; it remains part of the accumulated case.
    """

    evidence_text = "\n\n".join(
        f"{stage}:\n{evidence}"
        for stage, evidence in evidence_history
    )

    return f"""
Incident case: {case_id}

Evidence available so far:

{evidence_text}

Based on ALL evidence available so far,
identify the most likely root cause.

Return the decision and a brief rationale.
"""


# ============================================================
# LLM CALL
# ============================================================

def evaluate_stage(case_id, evidence_history):
    prompt = build_prompt(
        case_id,
        evidence_history,
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    content = response.choices[0].message.content

    result = json.loads(content)

    decision = result.get("decision")
    rationale = result.get("rationale")

    valid_decisions = {
        "DATABASE",
        "NETWORK",
        "APPLICATION",
        "CONFIGURATION",
        "UNCERTAIN",
    }

    if decision not in valid_decisions:
        raise ValueError(
            f"Invalid decision returned by model: {decision}"
        )

    return decision, rationale


# ============================================================
# RATE LIMIT DETECTION
# ============================================================

def is_rate_limit_error(error):
    message = str(error)

    return (
        "429" in message
        or "rate_limit_exceeded" in message
        or "Rate limit reached" in message
    )


# ============================================================
# LOAD EXISTING RESULTS
# ============================================================

def load_existing_results():
    if not OUTPUT_PATH.exists():
        return pd.DataFrame()

    existing = pd.read_csv(OUTPUT_PATH)

    print()
    print("=" * 70)
    print("EXISTING RESULTS FOUND")
    print("=" * 70)
    print(f"File:                 {OUTPUT_PATH}")
    print(f"Rows in file:         {len(existing)}")

    required_columns = {
        "case_id",
        "decision_e0",
        "decision_e1",
        "decision_e2",
        "decision_e3",
    }

    missing = required_columns - set(existing.columns)

    if missing:
        print(
            "Existing file has incompatible structure. "
            "Starting from scratch."
        )
        return pd.DataFrame()

    completed_mask = (
        existing[
            [
                "decision_e0",
                "decision_e1",
                "decision_e2",
                "decision_e3",
            ]
        ]
        .notna()
        .all(axis=1)
    )

    completed_count = completed_mask.sum()

    print(f"Completed cases:      {completed_count}")
    print(
        f"Incomplete cases:     "
        f"{len(existing) - completed_count}"
    )

    return existing


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(existing, new_result):
    new_row = pd.DataFrame([new_result])

    combined = pd.concat(
        [existing, new_row],
        ignore_index=True,
    )

    combined = combined.drop_duplicates(
        subset=["case_id"],
        keep="last",
    )

    combined = combined.sort_values("case_id")

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    combined.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    return combined


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("LLM EVIDENCE UPDATE VALIDATION — V1 CLEAR REVERSAL")
    print("=" * 70)

    print()
    print("[1] LOADING DATA")

    df = pd.read_csv(DATA_PATH)

    print(f"Dataset shape: {df.shape}")

    required_columns = {
        "case_id",
        "stage",
        "evidence",
        "expected_decision",
        "update_type",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    print("Required columns: OK")

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    expected_stages = {"E0", "E1", "E2", "E3"}

    for case_id, group in df.groupby("case_id"):

        stages = set(group["stage"])

        if stages != expected_stages:
            raise ValueError(
                f"{case_id}: expected stages "
                f"{sorted(expected_stages)}, "
                f"found {sorted(stages)}"
            )

    print("Stage structure: OK")

    # --------------------------------------------------------
    # Load existing results
    # --------------------------------------------------------

    existing = load_existing_results()

    if len(existing) > 0:

        completed_mask = (
            existing[
                [
                    "decision_e0",
                    "decision_e1",
                    "decision_e2",
                    "decision_e3",
                ]
            ]
            .notna()
            .all(axis=1)
        )

        completed_cases = set(
            existing.loc[
                completed_mask,
                "case_id",
            ]
        )

    else:
        completed_cases = set()

    case_ids = sorted(df["case_id"].unique())

    total_cases = len(case_ids)

    print()
    print("=" * 70)
    print("RESUME STATUS")
    print("=" * 70)

    print(f"Total cases:          {total_cases}")
    print(f"Already completed:    {len(completed_cases)}")
    print(
        f"Remaining:            "
        f"{total_cases - len(completed_cases)}"
    )

    if len(completed_cases) == total_cases:

        print()
        print("All cases are already completed.")
        print("Nothing to do.")
        return

    # --------------------------------------------------------
    # Process cases
    # --------------------------------------------------------

    for case_index, case_id in enumerate(
        case_ids,
        start=1,
    ):

        if case_id in completed_cases:
            continue

        case_df = (
            df[df["case_id"] == case_id]
            .sort_values("stage")
        )

        print()
        print("=" * 70)
        print(
            f"CASE {case_index:02d}/{total_cases}: "
            f"{case_id}"
        )
        print("=" * 70)

        result = {
            "case_id": case_id,

            "expected_e0": None,
            "expected_e1": None,
            "expected_e2": None,
            "expected_e3": None,

            "decision_e0": None,
            "decision_e1": None,
            "decision_e2": None,
            "decision_e3": None,

            "rationale_e0": None,
            "rationale_e1": None,
            "rationale_e2": None,
            "rationale_e3": None,

            "error": None,
        }

        try:

            # ------------------------------------------------
            # Sequential evidence evaluation
            # ------------------------------------------------

            evidence_history = []

            for _, row in case_df.iterrows():

                stage = row["stage"]
                evidence = row["evidence"]

                expected_decision = (
                    row["expected_decision"]
                )

                evidence_history.append(
                    (stage, evidence)
                )

                decision, rationale = evaluate_stage(
                    case_id,
                    evidence_history,
                )

                stage_number = int(stage[1])

                result[
                    f"expected_e{stage_number}"
                ] = expected_decision

                result[
                    f"decision_e{stage_number}"
                ] = decision

                result[
                    f"rationale_e{stage_number}"
                ] = rationale

                print()
                print(
                    f"{stage}: "
                    f"Expected={expected_decision} | "
                    f"Model={decision}"
                )

            # ------------------------------------------------
            # Save immediately after complete case
            # ------------------------------------------------

            existing = save_results(
                existing,
                result,
            )

            completed_cases.add(case_id)

            print()
            print(
                f"Saved: {OUTPUT_PATH}"
            )

        except Exception as error:

            if is_rate_limit_error(error):

                print()
                print("=" * 70)
                print("GROQ RATE LIMIT REACHED")
                print("=" * 70)

                print(
                    "Successfully completed cases "
                    "have already been saved."
                )

                print(
                    "Run this same script again after "
                    "the quota resets."
                )

                break

            print(
                f"ERROR in {case_id}: {error}"
            )

            continue

    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    if OUTPUT_PATH.exists():

        final_df = pd.read_csv(
            OUTPUT_PATH
        )

        completed_mask = (
            final_df[
                [
                    "decision_e0",
                    "decision_e1",
                    "decision_e2",
                    "decision_e3",
                ]
            ]
            .notna()
            .all(axis=1)
        )

        completed_count = (
            completed_mask.sum()
        )

    else:
        completed_count = 0

    print()
    print("=" * 70)
    print("V1 STATUS")
    print("=" * 70)

    print(
        f"Completed: "
        f"{completed_count}/{total_cases}"
    )

    print(
        f"Remaining: "
        f"{total_cases - completed_count}"
    )

    if completed_count == total_cases:

        print()
        print(
            "V1 CLEAR REVERSAL COMPLETE"
        )

        print(
            f"Results saved to: "
            f"{OUTPUT_PATH}"
        )

    else:

        print()
        print(
            "V1 is incomplete, but all successful "
            "results have been preserved."
        )


if __name__ == "__main__":
    main()