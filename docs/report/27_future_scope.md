# 27. Future Scope

The items below are ordered by the ratio of value delivered to effort required, not by ambition. The first four are corrections to defects this report documents, and none takes more than an afternoon.

## 27.1 Immediate Corrections

**Restore the sign of the SHAP attributions.** Two lines in `_get_shap_values`. Instead of averaging absolute values across classes, select the column of the predicted class and preserve its sign:

```python
k = int(model.predict(X_df)[0])
sv_row = sv[0][:, k]
```

The interface is already written to render negative values in red. This is the first thing that should be done, because it is the difference between an explainability module and a bar chart of magnitudes, and because the current caption misinforms. Every SHAP figure in Sections 14, 21 and 22 must then be regenerated.

**Promote the equivalence check to a regression test.** The comparison described in Section 9.7 — routing training records through the serving preprocessor and asserting the feature vectors match — runs in under a minute and would have caught five of this project's six defects on the day they were introduced. It belongs in `tests/`, running in continuous integration, and it is the single highest-value change available to this codebase.

**Remove `expense_ratio`.** It is the exact complement of `savings_ratio` (correlation −1.000000) and contributes nothing but a split of the SHAP attribution across two identical rows. Removing it leaves accuracy unchanged and makes the explanation honest.

**Fix the two backend path defects.** `GET /model/info` should resolve its metadata path relative to `ML_PATH` rather than to an absolute location on the author's machine. The local-development fallback in `ml_service` should ascend three directory levels rather than four.

## 27.2 Making the Model Fit Its Purpose

**Threshold on `P(High)` instead of taking the argmax.** Macro AUC (0.7712) exceeds weighted AUC (0.7461), which establishes that the model ranks high-risk individuals well even though the argmax rule selects that class for fewer than half of them. Recall on *High* is 0.4295 against precision 0.6898. Choosing a threshold to hit a target recall — say 0.75 — would trade precision the application can afford for recall it cannot. The probability vector is already in the API response; only the decision rule needs changing.

**Assess calibration.** The interface displays a confidence figure. Whether a stated 0.7 corresponds to being right 70% of the time is unmeasured. A reliability diagram over the test partition, and Platt scaling or isotonic regression if the model proves miscalibrated, would make the displayed number mean what it appears to mean.

**Fit a logistic-regression baseline.** The generating function is a weighted sum, so a linear model may perform comparably to the ensemble. Without that comparison the report cannot claim the non-linear models earned their complexity, and Section 26.10 concedes as much. The baseline may well win, and that would be a finding.

## 27.3 Repairing the Data

**Preserve the `None` insurance category.** Read the CSV with `keep_default_na=False` and restore the three-level ordinal map. Accuracy shifts by less than one cross-validation standard deviation, but `behavioral_composite_score` becomes correct for the third of records currently misattributed, and the live API stops mapping a user who reports no insurance onto the training median.

**Rewrite the `investment_preference` generator.** As Section 22.3 establishes, the label is currently sampled from a distribution conditioned on `risk_category` alone, giving it a Bayes ceiling of 0.3675 and making the secondary model unsalvageable. Making the draw depend on age, investment experience, luxury spending and risk band would give the target learnable structure. Every downstream number changes, so this belongs in a new iteration rather than a patch.

**Reconsider the IQR clip on `credit_score`.** The rule truncates at 660.5, discarding variation among poor-credit individuals precisely where the feature discriminates. This is why a variable carrying weight +25 in the generating function ranks eighth in SHAP. A wider bound, or clipping only the upper tail, would recover it.

**Widen the label's signal-to-noise ratio, or say why not.** The noise term at σ = 8.0 against a signal at σ = 7.64 caps achievable accuracy at 0.6104. This was almost certainly not deliberate. A generator with less noise would produce a more discriminative model, at the cost of a less interesting Bayes-ceiling analysis.

## 27.4 Toward Real Data

The largest limitation, and the hardest to address. Sections 5.2 and 26.1 argue that no ground truth for risk-band suitability exists even in principle, because no institution records years afterward whether an assigned band was correct.

Two tractable directions exist. A **small validation study** — 100 to 200 respondents completing both the form and the validated Grable–Lytton instrument [3] — would not provide a training label, but would show whether the system's bands correlate with an instrument the literature accepts. That is a modest, checkable claim, and it requires ethics approval and time rather than novel methodology.

A **proxy-label study** would substitute an observable outcome for the unobservable one: portfolio volatility actually held, or realised drawdown tolerance during a market decline. This changes the research question from *what band suits this person* to *what behaviour does this person exhibit*, which is answerable. It is the direction in which this work would have to move to make any empirical claim at all.

Until one of these is done, the behavioural-economics premise stated in Section 13.6 — that lifestyle spending reveals dispositions self-report conceals — remains untested, because the synthetic label was constructed without reference to any lifestyle attribute.

## 27.5 Engineering the System

**Authentication and authorisation.** No principal exists, the `users` table is never written, and `GET /assessments` returns every stored financial disclosure to any caller. Session-based authentication would populate the vestigial table and permit the history and analytics endpoints to be scoped to their owner.

**Audit-log policy.** The middleware persists complete request bodies to an unprotected table and does so with a synchronous commit inside an asynchronous handler. The write should move to a background task, and the body should be redacted or omitted.

**Schema migrations.** `backend/alembic/` is empty and the schema is materialised by `metadata.create_all()`, which silently ignores drifted column definitions. Generating an initial revision is a prerequisite to any change against a database holding data.

**Indexes.** No secondary index exists. The history listing orders `assessments` by `created_at`, and the analytics aggregations group `predictions` by `risk_category` and `investment_preference`. Those three columns are where load will first show.

**Reuse the `TreeExplainer`.** It is constructed per request against a 200-tree ensemble. Building it once at startup would remove the dominant cost of a prediction. No latency benchmark exists to quantify the gain, and establishing one is a precondition for claiming it.

**Code-split the frontend.** The bundle is 922.99 kB, 279.68 kB gzipped, dominated by Recharts and its D3 dependencies. Deferring the analytics and results routes behind `React.lazy` would bring the initial chunk under Vite's 500 kB threshold.

## 27.6 Beyond the Present Design

Interaction effects are computable for tree models at the same polynomial cost as the attributions themselves [7], and the interface presents none. Showing that a low emergency fund matters more for a user with dependants would demonstrate the capability that justifies replacing an additive rubric — the capability Section 25.3 claims and Section 5.2 concedes the synthetic label barely exercises.

Counterfactual explanation — *if your savings rate were 22% rather than 12%, your band would change* — is a more useful artefact for an individual than an attribution, and is what a user actually wants from a risk assessment.

And the incumbent deserves a fair test. Rudin's position is that a high-stakes decision should use an inherently interpretable model rather than an explained black box [15]. A scored rubric fitted to this data, rather than asserted, would be interpretable by construction and might lose very little accuracy against a label that is a weighted sum. Section 4.5 concedes that on transparency the rubric currently leads. Benchmarking against it would settle whether anything was gained.
