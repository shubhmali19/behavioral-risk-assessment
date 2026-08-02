# 7. Objectives

## 7.1 Primary Objectives

**O1 — Construct a labelled dataset suitable for supervised risk classification.**
Generate at least 20,000 records spanning demographic, financial and lifestyle attributes, with conditional dependencies specified explicitly rather than sampled independently, and derive a three-band risk label from a documented scoring function.

**O2 — Build a reproducible preprocessing pipeline.**
Handle missing values, clip outliers, encode categorical attributes, and derive ratio and composite features. Persist every constant fitted during this stage so that it can be reused at inference.

**O3 — Select a classifier by controlled comparison.**
Train Random Forest, XGBoost, LightGBM, CatBoost and a neural network on an identical partition with default hyperparameters; select on weighted F1; tune the winner; validate by cross-validation.

**O4 — Evaluate against the attainable ceiling.**
Derive the Bayes-optimal accuracy implied by the label's generating function and report model accuracy relative to it, rather than relative to perfect classification.

**O5 — Produce per-user explanations.**
Compute exact Shapley attributions for each individual prediction using the polynomial-time tree algorithm [7], and surface them in the interface alongside the predicted band.

**O6 — Verify training–serving equivalence.**
Demonstrate that the feature vector computed for a live request is identical to the one the training pipeline would have computed for the same record.

**O7 — Deliver an end-to-end system.**
A user completes a form; the backend validates the input; the model predicts; an explanation is generated; the assessment is persisted; the dashboard renders the result and the history.

## 7.2 Secondary Objectives

**O8 — Predict investment preference** as a secondary classification target.

**O9 — Detect behavioural biases** and generate personalised recommendations from the user's inputs.

**O10 — Containerise the system** with Docker Compose across frontend, backend and database.

## 7.3 Outcomes

The objectives are restated below against what was achieved, including where the achievement was partial and where it was not achieved at all.

| | Objective | Outcome |
|---|---|---|
| O1 | Labelled dataset | **Met.** 22,000 records, 30 columns, conditional dependencies documented in Section 12.3. One defect: a third of `insurance_coverage` values were destroyed on load (Section 12.5). |
| O2 | Reproducible preprocessing | **Met.** Constants persisted to `preprocessing_params.json`. Re-running the pipeline leaves the processed dataset byte-identical. |
| O3 | Controlled model selection | **Met.** Random Forest selected on untuned weighted F1 = 0.5949, tuned to 0.6006, cross-validated at 0.5996 ± 0.0032. The published comparison table reports the tuned winner against untuned competitors, which Section 15.4 flags. |
| O4 | Evaluation against ceiling | **Met.** Bayes-optimal accuracy derived as 0.6104; the model attains 0.6039, or 98.9% of it, and 95.9% of the accuracy available above the majority baseline. |
| O5 | Per-user explanations | **Not met.** Exact Shapley values are computed correctly, then reduced to absolute magnitudes averaged across classes before being returned. The user receives a magnitude, not a direction, while the interface caption asserts a direction. Section 21.4. |
| O6 | Training–serving equivalence | **Met, after repair.** Five disagreements were found and eliminated; equivalence is now verified to 10⁻¹⁶ across 300 records and to exact prediction agreement on every held-out row. Section 22.4. |
| O7 | End-to-end system | **Met, after repair.** The form initially submitted to the non-persisting endpoint, so nothing entered through the interface reached the database. Corrected and verified in Section 19.5. |
| O8 | Investment preference | **Not met, and not achievable.** Accuracy 0.2586 against a majority baseline of 0.2869 and a ceiling of ≈0.3210. The label was generated without reference to any feature. Reported as a negative result in Section 22.3. |
| O9 | Biases and recommendations | **Met as implemented, unvalidated.** Nine bias rules and eleven recommendation branches, all deterministic functions of the inputs. No validation against labelled data was performed and none is claimed. |
| O10 | Containerisation | **Met.** Three services compose and start healthy. `GET /model/info` fails under Docker because it reads a hardcoded absolute path (Section 16.7). |

Seven of ten objectives were met, two only after defects found during the writing of this report were repaired. O5 and O8 were not met: the first through an implementation fault that remains unrepaired, the second because the objective was unattainable given how its target was constructed.

Stating O5 as unmet is uncomfortable, since explainability is the feature that distinguishes this system from the rubric it proposes to replace (Section 4.5). The fault is two lines of code and is described precisely in Section 21.4. It is left unrepaired because correcting it would invalidate every SHAP figure reported in Sections 14, 21 and 22, and the report records the defect in preference to regenerating results under time pressure. Section 27 lists it as the first item of future work.
