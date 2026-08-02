# 3. Literature Review

## 3.1 Departures from Expected Utility

The starting point of behavioural finance is a negative result about the standard model. Kahneman and Tversky's prospect theory replaces expected utility with a value function defined over gains and losses relative to a reference point, concave in gains, convex and steeper in losses, together with a weighting function that overweights small probabilities [1]. Two consequences bear directly on risk profiling. Loss aversion means a person's stated willingness to accept a gamble depends on how the gamble is framed, so a questionnaire's wording is not neutral. And reference dependence means risk attitude is not a fixed personal constant; it moves with recent outcomes.

Barberis and Thaler's survey organises the field around limits to arbitrage and investor psychology, and catalogues the biases that recur in the empirical literature: overconfidence, which inflates trading frequency; herding; mental accounting; and present bias in intertemporal choice [2]. Their treatment is relevant here mainly as a caution. These biases are established as population-level regularities, established through controlled experiment and market data. They are not established as attributes reliably inferable from a person's demographic and spending profile, which is what an automated system would need.

## 3.2 Measuring Risk Attitude

Grable and Lytton constructed and validated a thirteen-item instrument for financial risk tolerance, reporting its factor structure and internal consistency [3]. The scale remains a reference point three decades on, and its methodology — item development, pilot testing, psychometric validation — is what distinguishes an instrument from a form.

Klement's compilation for the CFA Institute Research Foundation surveys the state of practice and is unusually candid about its failures [4]. The recurring criticism is conceptual rather than statistical: instruments intended to measure *risk tolerance*, a psychological disposition, frequently measure *risk capacity*, an objective property of a balance sheet, or silently blend the two. A person with substantial savings and no dependants has high capacity regardless of how they feel about volatility. Conflating the two produces an assessment that is neither.

This distinction shapes the present work and its limits. The twenty-six parameters collected here are overwhelmingly capacity-side: income, expenses, debt, buffer, credit score. The lifestyle attributes were included on the reasoning that discretionary spending might reveal dispositions that self-report does not, since Kahneman and Tversky's framing effects imply that asking someone directly how much risk they tolerate is unreliable. Whether that reasoning holds cannot be tested on the data used here, for reasons Section 24.5 sets out.

## 3.3 Statistical Classification of Financial Risk

Applying supervised learning to financial risk is not novel. Credit scoring has done so since long before the term machine learning was common, and Lessmann and colleagues provide the definitive modern benchmark, comparing a large family of classifiers across multiple credit datasets and several performance measures [5]. Their headline finding is that ensembles of decision trees are consistently among the strongest performers and that differences between the leading methods are often smaller than differences between evaluation protocols.

The algorithmic literature underlying those ensembles is well settled. Breiman's Random Forest grows decorrelated trees on bootstrap samples with feature subsampling at each split, and derives a bound on generalisation error in terms of individual tree strength and inter-tree correlation [9]. Gradient boosting fits trees sequentially against the ensemble's residual; XGBoost contributes a regularised objective and a sparsity-aware split-finding algorithm [10], LightGBM contributes gradient-based one-side sampling and histogram binning for speed [11], and CatBoost contributes ordered boosting and a principled treatment of categorical variables that avoids target leakage [12].

Whether such ensembles remain preferable to neural networks on tabular data has been examined directly. Grinsztajn, Oyallon and Varoquaux benchmark both families across a curated collection of tabular datasets and find tree-based models still ahead, attributing the gap to their robustness to uninformative features and to their bias toward axis-aligned, non-smooth decision boundaries [13]. This finding informed the model selection in Section 15, where a neural network was included as a control and lost by a wide margin.

## 3.4 Explanation

A learned classifier gives up the transparency of a rubric, and the explainability literature exists to buy some of it back.

Ribeiro, Singh and Guestrin's LIME explains an individual prediction by fitting an interpretable surrogate — typically sparse linear — to the model's behaviour in a neighbourhood of the instance [14]. The approach is model-agnostic, which is its strength, and locally approximate, which is its weakness: the explanation is of the surrogate, not of the model.

Lundberg and Lee showed that LIME and several other attribution methods are special cases of a single class of additive feature-attribution measures, and that within that class the Shapley value is the unique solution satisfying local accuracy, missingness and consistency [6]. This moves attribution from heuristic to axiomatic. The obstacle is cost: exact Shapley values require evaluating all feature subsets, which is exponential.

That obstacle disappears for tree ensembles. Lundberg and colleagues give a polynomial-time algorithm computing exact Shapley values for trees, and extend it to interaction effects and to global summaries built by aggregating local explanations [7]. This result is what makes the present system possible: it permits exact per-user attribution over a 200-tree ensemble inside a single HTTP request, without sampling.

A dissenting position deserves recording. Rudin argues that for high-stakes decisions one should not explain a black box but build an interpretable model instead, since a post-hoc explanation is by definition not the computation it purports to describe, and may be faithful in aggregate while misleading in particular [15]. The argument has force in the present setting. Section 21.4 documents an implementation in which the attribution reaching the user had its sign discarded — a post-hoc explanation that was not merely approximate but directionally uninformative, while continuing to look authoritative. Rudin's warning is that explanations invite exactly this kind of trust, and the experience here supports it.

## 3.5 Machine Learning Systems as Engineering Artefacts

The literature above concerns models. A deployed risk-assessment system is not a model, and the distinction turned out to be where this project's most instructive failures lived.

Sculley and colleagues frame the maintenance burden of production machine learning as technical debt, and enumerate its forms: entanglement, in which changing anything changes everything; undeclared consumers; data dependencies that no compiler checks; configuration debt; and the accumulation of glue code around a small modelling core [8]. Their central observation is that only a fraction of a real ML system is the learning algorithm, and that the surrounding infrastructure is where defects accumulate unobserved.

Section 24.3 of this report is, in effect, a case study in that claim. Five defects arose from a single feature computation being implemented twice, in two languages of expression, with no mechanism asserting their equivalence. Every unit test passed. Every reported metric was correct. Every live prediction was wrong. The literature on model evaluation offers no protection against this, because the fault is not in the model.

## 3.6 Position of This Work

The behavioural-finance literature establishes that risk attitude is unstable, frame-dependent and poorly measured by direct question. The measurement literature establishes that existing instruments conflate capacity with tolerance. The machine-learning literature establishes that tree ensembles are the appropriate estimator for tabular financial data, and that exact per-instance attribution for such models is computationally free. The systems literature establishes that the resulting artefact will fail in places the model literature never looks.

This project sits at the intersection, and its principal claims are correspondingly modest. It does not advance behavioural finance, because its data is synthetic. It does not advance machine learning, because it applies established methods. What it contributes is an end-to-end system in which the interfaces between these stages are specified and verified, an evaluation conducted against a derived Bayes ceiling rather than against perfection, and a documented account of the failures that the standard evaluation apparatus does not detect.
