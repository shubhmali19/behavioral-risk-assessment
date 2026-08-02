# 4. Existing System

## 4.1 The Rubric-Scored Questionnaire

The instrument in near-universal use for retail risk profiling is a short questionnaire whose answers are converted to a score by a fixed table of weights. A respondent answers between ten and twenty items; each response carries a preset point value; the values are summed; the total is compared against cut-offs that map it onto a small number of bands, typically labelled conservative, moderate and aggressive. An allocation is then recommended per band.

Grable and Lytton's thirteen-item scale is the canonical academic example and one of the few subjected to psychometric validation [3]. Commercial implementations, whether administered by an adviser or embedded in a robo-advisory onboarding flow, follow the same structure.

## 4.2 Why It Persists

The approach has genuine merits, and any replacement must account for them rather than dismiss them.

It is transparent. An adviser can point at a row of the scoring table and tell a client precisely how many points their answer contributed. This is not a post-hoc reconstruction of the model's reasoning; it *is* the model's reasoning, and the distinction matters when a client disputes an outcome or a regulator requests an audit trail.

It is cheap. No data collection, no training, no infrastructure. The rubric is a spreadsheet.

It is stable. The same answers always give the same score, and the score does not drift as a training population changes.

And it is defensible. Rudin's argument that high-stakes decisions should use inherently interpretable models rather than explained black boxes describes the rubric exactly [15]. The incumbent is not a naive baseline; it is the position the explainability literature would recommend on principle.

## 4.3 Limitations

Three weaknesses are structural rather than incidental.

**The weights encode assumption, not evidence.** Nothing in any dataset determines that a particular answer should be worth five points. The rubric expresses an analyst's beliefs about what constitutes risk, and where those beliefs are wrong the instrument is wrong in the same direction for every respondent it ever scores. There is no mechanism by which accumulated outcomes correct it.

**Additive scoring cannot represent interaction.** A sum of independent terms is, by construction, a model without interaction. It cannot express that a thin emergency fund is more dangerous for a sole earner with dependants than for a dual-income household, or that high debt matters less at high income. Every such conditional relationship must be either ignored or hard-coded as a special case, and the number of special cases grows combinatorially.

**Capacity and tolerance are conflated.** Klement's compilation identifies this as the field's characteristic failure: instruments that purport to measure a psychological disposition in fact measure a balance-sheet fact, or blend the two into a number that measures neither cleanly [4]. Since prospect theory tells us that stated risk attitude is frame-dependent and reference-dependent [1], the self-report half of such a blend is the less reliable half, and no amount of careful weighting repairs it.

## 4.4 Statistical Alternatives Already in Use

It would be inaccurate to present machine learning as absent from financial risk assessment. It is well established in the adjacent problem of credit scoring, where Lessmann and colleagues benchmark dozens of classifiers and find tree ensembles consistently strong [5]. Banks have used statistical scorecards for decades.

The reason those methods did not migrate into risk profiling is instructive, and it is not a matter of technical difficulty. A credit model predicts an event — default — that is observed, recorded and eventually labelled. A risk profile predicts a *suitability*, for which there is no ground truth: no institution records, years later, whether a client's assigned band was correct. Absent labels, supervised learning has nothing to fit.

Where machine learning does appear in robo-advisory platforms, it typically operates downstream of the questionnaire — optimising an allocation given a band the rubric assigned — rather than replacing the assignment itself.

## 4.5 The Position This Project Occupies

The system built here replaces the rubric's asserted weights with weights estimated from data, and replaces its built-in transparency with SHAP attributions computed per prediction [6], [7]. A tree ensemble captures the interactions an additive rubric cannot, and exact Shapley values for trees restore the per-answer contribution that was the rubric's chief virtue.

Two things should be said plainly about the terms of that trade.

The label problem identified in Section 4.4 has not been solved. This project trains on a synthetic label whose generating function was written by its author. It sidesteps the absence of ground truth rather than addressing it, and Section 24.5 is explicit that this limits every empirical claim the report can make.

And the restored transparency is post-hoc, which is exactly the arrangement Rudin cautions against [15]. Section 21.4 documents how it failed here in practice: the attribution reaching the user had its sign stripped, so the interface confidently displayed a legend distinguishing risk-increasing from risk-decreasing features over data in which no value was ever negative. The rubric could not have failed in that way. It is worth conceding that on this particular axis, the incumbent remains ahead.
