# 2. Introduction

## 2.1 Background

Classical finance assumes that people, faced with a choice among uncertain outcomes, maximise expected utility. The assumption is analytically convenient and empirically false in ways that are systematic rather than random. Kahneman and Tversky demonstrated that individuals evaluate outcomes as gains and losses relative to a reference point rather than as final states of wealth, that they weight losses roughly twice as heavily as equivalent gains, and that they distort small probabilities [1]. Preferences reverse when the same choice is described differently.

Behavioural finance grew out of that observation. Barberis and Thaler survey its two structural claims: that arbitrage is limited, so mispricing can persist, and that the psychology of real investors departs predictably from the rational agent of the textbook [2]. For an individual deciding how much to save, whether to hold equity, and how much debt to carry, the departures matter more than the equilibrium.

Financial institutions have long needed to place a client somewhere on a risk spectrum before recommending anything. The instrument they use is almost always a questionnaire scored by a fixed rubric. Grable and Lytton's thirteen-item scale is the best known and among the few to have been validated psychometrically [3]. Its persistence is a mark of how little the practice has changed.

## 2.2 Motivation

Two weaknesses of the rubric approach motivated this project.

The first is that the weights are asserted. An analyst decides that a question about reaction to a market decline is worth five points and that dependants subtract three, and nothing in the data confirms or refutes those numbers. A rubric cannot express the idea that a low savings rate is more serious for a person supporting a family than for one who is not, because a sum of independent terms has no way to represent an interaction.

The second is subtler and is documented across the industry literature. Questionnaires routinely conflate two different quantities: a person's *capacity* to absorb loss, which is an objective fact about their balance sheet, and their *tolerance* for it, which is a psychological disposition. Klement's survey of the field treats the confusion as endemic and notes that self-reported willingness to take risk is a poor guide to behaviour under actual loss [4].

Machine learning offers a partial answer to the first weakness. Where labelled data exists, the weights need not be asserted; they can be estimated. This is unremarkable in adjacent domains — credit scoring has used statistical classification for decades, and Lessmann and colleagues benchmark a large family of algorithms on that task [5]. It is less common in risk profiling, and the reason is not technical. A credit decision needs to be accurate. A risk profile needs to be *explicable* to the person it describes, and a learned model, unlike a rubric, does not explain itself.

The last decade closed that gap. Lundberg and Lee unified several attribution methods under the Shapley value from cooperative game theory [6], and a follow-up gave an exact polynomial-time algorithm for tree ensembles [7], which makes per-prediction attribution cheap enough to compute inside a web request. What a rubric provides by construction — a per-answer contribution to the score — a learned model can now provide by computation.

## 2.3 Scope of This Work

This project builds an end-to-end system on that premise: elicit twenty-six demographic, financial and lifestyle attributes through a web form; classify the respondent into one of three risk bands with a trained model; attribute the outcome to the individual's own inputs with SHAP; persist the assessment; and present the result through a dashboard.

Two boundaries must be stated at the outset, because they determine how everything that follows should be read.

**The data is synthetic.** No survey was administered and no human respondent contributed a record. The 22,000 rows were produced by a generator with documented conditional dependencies, because no public dataset combines these attributes with a behavioural risk label. The accuracy reported in Section 23 measures how faithfully a learning algorithm recovers a known generating process. It is not evidence about the financial behaviour of real people, and no claim to the contrary is made anywhere in this report.

**The system is not financial advice.** It classifies. The recommendations it displays are produced by fixed rules over the user's inputs, not by the model, and they are illustrative.

## 2.4 Contributions

What this work offers is chiefly a systems result, together with three findings that emerged from examining the system rather than from designing it.

A complete, containerised pipeline runs from data generation through preprocessing, model selection, explanation, persistence and presentation, with the interfaces between its stages specified and verified.

Because the label's generating function is known, the **Bayes-optimal accuracy** for this classification can be computed rather than estimated. It is 0.6104. The tuned Random Forest attains 0.6039, or 98.9% of the ceiling — a figure that transforms an apparently mediocre 60% into evidence that the model has extracted nearly all recoverable signal. Reporting an accuracy against a derived ceiling, rather than against 1.0, is the methodological point this report presses hardest.

A **negative result** is reported in full. The secondary model predicting investment preference scores below its own majority-class baseline. Inspection of the generator shows the label was drawn from a distribution conditioned on nothing but the risk band, so no model could have succeeded. The diagnosis came from reading forty lines of data-generation code, not from further experiments.

A class of defect is characterised that **no accuracy metric can expose**. Feature engineering was implemented twice — once for training, once for serving — and the two disagreed in five places while every reported metric remained correct, because the test set was evaluated through the training path. Sculley and colleagues describe this family of maintenance hazards as the hidden technical debt of machine learning systems [8]. The repair here was structural: the training pipeline now emits every constant it fits, and the serving path reads them, so the two cannot diverge.

## 2.5 Organisation

Section 3 reviews the literature. Sections 4 to 7 establish the existing approach, the gap, the problem and the objectives. Section 8 presents the proposed system and Sections 9 to 11 its methodology and architecture. Sections 12 to 14 describe the dataset, the input parameters and the derived features. Sections 15 to 21 cover model selection, implementation and explainability. Sections 22 to 24 report and interpret the results. Sections 25 to 28 assess advantages, limitations and future work, and Section 29 lists references.
