# 5. Research Gap

## 5.1 Preliminary Caution

A research gap should be a statement about what the literature has not established, not a rhetorical device for making a student project appear necessary. Several of the gaps below are gaps this project identifies without closing, and one of them this project actively worsens. Saying so is more useful than the alternative.

## 5.2 Gaps in the Literature

**G1 — Absence of ground truth for risk suitability.** Credit scoring succeeds as a supervised problem because default is observed and eventually labelled [5]. A risk band has no analogous outcome: no institution records, years afterward, whether the band assigned to a client was the correct one. The literature offers validated *instruments* for eliciting risk tolerance [3] but no labelled corpus against which a predictive model of suitability could be fitted or falsified. Without such a corpus, supervised learning has nothing to learn from.

*This project does not close G1. It circumvents it, by generating a synthetic label whose definition its author chose. Section 24.5 explains why that circumvention forfeits every empirical claim about real behaviour, and Section 5.4 returns to it.*

**G2 — Conflation of capacity and tolerance.** Klement's compilation treats the confusion between objective loss-bearing capacity and subjective loss-bearing willingness as endemic to deployed instruments [4]. Prospect theory implies the self-report half is the unreliable half, since stated risk attitude shifts with framing and with the reference point [1]. What is missing is an elicitation design that separates the two constructs and measures them independently.

*This project does not close G2 either. Its twenty-six parameters are overwhelmingly capacity-side, and Section 13.6 acknowledges as much.*

**G3 — Interaction effects are unrepresentable in additive rubrics.** A rubric is a sum of independent terms and therefore, by construction, a model without interactions. The behavioural-finance literature is rich in conditional claims — that present bias is stronger under liquidity constraint, that loss aversion varies with prior gains [1], [2] — none of which an additive score can express. Tree ensembles represent interactions natively [9], [13].

*This project addresses G3, though the demonstration is weak: its synthetic label is a weighted sum with no interaction terms, so there was little interaction structure for the model to find. Section 22.2 shows the Random Forest recovering, in essence, a linear score.*

**G4 — Post-hoc explanation is assumed adequate without being audited.** The explainability literature establishes that Shapley attribution is axiomatically well-founded [6] and exactly computable for trees [7]. Rudin objects that a post-hoc explanation is not the computation it describes, and may mislead while appearing authoritative [15]. What is largely missing is empirical scrutiny of whether explanation *pipelines*, as opposed to explanation *methods*, preserve the properties the method guarantees.

*This project contributes to G4, unintentionally and by counterexample. Section 21.4 documents an implementation whose SHAP values were correct on computation and then had their sign discarded before display, so the interface distinguished risk-increasing from risk-decreasing features over data in which no value was ever negative. The attribution method was sound. The pipeline around it was not, and nothing detected the difference.*

**G5 — Training-serving consistency is not part of the evaluation apparatus.** Sculley and colleagues catalogue the maintenance hazards of production machine learning and observe that most of a deployed system is not the model [8]. The evaluation literature, however, measures models. A held-out test set drawn from the training pipeline certifies the estimator; it says nothing about the separate code path that will compute features for live users, and reports accuracy that live users do not receive.

*This project contributes evidence for G5. Section 22.4 documents five disagreements between the training and serving feature computations, each of which left every reported metric correct and every live prediction wrong.*

## 5.3 What the Gaps Imply

Taken together, G1 and G2 mean that a supervised risk-profiling system cannot presently be validated on real data, because neither the label nor a clean measurement of the target construct exists. This is not a gap a final-year project can close, and pretending otherwise would be dishonest.

G3, G4 and G5 are tractable, and they concern the machinery rather than the science. They ask whether a learned model can represent what a rubric cannot, whether the explanation a user sees is the explanation the method computed, and whether the accuracy a report claims is the accuracy a user receives.

## 5.4 The Gap This Project Addresses

The addressable gap, stated narrowly:

> Existing accounts of machine-learned risk profiling report model accuracy against a benchmark of perfect classification and assume, without verification, that the features computed at serving time match those computed at training time, and that the explanation displayed to the user preserves the semantics of the attribution method that produced it.

Three commitments follow, and they organise the rest of this report.

Accuracy is reported against a **derived Bayes-optimal ceiling** rather than against 1.0. Because the label's generating function is known — a consequence of the synthetic data whose costs Section 24.5 tallies — the maximum attainable accuracy can be computed exactly. It is 0.6104, and the model reaches 98.9% of it. An absolute figure of 60% conveys almost nothing; the same figure against its ceiling conveys most of what matters.

Training–serving equivalence is **verified rather than assumed**, by routing training records through the serving preprocessor and comparing the resulting feature vectors column by column, and by checking that predictions agree on every held-out row.

The explanation pipeline is **audited end to end**, from the SHAP call to the pixel the user sees. That audit is what exposed the sign-discarding defect of Section 21.4, which no test of the SHAP library and no test of the model could have found.

None of these is a contribution to behavioural finance or to machine learning. Each is a contribution to the practice of building systems that make claims about people's money, and the honest summary of this project's ambition is that it is a systems result with a rigorous evaluation, not a scientific finding.
