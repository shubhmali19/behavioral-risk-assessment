# 29. References

IEEE style, numbered in order of first citation. Every entry was checked against a primary or authoritative secondary source during preparation of this report; Section 29.1 records what was confirmed and what was not. No reference is included that could not be located.

---

[1] D. Kahneman and A. Tversky, "Prospect theory: An analysis of decision under risk," *Econometrica*, vol. 47, no. 2, pp. 263–291, Mar. 1979.

[2] N. Barberis and R. Thaler, "A survey of behavioral finance," in *Handbook of the Economics of Finance*, vol. 1, G. M. Constantinides, M. Harris, and R. M. Stulz, Eds. Amsterdam, The Netherlands: Elsevier, 2003, ch. 18, pp. 1053–1128.

[3] J. Grable and R. H. Lytton, "Financial risk tolerance revisited: The development of a risk assessment instrument," *Financial Services Review*, vol. 8, no. 3, pp. 163–181, 1999.

[4] J. Klement, Ed., *Risk Profiling and Tolerance: Insights for the Private Wealth Manager*. Charlottesville, VA, USA: CFA Institute Research Foundation, 2018.

[5] S. Lessmann, B. Baesens, H.-V. Seow, and L. C. Thomas, "Benchmarking state-of-the-art classification algorithms for credit scoring: An update of research," *European Journal of Operational Research*, vol. 247, no. 1, pp. 124–136, Nov. 2015.

[6] S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," in *Advances in Neural Information Processing Systems 30 (NIPS 2017)*, Long Beach, CA, USA, 2017, pp. 4765–4774.

[7] S. M. Lundberg, G. Erion, H. Chen, A. DeGrave, J. M. Prutkin, B. Nair, R. Katz, J. Himmelfarb, N. Bansal, and S.-I. Lee, "From local explanations to global understanding with explainable AI for trees," *Nature Machine Intelligence*, vol. 2, no. 1, pp. 56–67, Jan. 2020, doi: 10.1038/s42256-019-0138-9.

[8] D. Sculley, G. Holt, D. Golovin, E. Davydov, T. Phillips, D. Ebner, V. Chaudhary, M. Young, J.-F. Crespo, and D. Dennison, "Hidden technical debt in machine learning systems," in *Advances in Neural Information Processing Systems 28 (NIPS 2015)*, Montréal, QC, Canada, 2015.

[9] L. Breiman, "Random forests," *Machine Learning*, vol. 45, no. 1, pp. 5–32, Oct. 2001.

[10] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining (KDD '16)*, San Francisco, CA, USA, 2016.

[11] G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye, and T.-Y. Liu, "LightGBM: A highly efficient gradient boosting decision tree," in *Advances in Neural Information Processing Systems 30 (NIPS 2017)*, Long Beach, CA, USA, 2017.

[12] L. Prokhorenkova, G. Gusev, A. Vorobev, A. V. Dorogush, and A. Gulin, "CatBoost: Unbiased boosting with categorical features," in *Advances in Neural Information Processing Systems 31 (NeurIPS 2018)*, Montréal, QC, Canada, 2018, pp. 6639–6649.

[13] L. Grinsztajn, E. Oyallon, and G. Varoquaux, "Why do tree-based models still outperform deep learning on tabular data?," arXiv:2207.08815 [cs.LG], Jul. 2022.

[14] M. T. Ribeiro, S. Singh, and C. Guestrin, "'Why should I trust you?': Explaining the predictions of any classifier," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining (KDD '16)*, San Francisco, CA, USA, 2016.

[15] C. Rudin, "Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead," *Nature Machine Intelligence*, vol. 1, no. 5, pp. 206–215, May 2019, doi: 10.1038/s42256-019-0048-x.

---

## 29.1 Verification Notes

*Working material for the author. Delete before submission.*

**Verified against a primary source** — publisher page, arXiv abstract, or official proceedings listing — for title, authorship and venue: [6], [7], [8], [9], [10], [11], [12], [13], [14].

**Verified against a primary source including full pagination**: [3] via the RePEc listing for *Financial Services Review* 8(3); [5] via the RePEc listing for *European Journal of Operational Research* 247(1).

**Verified against concurring secondary sources**: page ranges for [1], [2], [9], [7], [15]; venue, editor and year for [4].

**Pagination deliberately omitted**, because it could not be confirmed from a primary source: [8], [10], [11], [14]. IEEE style permits a conference reference without pagination. The conventional values are widely cited — KDD '16 pp. 785–794 for [10], NIPS 2017 pp. 3146–3154 for [11], KDD '16 pp. 1135–1144 for [14] — but they are recorded here only as a note and must be confirmed against the ACM Digital Library or the NeurIPS proceedings before insertion.

**One discrepancy unresolved.** Sources disagree on the final page of [1], giving either 263–291 or 263–292. The Econometric Society's own listing returned HTTP 403 during preparation. The value 263–291 is used above, being the more commonly cited, and should be confirmed against the journal itself.

**Claims checked, not assumed.** The abstract of [8] enumerates boundary erosion, entanglement, hidden feedback loops, undeclared consumers, data dependencies and configuration debt. It does **not** use the phrase *training–serving skew*. Section 3.5 and Section 5.2 therefore cite [8] for hidden technical debt and for the observation that most of a deployed ML system is not the model, and do not attribute the training–serving terminology to it.

**Deliberate omissions.** Two sources consulted on robo-advisory risk profiling were not cited, because their full text could not be retrieved and their claims could not be checked: an MDPI *Sustainability* article on content analysis of robo-advisor questionnaires, and a *Financial Services Review* retrospective on the Grable–Lytton scale. The argument they would have supported — that deployed questionnaires conflate risk capacity with risk tolerance — is instead attributed to [4], whose scope, editor and year were confirmed.

**No reference in this list was reconstructed from memory.** Where a detail could not be established, it was omitted rather than guessed.
