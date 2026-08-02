# 26. Limitations

## 26.1 The Data Is Synthetic

This is the limitation from which most others follow, and it cannot be mitigated within the present design.

No person supplied a record. The 22,000 rows were produced by a generator whose conditional dependencies were written by the author. Every correlation the analysis recovers is a correlation the generator was written to contain. When Section 12.3 reports *r* = +0.711 between savings rate and financial decision score, that is not a finding about savers; it is a restatement of a formula. When Section 21.5 observes that every feature entering `risk_score` appears among the top eight SHAP ranks, it confirms that a Random Forest can recover a weighted sum — which was not in doubt.

Three consequences deserve separate statement.

**The reported accuracy does not transfer.** A real population's risk band would depend on attributes not collected, would carry measurement error in the self-reports, and would exhibit relationships no generator anticipated. The 60.4% figure describes recovery of a known function, in neither direction a prediction about people.

**The project's own premise is untestable on its own data.** The system was built on the reasoning, set out in Section 13.6, that discretionary spending reveals risk dispositions that direct questioning does not. But `risk_score` is a function of five financial quantities and no lifestyle attribute enters it. That no lifestyle feature reaches the top ten SHAP ranks is therefore a property of the generator, not a result about behaviour. The behavioural-economics motivation of this project is, on this data, unfalsifiable.

**The Bayes-ceiling analysis is purchased with the same coin.** Deriving an attainable ceiling requires knowing the generating function, which is possible only because the data was constructed. The analysis that Section 25.1 claims as the report's strongest contribution is available precisely because the data is weakest.

## 26.2 The Explainability Module Does Not Deliver What It Claims

This is the most serious defect in the system, because explanation is the feature that distinguishes it from the rubric it proposes to replace.

`TreeExplainer` returns signed, class-specific Shapley values. The serving code reduces them with `np.abs(sv[0]).mean(axis=1)`, taking the absolute value and averaging across the three classes. What reaches the user is a magnitude — how much a feature mattered, in any direction, for any class — not an attribution to their predicted band. Across 120 attributions sampled from twelve varied inputs, none was negative.

The interface nonetheless captions its chart *"Blue = increases risk score, Red = decreases risk score."* No bar can ever be red. For a record with a credit score of 720, that feature is rendered as increasing risk. This is the one defect in the system that actively misinforms rather than merely underperforming, and Rudin's objection to post-hoc explanation — that it may look authoritative while being unfaithful — describes it exactly [15].

The repair is two lines, given in Section 21.4. It was not applied because it would invalidate every SHAP figure in Sections 14, 21 and 22.

## 26.3 Redundant Features Corrupt the Attribution

`savings_ratio` and `expense_ratio` are exact complements: correlation −1.000000, with `|savings_ratio + expense_ratio − 1|` never exceeding 4.4 × 10⁻¹⁶. `savings_rate` is a third, noisier encoding of the same quantity, correlating at 0.944. `financial_discipline_score` weights `savings_rate` at 0.40.

One underlying quantity therefore occupies four of the top five rows of the SHAP ranking, and ranks four and five carry identical importance to four decimal places. Accuracy is unaffected — a Random Forest is untroubled by collinearity — but a reader of the chart would substantially underestimate how completely a single number determines the model's output.

## 26.4 A Category Was Destroyed During Loading

`insurance_coverage` is generated with three levels. `pandas.read_csv` treats the bare string `None` as a null, so 7,264 records — 33.0% of the dataset — arrived as missing and were imputed to the mode, `Basic`.

The effect on accuracy is negligible, and measured: retraining with the category preserved gives weighted F1 0.5915 against 0.5955, a difference within the ±0.0032 cross-validation spread. Insurance never enters `risk_score`, so the classifier lost nothing it was using.

The effect elsewhere is real. `behavioral_composite_score` weights insurance at 0.20 and is therefore overstated for a third of records. The fitted ordinal map has two levels, so a live user selecting "no insurance" is silently encoded as the training median. The system accepts an input it cannot represent.

## 26.5 The Interface Accepts Inputs the Model Cannot Represent

Every numeric field except `credit_score` admits a wider range than the training data spans. The form takes `investment_experience_years` up to 50 against a training support of 0–15, and `age` up to 100 against 18–75. Values are clipped to the fitted IQR bounds before any feature is derived, which makes the prediction well-defined but not valid: an out-of-range input receives the prediction the model would have made at the boundary.

`savings_rate` is declared non-negative, though the training data runs to −10%. A user whose expenses exceed their income cannot express that state and must enter zero.

`credit_score` is clipped at a lower bound of 660.5 by the IQR rule, discarding the variation among poor-credit individuals — exactly where the feature is most discriminative. This is why `credit_score` ranks eighth in SHAP despite carrying weight +25 in the generating function.

## 26.6 The Model Is Calibrated Against the Wrong Objective

*High* risk is predicted with precision 0.6898 and recall 0.4295. For a screening instrument the asymmetry runs the wrong way: failing to warn a genuinely high-risk person is costlier than an over-conservative recommendation, and the argmax rule weights the two errors equally.

The remedy exists and was not applied. Macro AUC exceeds weighted AUC, meaning the ranking information is present; thresholding on `P(High)` below 0.5 would trade precision for recall along a curve the model already supports.

## 26.7 There Is No Security Posture

No authentication, no authorisation, no sessions, no tokens. `SECRET_KEY` is declared in the settings model and consumed by no code path. The `users` table is created, related to `assessments`, and never written to.

`GET /assessments` returns every stored assessment, including all twenty-six financial fields of each, to any caller. The audit middleware persists the complete request body — income, expenses, debt, credit score — to a table with no access control. CORS restricts two localhost origins, which constrains browsers and not clients.

This was a scoping decision, and on synthetic inputs it is harmless. The system is not deployable against real financial disclosures without an authentication layer, an authorisation model for the history and analytics endpoints, and a retention policy for the audit log.

## 26.8 Defects in the Deployed Backend

`GET /model/info` reads an absolute path from the development machine and therefore returns `{"error": ...}` with HTTP 200 under Docker Compose, the documented deployment path.

The fallback in `ml_service` that locates the inference module when `/ml` is absent ascends one directory too many and resolves to a path that does not exist. The defect is masked under Docker, where the bind mount always exists, and surfaces when the service is run directly, where every prediction returns 503.

The audit middleware describes its database write as "non-blocking best-effort". It is best-effort; it is not non-blocking. A synchronous SQLAlchemy commit executes inside an `async` coroutine and occupies the event loop on every request.

## 26.9 Testing Is Thin

Eleven tests exist: five unit tests over `predict()` and six integration tests against a running service. There are no tests for the preprocessing scripts and none for the frontend.

More importantly, none of the eleven could have caught any of the six defects in this report, because five of the six lived in the *agreement between two representations of one thing* rather than inside any function. The equivalence check of Section 9.7 — asserting that the serving path and the training path compute identical feature vectors — would have caught five of them on the day they were written. It runs in under a minute and is not in the suite.

The integration tests exercise SQLite while the deployment uses PostgreSQL. The dialect-specific failure in `/analytics`, described in Section 18.7, passed its tests and returned HTTP 500 in production.

## 26.10 Methodological Gaps

No logistic-regression baseline was fitted, so the report cannot say whether the non-linear models earned their complexity. Given that the generating function is a weighted sum, a linear model might have performed comparably, and its absence is a real weakness in Section 15.

The published model-comparison table reports a tuned Random Forest against four untuned competitors, because `train.py` overwrites the winner's metrics after tuning. Selection was made on untuned scores and is unaffected, but the table overstates the margin.

The neural network was evaluated on unscaled inputs, which disadvantages it. As a control that lost by a wide margin this does not affect the selection, but the reported figure understates what a properly scaled network would achieve.

No probability calibration was assessed. The interface displays a confidence value; whether a stated confidence of 0.7 corresponds to being correct 70% of the time is unmeasured.

No latency benchmark was performed. Each request constructs a fresh `TreeExplainer` rather than reusing one, and performs a synchronous audit write.

## 26.11 The Recommendations Are Not Grounded

Nine bias rules and eleven recommendation branches are implemented as deterministic functions of the raw inputs and the predicted band. They are heuristics drawn from the behavioural-finance vocabulary, not inferences. None was validated against labelled data, and no claim is made that a user flagged with *present bias* exhibits it. This is the component of the system with the weakest evidentiary basis, and it is the one whose output most resembles advice.
