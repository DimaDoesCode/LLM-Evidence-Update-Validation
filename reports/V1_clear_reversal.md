# V1 — Clear Reversal Validation

## 1. Objective

The purpose of V1 is to validate whether an LLM correctly updates a decision when new evidence arrives sequentially.

The validation focuses on **decision trajectory**, not only on the final answer.

The model receives evidence in four sequential stages:

```text
E0 → E1 → E2 → E3
```

At each stage, the model must decide whether to:

* maintain the current hypothesis;
* or update it when the new evidence warrants a change.

The central validation question is:

> Does the model change its decision at the right point, for the right evidence, while avoiding premature changes?

---

## 2. Validation Object

The validation object is a sequential diagnostic process:

```text
Evidence → LLM Decision → New Evidence → LLM Update → ...
```

Possible root causes:

* `DATABASE`
* `NETWORK`
* `APPLICATION`
* `CONFIGURATION`
* `UNCERTAIN`

Each test case contains exactly one required decision reversal.

The expected trajectory therefore has the form:

```text
A → A → B → B
```

or:

```text
A → B → B → B
```

or:

```text
A → A → A → B
```

depending on the reversal stage.

---

## 3. Dataset

The V1 dataset contains:

* **40 cases**
* **160 observations**
* **4 evidence stages per case**
* **1 required reversal per case**

Reversal timing:

| Reversal stage |  Cases |
| -------------- | -----: |
| E1             |     10 |
| E2             |     20 |
| E3             |     10 |
| **Total**      | **40** |

The dataset was subjected to a deterministic integrity audit before inference.

The audit verified:

* dataset structure;
* row and case counts;
* valid decision values;
* valid update types;
* complete E0–E3 structure;
* exactly one `INITIAL` per case;
* exactly one `REQUIRED_REVERSAL` per case;
* exactly one expected decision change;
* consistency between trajectory and `update_type`;
* reversal-stage distribution;
* evidence completeness;
* duplicate observations;
* reversal-direction diversity.

Result:

```text
DATASET INTEGRITY AUDIT: PASSED
```

---

## 4. Model Configuration

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

The model receives cumulative evidence up to the current stage.

The inference prompt explicitly instructs the model to:

* use only the available evidence;
* reconsider the previous diagnosis when new evidence appears;
* update when evidence warrants an update;
* avoid changing the diagnosis merely because another possibility exists;
* use `UNCERTAIN` when the available evidence is insufficient;
* return a structured decision and short rationale.

---

## 5. Validation Metrics

### Initial Decision Accuracy

Percentage of cases where the model's E0 decision matches the expected initial decision.

```text
Initial Decision Accuracy = 87.5%
```

Result:

```text
35 / 40 correct
```

---

### Final Decision Accuracy

Percentage of cases where the model's E3 decision matches the expected final decision.

```text
Final Decision Accuracy = 100.0%
```

Result:

```text
40 / 40 correct
```

---

### Required Reversal Accuracy

Percentage of cases where the model has adopted the expected new decision at the exact stage where the reversal is required.

```text
Required Reversal Accuracy = 100.0%
```

Result:

```text
40 / 40 correct
```

This metric is important because final correctness alone cannot determine whether the model updated at the correct point in the evidence sequence.

---

### Fully Correct Decision Trajectory

A trajectory is considered fully correct only if the model's decision matches the expected decision at **all four stages**.

```text
Fully Correct Trajectory = 60.0%
```

Result:

```text
24 / 40 cases
```

This is substantially lower than final decision accuracy.

The difference is one of the central findings of V1.

---

## 6. Main Result

The model achieved:

| Metric                            |     Result |
| --------------------------------- | ---------: |
| Initial Decision Accuracy         |  **87.5%** |
| Final Decision Accuracy           | **100.0%** |
| Required Reversal Accuracy        | **100.0%** |
| Fully Correct Decision Trajectory |  **60.0%** |

The results show that the model reliably reached the expected final decision and responded correctly at the required reversal stage.

However, only 60% of cases followed the expected trajectory at every intermediate stage.

---

## 7. Error Taxonomy

The observed errors are more informative than the final accuracy alone.

### 7.1 Premature Reversal

The model changes its decision before the evidence warrants a reversal.

Example:

```text
CASE_003

Expected:
APPLICATION → APPLICATION → CONFIGURATION → CONFIGURATION

Model:
APPLICATION → CONFIGURATION → CONFIGURATION → CONFIGURATION
```

At E1 the model interprets environmental differences as evidence of a configuration problem.

The decisive evidence identifying an unsupported feature flag appears only at E2.

This is a classic premature reversal.

---

### 7.2 Initial Error

The model starts with an incorrect diagnosis and subsequently recovers.

Example:

```text
CASE_007

Expected:
APPLICATION → APPLICATION → NETWORK → NETWORK

Model:
NETWORK → APPLICATION → NETWORK → NETWORK
```

The model begins with the wrong hypothesis but corrects it at E1 and subsequently performs the required reversal at E2.

This is different from premature reversal because the model was already wrong before the intermediate transition.

---

### 7.3 Persistent Intermediate Error

In several cases the model reaches the correct final decision but temporarily adopts an incorrect intermediate hypothesis.

Example:

```text
CASE_018

Expected:
CONFIGURATION → DATABASE → DATABASE → DATABASE

Model:
CONFIGURATION → CONFIGURATION → DATABASE → DATABASE
```

The model fails to perform the expected update at E1 but reaches the correct state by E2.

---

### 7.4 Uncertainty Drift

Some cases demonstrate movement through `UNCERTAIN` or another unsupported intermediate hypothesis before the decisive evidence appears.

Example:

```text
CASE_039

Expected:
APPLICATION → APPLICATION → APPLICATION → DATABASE

Model:
UNCERTAIN → CONFIGURATION → UNCERTAIN → DATABASE
```

The final decision is correct, but the intermediate trajectory is substantially different from the expected one.

This illustrates why a final-answer metric alone is insufficient for sequential decision validation.

---

## 8. Timing Effect

The reversal stage appears to matter for trajectory stability.

The test deliberately included:

```text
E1 reversal: 10 cases
E2 reversal: 20 cases
E3 reversal: 10 cases
```

The model was able to identify the required final reversal even when it occurred late in the sequence.

However, later reversals create more opportunity for intermediate deviations before the decisive evidence arrives.

This is particularly visible in the E3 cases, where several models reached the correct E3 decision after incorrect E1/E2 states.

---

## 9. Important Validation Finding

The most important result of V1 is the gap between:

```text
Final Decision Accuracy
        100%
```

and:

```text
Fully Correct Decision Trajectory
         60%
```

This demonstrates that:

> **A model can produce the correct final decision while following an incorrect or unstable decision trajectory.**

Therefore, evaluating only the final answer would miss a substantial part of the model's sequential decision behavior.

This is the primary validation signal identified by V1.

---

## 10. Interpretation

V1 does not establish that the model is generally unreliable.

The experiment demonstrates something narrower:

* the model responds effectively to decisive evidence;
* the model reaches the expected final decision in all 40 cases;
* intermediate decisions are considerably less stable;
* premature or unsupported hypothesis changes can occur before decisive evidence arrives;
* final correctness therefore does not fully characterize sequential decision behavior.

The distinction between **outcome correctness** and **trajectory correctness** is therefore important for LLM-based decision systems.

---

## 11. Limitations

V1 is intentionally a compact validation experiment.

Important limitations include:

1. The dataset is synthetic.
2. The number of cases is limited to 40.
3. The root-cause domain is software incident diagnosis.
4. Each case contains exactly one expected reversal.
5. The expected trajectories are deterministic.
6. Only one model and one provider configuration were tested.
7. Temperature was fixed at zero.
8. The validation does not establish whether the model's internal reasoning is causally correct.
9. The expected trajectory represents the validation reference and does not prove that a human expert would always make exactly the same intermediate decision.

The results should therefore be interpreted as **evidence from a controlled validation scenario**, not as a general performance claim about LLMs.

---

## 12. Conclusion

V1 successfully demonstrated a measurable validation dimension for sequential LLM decision-making.

The model achieved:

```text
87.5%  Initial Decision Accuracy
100.0% Final Decision Accuracy
100.0% Required Reversal Accuracy
60.0%  Fully Correct Decision Trajectory
```

The main finding is the discrepancy between final correctness and trajectory correctness.

The model can arrive at the correct conclusion while making intermediate decisions that do not follow the expected evidence-driven trajectory.

This makes **decision trajectory stability** a potentially useful validation dimension for systems in which decisions are updated as new evidence becomes available.

V1 therefore provides a compact empirical basis for further investigation of **evidence-driven decision updating and decision reversal in LLMs**.
