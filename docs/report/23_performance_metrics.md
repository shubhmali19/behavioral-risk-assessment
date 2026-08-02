# 23. Performance Metrics

## 23.1 Choice of Metrics

Accuracy is reported but is not the criterion. With classes at 35 / 45 / 20, a constant predictor reaches 45%, and any accuracy figure must be read against that floor rather than against zero.

Weighted F1 is the selection criterion. It averages the per-class harmonic mean of precision and recall, weighting each class by its support, and so penalises a model that achieves accuracy by neglecting the minority band. Macro F1 is also reported, since it weights the three classes equally and therefore exposes the *High*-class weakness that the weighted figure partially conceals.

ROC AUC is computed one-vs-rest. It measures the ranking quality of the predicted probabilities independently of the decision threshold, which matters here because the interface displays a confidence value and Section 24 argues that the operating threshold should be reconsidered.

## 23.2 Classification Report

Tuned Random Forest, held-out partition of 4,400 records.

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Low | 0.6565 | 0.5883 | 0.6205 | 1,540 |
| Medium | 0.5554 | 0.6934 | 0.6168 | 1,980 |
| High | 0.6898 | 0.4295 | 0.5294 | 880 |
| | | | | |
| **Accuracy** | | | **0.6039** | 4,400 |
| Macro average | 0.6339 | 0.5704 | 0.5889 | 4,400 |
| Weighted average | 0.6177 | 0.6039 | 0.6006 | 4,400 |

The gap between macro F1 (0.5889) and weighted F1 (0.6006) is entirely attributable to the *High* class, whose F1 of 0.5294 trails the other two by nine points.

The shape of that deficit matters more than its size. *High* carries the **highest precision of any class** at 0.6898 and the **lowest recall** at 0.4295. When the model announces high risk it is usually correct; it announces it for fewer than half the individuals who warrant it. Section 22.2 shows that this is the Bayes-optimal response to threshold noise rather than a learned bias, and Section 24 argues it is nonetheless the wrong operating point for the application.

## 23.3 Discrimination

| Metric | Value |
|---|---|
| ROC AUC, one-vs-rest, weighted | 0.7461 |
| ROC AUC, one-vs-rest, macro | 0.7712 |

Macro AUC exceeds weighted AUC, which is the reverse of the usual pattern and is informative. AUC measures ranking, not thresholded decisions. The model ranks *High*-risk individuals well — it assigns them elevated probabilities — even though the argmax rule rarely selects that class for them. The information required to identify high-risk individuals is present in the probability vector and is discarded by taking the maximum.

This is the quantitative basis for the recommendation in Section 24 that the interface should threshold on `P(High)` rather than report the argmax.

## 23.4 Stability

Five-fold stratified cross-validation on the tuned model over the full 22,000 records:

| Statistic | Weighted F1 |
|---|---|
| Mean | 0.5996 |
| Standard deviation | 0.0032 |

The held-out estimate of 0.6006 lies within a third of a standard deviation of the cross-validated mean, so the reported performance is not an artefact of the particular 80/20 split. A standard deviation of 0.0032 across folds also sets the scale against which differences between models should be judged: the 1.76-point F1 gap between the Random Forest and LightGBM is roughly five standard deviations and is real, whereas the 0.03-point gap between LightGBM and CatBoost is not.

That same scale governs the insurance-category defect of Section 12.5. Restoring the destroyed `None` level changes weighted F1 from 0.5955 to 0.5915, a difference of 0.0040 — approximately one standard deviation, and therefore not distinguishable from fold-to-fold variation.

## 23.5 Performance Against the Attainable Ceiling

Reporting accuracy against a ceiling of 1.0 is misleading for a label that is roughly half noise by construction. The Bayes-optimal accuracy derived in Section 22.2 provides the correct denominator.

| Reference point | Accuracy | Interpretation |
|---|---|---|
| Random guessing (uniform) | 0.3333 | no information |
| Majority class (always *Medium*) | 0.4500 | prior only |
| **Tuned Random Forest** | **0.6039** | — |
| **Bayes-optimal ceiling** | **0.6104** | maximum attainable |

Normalising the model's position between the majority baseline and the ceiling:

```
(0.6039 − 0.4500) / (0.6104 − 0.4500)  =  0.9595
```

The Random Forest captures **95.9% of the accuracy that is available to be captured** above the trivial baseline, and reaches 98.9% of the absolute ceiling. Interpreting 0.6039 as a weak result mistakes the noise floor of the data for a shortcoming of the model.

This framing depends entirely on the label being synthetic and its generating function being known. It is available here precisely because the data was constructed, and it would not be available for a real dataset. That is one of the few advantages a synthetic study confers, and Section 24 discusses what is given up in exchange.

## 23.6 Secondary Model

| Metric | Investment-preference model | Reference |
|---|---|---|
| Accuracy | 0.2586 | majority baseline 0.2869 |
| Weighted F1 | 0.1892 | — |
| ROC AUC (ovr, weighted) | 0.4949 | chance 0.5000 |
| Ceiling given predicted risk | ≈ 0.3210 | — |
| Ceiling given perfect risk | 0.3675 | — |

The model performs below the majority baseline and ranks at chance. Section 22.3 establishes that the label was constructed without reference to any feature, so this is a property of the target rather than of the estimator. No metric in this table should be cited as evidence about the predictability of investment preference in general.

## 23.7 Serving Latency

Latency was not measured systematically and no benchmark is reported. Each prediction loads no artefacts — models are cached at process start — but does construct a `TreeExplainer` and compute exact Shapley values for one row against a 200-tree ensemble of depth 10, which dominates the request cost. The audit-log write described in Section 20.6 executes synchronously on the event loop and adds a database round trip to every request.

Both are addressable: the explainer can be constructed once and reused, and the audit write can be dispatched to a background task. Neither was done, and the omission of any latency measurement is recorded in Section 26.

---

> **Figure 23.1** — *Per-class precision and recall,* grouped bars across Low / Medium / High. The inversion on *High* — precision high, recall low — is the point. Place in Section 23.2.

> **Figure 23.2** — *ROC curves, one-vs-rest,* three classes plus macro-average and the chance diagonal. Shared with Figure 15.2; render once. Place in Section 23.3.

> **Figure 23.3** — *Model accuracy against reference points,* a horizontal bar or number-line showing 0.3333, 0.4500, 0.6039 and 0.6104, with the interval between baseline and ceiling shaded. This visualises the 95.9% figure and is the most important chart in the chapter. Place in Section 23.5.

> **Figure 23.4** — *Cross-validation fold scores,* five points with the mean and ±1 s.d. band. Place in Section 23.4.
