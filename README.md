# LLM Evidence Update Validation

A compact validation experiment for testing how an LLM updates decisions when new evidence arrives sequentially.

The project focuses on **evidence-driven decision updating**, with particular attention to the difference between:

* reaching the correct final decision;
* and following a correct decision trajectory as evidence accumulates.

The validation question is related to the broader research area of **belief revision in large language models**, including work on belief revision benchmarks, rational belief-update properties, and anchoring effects in LLM judgments. [1–3]

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

The project therefore evaluates not only the final answer, but also the **decision trajectory**.

This is closely related to the problem of **belief revision** studied in recent LLM research. Wilie et al. introduced Belief-R, a benchmark designed to test whether language models appropriately revise conclusions when additional premises require previous inferences to be changed. [1]

More recently, AGM-BENCH framed LLM belief revision in terms of classical rationality postulates and iterated belief revision, providing a more formal approach to evaluating whether updates are performed in a rational manner. [2]

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

This distinction is consistent with a broader line of research showing that LLMs can have difficulty updating conclusions appropriately when information changes. Belief-R, for example, evaluates both situations where a previous conclusion should be revised and situations where it should remain unchanged. [1]

The problem is also related to **anchoring**: prior information can influence subsequent LLM judgments even when that information should no longer determine the result. Nguyen reports anchoring effects across several LLMs in forecasting tasks. [3]

---

## Validation Scope

V1 is intentionally narrow.

It does not attempt to build a general LLM evaluation framework.

It tests one specific behavioral property:

> **Whether an LLM updates a diagnosis appropriately when decisive evidence appears during a sequential evidence stream.**

The dataset is synthetic and the experiment uses a single model configuration.

The experiment should therefore be viewed as a **validation prototype**, rather than as a benchmark of general reasoning ability.

---

## Relation to Existing Research

The project is positioned within the broader problem of **LLM belief revision and evidence-driven updating**, but uses a deliberately simpler validation setup.

### Belief revision

Wilie et al. introduced **Belief-R**, a dataset for evaluating whether LMs revise conclusions when new premises invalidate or modify earlier inferences. Their work emphasizes that models can struggle both with required updates and with situations where an update should *not* occur. [1]

V1 uses the same general idea of sequential information, but translates it into a concrete **decision trajectory**:

```text
initial decision
      ↓
new evidence
      ↓
decision update
      ↓
confirmation
```

### Rational belief revision

Jenkins' **AGM-BENCH** approaches the problem from a more formal perspective. It evaluates LLM belief revision against rationality postulates derived from AGM belief revision theory and extends the analysis to iterated revision. [2]

V1 does not attempt to reproduce these formal postulates. Instead, it uses a simpler operational criterion:

```text
Expected reversal point
        vs.
Observed reversal point
```

This makes the experiment easier to reproduce and directly applicable to sequential decision systems.

### Anchoring

Nguyen's study investigates anchoring effects in LLM-generated forecasts and reports that prior numerical information can influence subsequent model judgments. [3]

While V1 does not explicitly test anchoring, the concept is relevant because a sequential decision system must distinguish between:

```text
evidence that should remain influential
```

and:

```text
previous information that should be superseded by new evidence
```

This provides a possible direction for future validation experiments.

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

In particular, the results should not be directly compared numerically with Belief-R or AGM-BENCH. Those studies use different datasets, tasks, evaluation criteria, and model populations. [1, 2]

---

## Main Takeaway

V1 produced an important distinction:

```text
Final Decision Accuracy:       100%

Fully Correct Trajectory:       60%
```

The model consistently reached the expected final decision, but intermediate decision states were substantially less stable.

This suggests that, for sequential LLM decision systems, **how a decision changes as evidence accumulates can be a distinct validation target from whether the final decision is correct.**

---

## References

**[1]** Wilie, B., Cahyawijaya, S., Ishii, E., He, J., & Fung, P. (2024).
**Belief Revision: The Adaptability of Large Language Models Reasoning.**
*Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing (EMNLP 2024), 10480–10496.*
DOI: 10.18653/v1/2024.emnlp-main.586
[ACL Anthology](https://aclanthology.org/2024.emnlp-main.586/)

**[2]** Jenkins, B. (2026).
**AGM-BENCH: Do Large Language Models Revise Beliefs Rationally?**
*International Conference on Learning Representations (ICLR 2026).*
[OpenReview](https://openreview.net/pdf?id=2s1BujG84C)

**[3]** Nguyen, J. K. (2024).
**Human bias in AI models? Anchoring effects and mitigation strategies in large language models.**
*Journal of Behavioral and Experimental Finance, 43, 100971.*
DOI: 10.1016/j.jbef.2024.100971
[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2214635024000868)
