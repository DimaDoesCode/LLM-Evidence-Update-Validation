# LLM Evidence Update Validation

A compact validation experiment for testing how an LLM updates decisions when new evidence arrives sequentially.

The project focuses on **evidence-driven decision updating**, with particular attention to the difference between:

* reaching the correct final decision;
* and following a correct decision trajectory as evidence accumulates.

---

## Validation Question

A model may receive new information over several stages:

```text
E0 → E1 → E2 → E3
```

The expected decision may initially be:

```text
DATABASE
```

and later change when decisive evidence appears:

```text
DATABASE → DATABASE → NETWORK → NETWORK
```

The validation question is:

> Does the model change its decision at the appropriate point when the evidence changes?

The project therefore evaluates not only the final answer, but also the **trajectory of decisions**.

---

## V1 — Clear Reversal

V1 uses synthetic software incident diagnosis cases.

Each case contains:

* an initial hypothesis;
* sequential evidence;
* exactly one expected decision reversal;
* confirmation after the reversal.

Possible root causes:

```text
DATABASE
NETWORK
APPLICATION
CONFIGURATION
UNCERTAIN
```

### Dataset

```text
40 cases
160 observations
4 stages per case
1 required reversal per case
```

Reversal distribution:

```text
E1: 10 cases
E2: 20 cases
E3: 10 cases
```

The dataset passed a deterministic structural integrity audit before inference.

---

## Model

Provider:

```text
Groq
```

Model:

```text
openai/gpt-oss-120b
```

Temperature:

```text
0
```

The model receives cumulative evidence and produces a structured decision plus a short rationale at every stage.

---

## V1 Results

| Metric                            |     Result |
| --------------------------------- | ---------: |
| Initial Decision Accuracy         |  **87.5%** |
| Final Decision Accuracy           | **100.0%** |
| Required Reversal Accuracy        | **100.0%** |
| Fully Correct Decision Trajectory |  **60.0%** |

The key observation is the gap between final and trajectory correctness.

The model reached the expected final decision in all 40 cases, but only 24 cases followed the expected trajectory at every stage.

This means that **final correctness alone does not fully describe sequential decision behavior**.

---

## Example

### CASE_003

Expected:

```text
APPLICATION → APPLICATION → CONFIGURATION → CONFIGURATION
```

Model:

```text
APPLICATION → CONFIGURATION → CONFIGURATION → CONFIGURATION
```

The model identified the final root cause correctly, but changed its decision one stage too early.

This is classified as a **premature reversal**.

---

## Why This Matters

For a one-shot classification task, the final answer may be the primary object of evaluation.

For a system that continuously receives evidence and updates a decision, the path to the final decision can also matter.

V1 demonstrates a simple way to make this behavior measurable.

The project therefore separates:

```text
Outcome correctness
```

from:

```text
Decision trajectory correctness
```

---

## Validation Scope

V1 is intentionally narrow.

It does not attempt to build a general LLM evaluation framework.

It tests one specific behavioral property:

> **Whether an LLM updates a diagnosis appropriately when decisive evidence appears during a sequential evidence stream.**

The dataset is synthetic and the experiment uses a single model configuration.

---

## Repository Structure

```text
LLM-Evidence-Update-Validation/
│
├── data/
│   └── clear_reversal_v1.csv
│
├── reports/
│   └── V1_clear_reversal.md
│
├── results/
│   ├── v1_clear_reversal.csv
│   └── v1_clear_reversal_dataset_audit.csv
│
├── scripts/
│   ├── generate_cases.py
│   ├── audit_clear_reversal_v1.py
│   └── run_v1_clear_reversal.py
│
└── README.md
```

---

## Running the Validation

Generate the dataset:

```bash
python scripts/generate_cases.py
```

Run the dataset integrity audit:

```bash
python scripts/audit_clear_reversal_v1.py
```

Run the LLM validation:

```bash
python scripts/run_v1_clear_reversal.py
```

The inference script is resumable and stores completed case results, allowing the experiment to continue after an interrupted run or API rate limit.

---

## Project Status

### V1 — Clear Reversal

**Completed**

* Dataset generation
* Dataset integrity audit
* Sequential LLM inference
* Result collection
* V1 analysis
* Validation report

The project currently stops at V1.

Further validation dimensions are intentionally left open rather than being added without a clear validation question.

---

## Limitations

The current results should not be interpreted as a general benchmark of LLM reasoning.

The experiment is limited by:

* synthetic data;
* 40 cases;
* one diagnostic domain;
* one model;
* one provider configuration;
* deterministic temperature setting;
* predefined expected trajectories.

The experiment is intended as a **validation prototype**, not a general-purpose benchmark.

---

## Main Takeaway

V1 produced an important distinction:

```text
Final Decision Accuracy:       100%
Fully Correct Trajectory:       60%
```

The model consistently reached the expected final decision, but intermediate decision states were substantially less stable.

This suggests that, for sequential LLM decision systems, **how a decision changes as evidence accumulates can be a distinct validation target from whether the final decision is correct.**
