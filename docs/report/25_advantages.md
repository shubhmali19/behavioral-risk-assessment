# 25. Advantages

The advantages below are claimed only where the implementation supports them. Where a stated design goal was not achieved, it appears in Section 26 instead of here.

## 25.1 Evaluation Against a Derived Ceiling

The system's evaluation does not compare accuracy against perfect classification. Because the label's generating function is documented, the Bayes-optimal accuracy can be computed exactly: 0.6104. The tuned Random Forest attains 0.6039, which is 98.9% of that limit and 95.9% of the accuracy available above the majority-class baseline of 0.4500.

This reframes a figure that looks weak in isolation. It also supplies a falsifiable claim: had the model scored materially above 0.6104, that would have been evidence of leakage rather than skill, and the report would have had to explain it.

Two independent checks confirm the model has converged on the Bayes decision rule rather than coincidentally matching its accuracy. Its predicted class distribution (31.4 / 56.2 / 12.5) tracks the Bayes rule's (32.9 / 54.4 / 12.7) rather than the true distribution (35 / 45 / 20), reproducing the characteristic retreat toward the central class near a noisy threshold. And 1,706 of its 1,743 errors fall between adjacent bands; only 37 records, 0.84% of the test set, confuse *Low* with *High*.

## 25.2 Training and Serving Provably Agree

Feature engineering is defined once. `preprocess.py` writes every constant it fits — ordinal maps, IQR clip bounds, min–max normalisation ranges, imputation medians — to `preprocessing_params.json`, and `inference.py` reads that artefact rather than restating the values. No encoding constant is hardcoded in the serving path.

The equivalence is verified, not assumed. Three hundred randomly drawn training records routed through the serving preprocessor produce feature vectors agreeing with the training pipeline's to within 10⁻¹⁶ across all thirteen derived and encoded columns. Held-out records routed through the full serving path produce predictions identical to feeding the model its training-format features directly, on every row.

The accuracy reported in Section 23 is therefore the accuracy a live user receives. Section 22.4 documents that this was not true before the repair, and that no metric in the report would have revealed it.

## 25.3 Interactions Without Loss of Per-Answer Attribution

A rubric is a sum of independent terms and cannot represent that a thin emergency fund matters more for a sole earner with dependants. A tree ensemble represents such conditionals natively [9], [13].

Historically this capability cost the per-answer transparency that made rubrics defensible. Exact Shapley values for tree models are computable in polynomial time [7], so attribution can be recovered inside a single HTTP request over a 200-tree ensemble, without sampling. The mechanism that restores the rubric's chief virtue is present and correct at the point of computation — though Section 21.4 records that the serving code then discards part of what it computed.

## 25.4 Uncertainty Is Reported, Not Hidden

The classifier returns a probability across all three bands rather than a bare label, and the interface displays the probability of the predicted class. Where the model is unsure, the user is told.

This is more than presentational. Macro ROC AUC (0.7712) exceeds weighted ROC AUC (0.7461), which means the model *ranks* high-risk individuals well even though the argmax rule selects that class for fewer than half of them. The information needed for a more conservative operating point already exists in the payload the API returns; Section 24.2 explains how to use it.

## 25.5 Assessments Are Reproducible and Auditable

Every persisted assessment stores the twenty-six submitted inputs, the predicted band, the full probability vector, the three derived scores and the SHAP attributions. Any past prediction can be reconstructed and examined. Because inference is deterministic given its inputs — the noise term exists only in the data generator, not in the model — re-running a stored record reproduces its original result exactly.

The database records what the user asserted rather than what the system derived. Section 17.4 defends the resulting third-normal-form violation on precisely this ground: `savings_rate` need not equal the value implied by the income and expenses the user also reported, and an audit trail should preserve the discrepancy rather than normalise it away.

## 25.6 Modularity

The five stages — generation, preprocessing, training, serving, presentation — communicate through files and HTTP rather than through shared memory, so each can be inspected and re-run independently. Re-running `preprocess.py` after the parameter-persistence change left `processed_dataset.csv` byte-identical, which is why the trained model remained valid and no retraining was needed to repair the serving defects.

The frontend holds no thresholds, no scoring weights and no model. A model change requires no frontend release. The API contract is a checked-in artefact against which both the backend schemas and the frontend types are validated, and Section 18.1 records the six interface divergences that existed before that discipline was adopted.

## 25.7 Deployment

Three containers compose: PostgreSQL with a health check, the FastAPI service gated on that health check, and an nginx-served static bundle. SQLite is supported for development through the same ORM, with the one non-portable query — date truncation in the analytics aggregate — resolved by inspecting the active dialect rather than assuming a backend.

## 25.8 The Report Is Falsifiable

Six defects are documented in the sections that describe the components containing them, rather than collected in a footnote or omitted. Two objectives are marked not met. A secondary model is reported as failing, with a derivation showing that no model could have succeeded. Every numeric claim in this report was recomputed from the artefacts in the repository during writing, and three figures the author had previously asserted — the Bayes ceiling, the frontend bundle size, and the count of recommendation branches — were found wrong and corrected.

This is stated as an advantage because the alternative was available and was not taken. A report claiming a working explainability module, a functioning investment recommender and a clean end-to-end system would have been shorter, and would have been false.
