# 30. IEEE-Format Research Paper

> **Formatting note.** The text below is written to the IEEE conference template (two-column, 10 pt Times New Roman, `\documentclass[conference]{IEEEtran}`). Section numbering restarts here and is independent of the main report. Figure and table callouts are marked; sources for each are given in the note at the end.

---

# Evaluating a Behavioural Risk-Assessment System Against Its Bayes Ceiling: Explainability, Serving Skew, and a Negative Result

**Chirag Mali**
*Department of Computer Engineering*
[Institution]
[City, India]
[email]

---

## Abstract

Retail financial risk profiling remains dominated by questionnaires scored against fixed rubrics whose weights encode assumption rather than evidence and which, being additive, cannot represent interactions among a respondent's attributes. We replace the rubric with a tree-ensemble classifier and attempt to preserve per-answer transparency using Shapley attribution, then audit the resulting system end to end. On 22,000 synthetic records with twenty-six demographic, financial and lifestyle attributes, a tuned Random Forest attains accuracy 0.6039 and weighted F1 0.6006. Because the label is a threshold on a linear score perturbed by Gaussian noise of known scale, we derive the Bayes-optimal accuracy exactly: 0.6104. The model therefore reaches 98.9% of the attainable ceiling and 95.9% of the accuracy available above the majority-class baseline, and its predicted class distribution tracks the Bayes rule rather than the empirical one. We report a secondary model as a negative result: its target was generated conditioned on the risk band alone, bounding any classifier at 0.3675, and it scores 0.2586 against a 0.2869 baseline. Finally we characterise a class of defect invisible to model evaluation. Feature engineering implemented separately for training and for serving diverged in five places; every reported metric stayed correct while every live prediction was wrong, and all unit tests passed. We argue that verifying training–serving feature equivalence, and auditing the explanation pipeline rather than only the explanation method, belong in the standard evaluation apparatus.

**Index Terms** — behavioural finance, explainable AI, SHAP, Bayes-optimal accuracy, training–serving skew, negative results, synthetic data.

---

## I. Introduction

Classical finance models the investor as an expected-utility maximiser. Kahneman and Tversky showed the description fails systematically: outcomes are evaluated as gains and losses against a reference point, losses weigh roughly twice as heavily as equivalent gains, and small probabilities are distorted [1]. Barberis and Thaler survey the consequences for market and individual behaviour [2].

Institutions nonetheless place clients on a risk spectrum using questionnaires scored by fixed rubrics; Grable and Lytton's thirteen-item scale is the canonical validated instance [3]. Two weaknesses are structural. The weights are asserted rather than estimated, so where an analyst's beliefs are wrong the instrument is wrong identically for every respondent. And an additive score cannot express interaction — that a thin emergency fund is more dangerous for a sole earner with dependants. Klement's survey adds a third: deployed instruments routinely conflate risk *capacity*, a balance-sheet fact, with risk *tolerance*, a psychological disposition [4].

Supervised learning addresses the first two. It is long established in credit scoring, where Lessmann *et al.* find tree ensembles consistently strongest [5]. It has not migrated to risk profiling, and the obstacle is not technical: a credit model predicts default, which is observed, whereas a risk band predicts suitability, which no institution ever labels.

A learned model also forfeits the rubric's transparency. Lundberg and Lee unified additive attribution methods under the Shapley value [6]; an exact polynomial-time algorithm for tree ensembles [7] makes per-request attribution cheap. Rudin objects that a post-hoc explanation is not the computation it describes and may mislead while appearing authoritative [15].

This paper contributes three results, none of which required a new algorithm.

1. **Evaluation against a derived ceiling.** Where a label's generating process is known, the Bayes-optimal accuracy is computable. We derive it (0.6104) and report the model's 0.6039 relative to it, rather than to unity.
2. **A negative result, diagnosed at the source.** A secondary classifier fails below its own majority baseline. Reading the generator — not further tuning — shows why no classifier could succeed.
3. **A defect class invisible to model evaluation.** Training and serving computed features differently in five places while all metrics and all tests remained green.

---

## II. Related Work

**Behavioural foundations.** Prospect theory establishes reference dependence and loss aversion [1]; the survey literature catalogues overconfidence, herding and present bias as population regularities [2]. These are established by experiment, not as attributes inferable from a spending profile.

**Measurement.** Grable and Lytton validate an instrument psychometrically [3]. Klement documents the capacity/tolerance conflation as endemic [4].

**Estimators.** Breiman's Random Forest bounds generalisation error via tree strength and inter-tree correlation [9]. Gradient boosting refines this: XGBoost with a regularised objective and sparsity-aware splits [10], LightGBM with one-side sampling and histogram binning [11], CatBoost with ordered boosting against target leakage [12]. Grinsztajn *et al.* find tree ensembles still ahead of neural networks on tabular data, attributing the gap to robustness against uninformative features and a bias toward axis-aligned boundaries [13].

**Explanation.** LIME fits a local interpretable surrogate [14]. Lundberg and Lee show LIME and others are special cases of additive attribution, within which the Shapley value uniquely satisfies local accuracy, missingness and consistency [6]. `TreeExplainer` computes it exactly in polynomial time for trees [7]. Rudin argues against post-hoc explanation for high-stakes decisions [15].

**Systems.** Sculley *et al.* frame production ML maintenance as technical debt, observing that most of a deployed system is not the learning algorithm [8]. The evaluation literature measures models; the debt accrues elsewhere.

---

## III. Data and Method

### A. Dataset

No public dataset joins twenty-six demographic, financial and lifestyle attributes to a behavioural risk label, and Section VII argues no such label exists in principle. We therefore generate 22,000 records under a fixed seed with explicit conditional dependencies: income conditioned on occupation and education, expenses on income and dependants, credit score on debt burden and savings, and so forth.

The risk label is a threshold on a continuous score,

> `risk_score = −30·s + 25·(1 − c/900) + 20·min(d,5)/5 − 15·(e/20) + 10·[f < 3] + ε`

with `s` savings rate, `c` credit score, `d` debt-to-income, `e` investment experience, `f` emergency-fund months, and `ε ~ N(0, 8)`. Cuts at the 35th and 80th percentiles give classes at 35 / 45 / 20.

**The noise dominates.** The deterministic component has standard deviation 7.642 against a noise standard deviation of 8.000 — a signal-to-noise variance ratio of 0.912.

### B. Preprocessing

Missing values imputed; nine numeric columns clipped at 1.5 × IQR; five ordinal and six nominal columns encoded; seven features derived (three ratios, two composites, two others), yielding 48 model features from 61 columns. Every constant fitted here — ordinal maps, clip bounds, min–max ranges, medians — is persisted to a JSON artefact consumed at serving time, for reasons Section VI-C makes clear.

### C. Model Selection

Stratified 80/20 split under a fixed seed. Five classifiers trained with library defaults on the identical partition and compared on weighted F1, chosen over accuracy because a constant predictor achieves 0.45. The Random Forest led at F1 = 0.5949 and alone received a randomised hyperparameter search (20 candidates, 3-fold CV), reaching 0.6006.

*(Table I — model comparison.)*

### D. Explanation

Exact Shapley values via `TreeExplainer` [7]: globally by averaging absolute values across the test partition, locally per request for the submitted row.

---

## IV. System

A React/TypeScript client elicits the twenty-six attributes through a four-step form and holds no business logic. A FastAPI service validates against Pydantic schemas whose categorical fields are constrained to the exact training vocabulary, calls the inference module in-process (avoiding a cross-language serialisation boundary), persists inputs, prediction and attributions to PostgreSQL, and returns a probability vector. Three containers compose. Seven endpoints are documented by the same schemas that enforce them.

*(Fig. 1 — three-tier architecture and data flow.)*

---

## V. Results

### A. Classification Performance

Accuracy 0.6039, weighted F1 0.6006, one-vs-rest weighted ROC AUC 0.7461 on 4,400 held-out records. Five-fold CV F1 = 0.5996 ± 0.0032.

*(Table II — per-class precision, recall, F1.)*

Per class, *High* carries the highest precision (0.6898) and the lowest recall (0.4295).

### B. The Bayes Ceiling

Every quantity entering `risk_score` is available as a feature, so the deterministic component is exactly recoverable; `ε` is not. For a record with signal `s`, class probabilities follow from the noise CDF, and the Bayes-optimal rule takes their argmax. Recovering the thresholds numerically (`t₁ = −11.074`, `t₂ = 2.598`) so that induced proportions match the observed 35/45/20 and averaging the success probability over all records gives:

| Reference | Accuracy |
|---|---|
| Majority class | 0.4500 |
| **Random Forest** | **0.6039** |
| **Bayes ceiling** | **0.6104** |

The model attains **98.9%** of the ceiling and **95.9%** of the accuracy available above the baseline:
`(0.6039 − 0.4500)/(0.6104 − 0.4500) = 0.9595`.

Two checks indicate convergence on the Bayes *rule*, not merely on its accuracy. Near a noisy threshold the optimal rule retreats toward the central class, and the model reproduces this:

| Class | True | Bayes | Model |
|---|---|---|---|
| Low | 35.0% | 32.9% | 31.4% |
| Medium | 45.0% | 54.4% | 56.2% |
| High | 20.0% | 12.7% | 12.5% |

And errors respect ordinal structure: 1,706 of 1,743 errors are between adjacent bands; only 37 records (0.84%) confuse *Low* with *High*.

*(Fig. 2 — accuracy against reference points. Fig. 3 — confusion matrix.)*

### C. A Negative Result

A secondary Random Forest predicting investment preference across five classes scores accuracy 0.2586, weighted F1 0.1892, ROC AUC 0.4949 — below the 0.2869 majority baseline and at chance in ranking.

The generator draws this label from one of three fixed probability vectors selected by `risk_category` alone; no feature enters. Hence

> `ceiling | true band = Σₖ P(band = k)·max(pₖ) = 0.3675`,

and ≈ 0.3210 given the 60.4%-accurate band the system can infer. No algorithm, tuning budget or additional feature could have succeeded. The diagnosis required reading the data generator, not running experiments.

### D. Training–Serving Skew

Feature engineering existed in two implementations. They disagreed on: the scale of `savings_rate` (fraction vs. percentage); the denominator of `debt_to_income_ratio` (annual vs. monthly income); the direction of `age_income_ratio`; the spelling and cardinality of four ordinal maps; and the formulae of both composite scores.

The held-out set was evaluated through the training path. **Every reported metric was correct. Every live prediction was wrong.** Predicted risk was not monotone in the savings rate: a user reporting 10% was assessed *Medium* where the training scale placed them at *High*.

The repair eliminated the duplication rather than fixing five instances: the training pipeline emits its fitted constants and the serving path reads them. Equivalence was then verified — 300 records agree across all thirteen derived features to 10⁻¹⁶, and predictions agree with the training-format path on every held-out row.

### E. Explanation Pipeline Failure

`TreeExplainer` returns signed, class-specific values. The serving code reduced them by `np.abs(sv[0]).mean(axis=1)` — absolute value, then averaged across classes. Across 120 attributions from twelve inputs, none was negative. The interface nonetheless captioned its chart *"Blue = increases risk, Red = decreases risk"*; no bar can ever be red.

Separately, `savings_ratio` and `expense_ratio` are exact complements (r = −1.000000), and `savings_rate` a noisy third copy (r = 0.944), so one quantity occupies four of the five top-ranked features and its importance is split among them.

The attribution *method* was sound. The *pipeline* was not, and nothing detected the difference — precisely the failure mode Rudin anticipates [15].

---

## VI. Discussion

**A. Sixty percent is not weak.** Against unity it looks poor; against 0.6104 it is near-optimal. Reporting `A/A*` rather than `A` is available whenever a generating process is known, and is the discipline this paper presses.

**B. Optimal accuracy, wrong objective.** *High* recall of 0.4295 is the Bayes-optimal response to threshold noise — and the wrong operating point for a screening instrument, where under-warning is costlier than over-caution. Macro AUC (0.7712) exceeding weighted AUC (0.7461) shows the ranking information is present; thresholding `P(High)` below 0.5 would recover recall. A model can sit at its Bayes limit and still be misconfigured for its task.

**C. Metrics do not see what breaks.** Five of six defects lay not inside any function but in the *agreement between two representations of one computation* — two feature implementations, two spellings of a category, two endpoints of identical shape, a colour legend and the values it coloured. All eleven tests passed. Unit tests examine one representation. What found these was comparing representations: routing training rows through the serving preprocessor, reading the CSV as text rather than through `pandas`, asking whether any returned attribution was ever negative. This is the debt Sculley *et al.* describe [8], and we propose that a training–serving equivalence assertion belongs in the standard suite. Ours runs in under a minute and would have caught five of the six.

---

## VII. Limitations

The data is synthetic, and this forfeits every empirical claim. Recovered correlations are those the generator was written to contain. The project's own premise — that lifestyle spending reveals dispositions self-report conceals — is untestable here, because no lifestyle attribute enters `risk_score`; that none reaches the top ten SHAP ranks is a fact about the generator. The Bayes-ceiling analysis, our strongest contribution, exists only because the data is synthetic: the contribution and the limitation are one fact viewed twice.

No ground truth for risk-band suitability exists even in principle, since no institution records whether an assigned band was later correct. The explanation defect of Section V-E is unrepaired, as correcting it invalidates the reported SHAP figures. No logistic baseline was fitted, so we cannot claim the non-linear model earned its complexity against a label that is a weighted sum. No calibration assessment and no latency benchmark were performed. The system has no authentication and is not deployable against real financial disclosures.

---

## VIII. Conclusion

We built and audited an end-to-end behavioural risk-assessment system. The classifier reaches 98.9% of the Bayes-optimal accuracy its data permits, having converged on the Bayes decision rule rather than merely its accuracy. A secondary model is reported as a negative result, with a derivation showing its target carried no learnable structure. Most instructively, five defects that rendered every live prediction wrong left every reported metric correct and every test passing, because they lived in the agreement between two implementations rather than within either.

We conclude that a held-out test set drawn from the training pipeline certifies the estimator and says nothing about the code that will serve it; that an explanation pipeline requires auditing separately from the explanation method it invokes; and that accuracy is uninterpretable without the ceiling against which it is read.

---

## References

*Use the fifteen entries of Section 29, unchanged and in the same order. Citation numbers in this paper correspond exactly.*

---

## Preparation Note

**Figures.** Fig. 1 renders from the Mermaid source in Section 11. Fig. 2 is specified as Figure 23.3. Fig. 3 as Figure 22.1. A fourth figure — `P(High)` versus submitted `savings_rate`, before and after the skew repair (Figure 22.3) — is the most persuasive single artefact and should be included if space permits.

**Tables.** Table I from Section 15.4, annotating that the Random Forest row is the tuned model and the others are untuned. Table II from Section 23.2.

**Length.** As drafted this runs to roughly six pages in the IEEE conference template. Sections II and IV compress most readily; Sections V-B, V-C and V-D should not be cut, as they carry the contributions.

**Before submission.** Confirm the pagination gaps flagged in Section 29.1, resolve the page-range discrepancy in [1], and delete Section 29.1 itself.
