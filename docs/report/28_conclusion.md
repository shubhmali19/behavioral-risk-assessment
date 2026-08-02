# 28. Conclusion

## 28.1 What Was Built

An end-to-end system that elicits twenty-six demographic, financial and lifestyle attributes through a four-step web form, classifies the respondent into one of three financial-risk bands with a tuned Random Forest, attributes the outcome with Shapley values, persists the assessment to PostgreSQL, and renders the result through a React dashboard. Three services compose under Docker. Seven REST endpoints are validated by schemas that also generate their own documentation.

The dataset is synthetic: 22,000 records produced by a generator with documented conditional dependencies, because no public dataset joins these attributes to a behavioural risk label, and Section 5.2 argues no such label exists even in principle.

## 28.2 What Was Found

**The model operates at the Bayes limit.** Because the label's generating function is known, the maximum accuracy attainable by any classifier can be computed rather than guessed. It is 0.6104, the noise term having a standard deviation of 8.0 against a signal of 7.64. The Random Forest attains 0.6039 — 98.9% of the ceiling, and 95.9% of the accuracy available above the majority baseline. Its predicted class distribution tracks the Bayes rule's rather than the truth, and 1,706 of its 1,743 errors fall between adjacent bands. Read against 1.0 the result looks mediocre; read against what the data permits, the model recovers nearly all recoverable signal.

**A negative result is reported in full.** The secondary model predicting investment preference scores 0.2586 against a majority baseline of 0.2869 and ranks at chance. Reading the generator shows the label is drawn from a distribution conditioned on the risk band alone, giving a ceiling of 0.3675 under perfect knowledge. No algorithm, no tuning and no additional feature could have rescued it. The diagnosis came from forty lines of data-generation code, not from another experiment.

**The worst defects produced no bad numbers.** Feature engineering was implemented twice — once for training, once for serving — and the two disagreed on the scale of `savings_rate`, the denominator of `debt_to_income_ratio`, the direction of `age_income_ratio`, the spelling of four ordinal maps, and the formula for both composite scores. Every reported metric stayed correct, because the test set was evaluated through the training path. Every live prediction was wrong. Separately, a third of the `insurance_coverage` column was destroyed by `pandas` on load; the explanation pipeline discarded the sign of every attribution before display; and the form submitted to the non-persisting endpoint, so nothing a user entered ever reached the database.

Five of those six defects share one structure. None was a mistake inside a function; each lived in the *agreement between two representations of the same thing* — two implementations of a feature, two spellings of a category, two endpoints of the same shape, a colour legend and the values it coloured. All eleven tests passed throughout. What exposed them was checking one representation against another. This is the hazard Sculley and colleagues describe as the hidden technical debt of machine learning systems [8], and it is the finding of this project most likely to generalise.

## 28.3 What Was Not Achieved

Seven of ten objectives were met, two of them only after defects found while writing this report were repaired.

Two were not met. The explainability module returns absolute magnitudes averaged across classes rather than signed attributions to the predicted band, so the interface's caption — *"Blue = increases risk score, Red = decreases risk score"* — describes a distinction its data does not carry, and no bar is ever red. This is uncomfortable, because explanation is the sole feature distinguishing this system from the rubric it proposes to replace. The repair is two lines and is deferred only because it invalidates every SHAP figure already generated. And the investment-preference objective was unattainable by construction.

The redundancy among `savings_rate`, `savings_ratio` and `expense_ratio` — the latter two correlating at exactly −1.000000 — splits one dominant signal across four of the five top-ranked features, so the explanation understates how completely one quantity determines the model. Accuracy is untouched; interpretation is not.

## 28.4 What It Does Not Show

Nothing in this report is evidence about human financial behaviour. Every correlation recovered is one the generator was written to contain. The project's own premise — that lifestyle spending reveals dispositions self-report conceals — is untestable here, because no lifestyle attribute enters the generating function. That no lifestyle feature reaches the top ten SHAP ranks says something about the generator and nothing about people.

The Bayes-ceiling analysis, the report's strongest methodological contribution, is available only because the data is synthetic. The analysis and the limitation are the same fact seen from two sides.

## 28.5 Closing Assessment

Judged as science, the project establishes nothing about behavioural finance and applies no novel method.

Judged as engineering, it delivers a working, containerised, verified pipeline and an evaluation more careful than the result required — accuracy reported against a derived ceiling rather than against perfection, serving-time feature computation proved identical to training-time, and a failing component reported as failing rather than quietly removed.

The most durable lesson is the least glamorous. A test set drawn from the training pipeline certifies the estimator and says nothing about the code that will serve it. The accuracy in a report and the accuracy a user receives are different quantities, and in this system they differed for most of its existence, silently, while every metric agreed. Establishing that they now coincide took one comparison, sixty seconds of compute, and no new theory — and it should have been the first thing written, not among the last.
