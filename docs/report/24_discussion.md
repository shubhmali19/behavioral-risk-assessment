# 24. Discussion

## 24.1 What Sixty Percent Means

The instinct on seeing 60.4% accuracy is to call the model weak. That instinct is wrong here, and correcting it is the central interpretive claim of this work.

The label was manufactured by adding noise of standard deviation 8.0 to a signal of standard deviation 7.64 and cutting the result at two percentiles. Half the variance in the underlying score is unrecoverable by any function of the features, because it is not a function of the features. The Bayes-optimal classifier — one that knows the generating equation exactly — reaches 61.04%. The Random Forest reaches 60.39%, which is 98.9% of that limit and 95.9% of the accuracy available above the majority-class baseline.

The model is very nearly the best model that can exist for this problem. What remains is not error to be engineered away; it is the noise term, and no algorithm can see through it.

Two pieces of evidence make this more than an arithmetic coincidence. The model's predicted class distribution (31.4 / 56.2 / 12.5) tracks the Bayes rule's (32.9 / 54.4 / 12.7) rather than the true distribution (35 / 45 / 20), which means it has reproduced the Bayes rule's characteristic retreat toward the central class near a noisy boundary. And 1,706 of its 1,743 errors fall between adjacent bands, with only 37 records confusing *Low* with *High*. A model that had learned nothing would scatter its mistakes. This one places them exactly where the noise places the class boundary.

This kind of analysis is available only because the data is synthetic. It is the one genuine methodological advantage the synthetic approach confers, and it is worth being explicit that it is purchased at a steep price, discussed in Section 24.5.

## 24.2 The Model Is Calibrated Against the Wrong Objective

The Random Forest identifies high-risk individuals with precision 0.6898 and recall 0.4295. It is usually right when it says *High*; it says *High* for fewer than half of those who are.

For a risk-screening instrument this is the wrong way round. The cost of telling a genuinely high-risk person that they are medium-risk is that they take on exposure they cannot absorb. The cost of the reverse error is an unnecessarily conservative recommendation. These costs are plainly asymmetric, and the model's operating point optimises for neither — it optimises for accuracy, which weights them equally.

Section 23.3 supplies the remedy. Macro ROC AUC (0.7712) exceeds weighted ROC AUC (0.7461), an inversion which tells us that the model *ranks* high-risk individuals well even though the argmax rule rarely selects that class for them. The information is present in the probability vector and is thrown away by taking the maximum. Thresholding on `P(High)` at a value below 0.5 — chosen to hit a target recall — would trade precision for recall along a curve the model already supports. The interface displays a confidence figure, so the machinery is in place; only the decision rule needs changing.

That this was not done is a limitation, not a discovery. But it demonstrates something about evaluation practice: a model can be at its Bayes limit on accuracy and still be badly configured for the task it serves.

## 24.3 Failures That Metrics Cannot See

The most instructive result of this project is that its worst defects produced no bad numbers.

Feature engineering was written twice — once for training, once for serving — and the two implementations disagreed on the scale of `savings_rate`, the denominator of `debt_to_income_ratio`, the direction of `age_income_ratio`, the spelling and cardinality of four ordinal maps, and the entire formula for both composite scores. The test set was evaluated through the training path. Every reported metric was therefore correct, and every live prediction was wrong. A user reporting a 10% savings rate was assessed *Medium* where the training scale placed them at *High*, and `P(High)` was not even monotone in the savings rate.

Separately, the questionnaire's third insurance category was silently converted to a null by `pandas.read_csv` and imputed to the mode, so a third of the dataset carried a category it had never held. The explainability module discarded the sign of every SHAP value, so the interface's "red = decreases risk" legend rendered a distinction the data no longer contained. The frontend submitted to the non-persisting endpoint, so the database the analytics dashboard aggregated was never written to by the application.

Five of these six defects share a structure: each lived in the *agreement between two representations of one thing* — two implementations of a feature, two spellings of a category, two endpoints with the same shape, a colour legend and the values it coloured. None was a mistake inside a function. Every function was individually correct.

Unit tests do not find defects of this kind, because a unit test examines one representation. The eleven tests in this repository all passed throughout. What found them was checking one representation against another: routing training rows through the serving preprocessor and comparing the output column by column, reading the CSV as raw text instead of through pandas, asking whether any SHAP value returned by the API was ever negative.

The engineering conclusion is that the appropriate response is not more unit tests but a different kind of test. The equivalence check of Section 9.7 — asserting that the serving path and the training path produce identical feature vectors for the same input — would have caught the five feature defects on the day they were written. It runs in under a minute. It is not yet in the suite, and adding it is the single highest-value change available to this codebase.

The structural response is stronger still, and it was adopted: `preprocess.py` now emits every constant it fits, and `inference.py` reads them. The two paths can no longer disagree about a value because only one of them holds a value. Duplication was removed rather than tested.

## 24.4 A Negative Result Worth Reporting

The investment-preference model achieves 0.2586 accuracy against a 0.2869 majority baseline and a ROC AUC of 0.4949. It is worse than a constant and ranks at chance.

The temptation, on obtaining such a result, is to tune harder, try another algorithm, or quietly drop the component. None would have helped, and the reason is instructive. Reading the generator shows that `investment_preference` is sampled from one of three fixed probability vectors selected by `risk_category` alone. No feature enters the draw. The Bayes ceiling is 0.3675 given perfect knowledge of the risk band, and roughly 0.3210 given the 60.4%-accurate band the system can actually infer.

The model was never going to work, and the diagnosis required reading forty lines of data-generation code rather than running another experiment. This is worth stating as a methodological point: when a model fails, the generating process is a more informative place to look than the hyperparameter grid.

Two cautions attach. This says nothing about whether investment preference is predictable from behavioural attributes in reality — the finding concerns a synthetic label, and a real one would carry real dependence on income, age and experience. And the system still exposes the field through its API and renders it in the interface, which is a defensible choice only because this report states plainly that the value is meaningless.

## 24.5 The Cost of Synthetic Data

Every result above rests on data that no person supplied.

The gains are real. The generating function is known, which is what permits a Bayes ceiling to be computed at all — an analysis unavailable for any real dataset. Twenty-two thousand records were obtained without ethics approval, recruitment or expense. Correlation structure was specified rather than hoped for.

The losses are larger, and three of them bear directly on the interpretation of the results.

The relationships the model discovers are the relationships the generator was written to contain. Section 12.3 reports a correlation of +0.711 between savings rate and financial decision score; this is not a finding about savers, it is a restatement of the formula. When Section 21.5 observes that every feature entering `risk_score` appears in the top eight SHAP ranks, it is confirming that a Random Forest can recover a weighted sum, which was not in doubt.

No lifestyle feature reaches the top ten, and no lifestyle feature appears in `risk_score`. The system was built on the premise, set out in Section 13.6, that discretionary spending reveals risk preferences that direct questions do not. The dataset cannot test that premise, because its author did not encode it. The entire behavioural-economics motivation of this project is, on this data, untestable.

And the reported accuracy measures recovery of a known function, not prediction of human behaviour. A real population's risk band would depend on attributes not collected, would carry measurement error in the self-reports, and would exhibit relationships no generator anticipated. The 60.4% would not transfer, in either direction.

What the project does demonstrate is that the pipeline — elicitation, validation, preprocessing, inference, attribution, persistence, presentation — functions end to end and that its components agree with one another. That is a systems result, and it is a real one. It is not an empirical result about financial behaviour, and Section 26 states so.

## 24.6 Explanation Was the Weakest Link

The stated purpose of the explainability module was to restore, for a learned model, the per-answer transparency that a rule-based rubric provides for free. It falls short on three counts, and the shortfalls compound.

The attribution reaching the user is a magnitude, not a direction, because the serving code takes an absolute value and averages across classes. A user cannot learn from it whether their credit score helped or hurt.

The interface tells them it can. The chart is captioned *"Blue = increases risk score, Red = decreases risk score"* over data in which no value is ever negative. A caption that describes a distinction the data does not carry is worse than no caption, and it is the one defect in this system that actively misinforms rather than merely underperforming.

And the ranking itself is distorted by redundancy. `savings_ratio` and `expense_ratio` correlate at exactly −1.000000; `savings_rate` is a noisy third copy; `financial_discipline_score` weights `savings_rate` at 0.40. One underlying quantity occupies four of the top five rows, and its apparent importance is divided among them. The reader of the chart underestimates how completely a single number determines this model's output.

None of the three affects accuracy. All three affect the only thing the module exists to deliver. A model that is right for reasons it cannot articulate is, for this application, not obviously preferable to the rubric it replaced — and Section 8.5 claimed otherwise. That claim is not sustained by the implementation as it stands, and the fixes required, set out in Sections 21.4 and 22.5, are small.

---

> **Figure 24.1** — *Precision–recall trade-off for the `High` class,* sweeping the decision threshold on `P(High)` from 0.1 to 0.9, with the argmax operating point marked. This substantiates the argument of Section 24.2 and is the figure most likely to be asked about. Place there.

> **Table 24.1** — *Defect taxonomy.* Six rows, one per defect from Section 24.3. Columns: defect, where it lived, whether any metric was affected, whether any existing test could have caught it, how it was found. The pattern in the fourth column — uniformly "no" — is the argument.
