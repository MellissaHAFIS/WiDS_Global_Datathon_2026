I’ll now review the four state-of-the-art notebooks sequentially, extract their modeling and validation patterns, and then synthesize a practical “do vs avoid” conclusion list tailored to your competition metric.

Retrieving Notebook summary.

Retrieving Notebook summary.

Retrieving Notebook summary.

Retrieving Notebook summary.

I have the notebook structure; next I’ll extract the actual model logic and metric handling (algorithms, blending, validation) so the final recommendations are evidence-based, not just titles.

Searched for regex `Hybrid|Brier|C-index|concordance|cox|Cox|RandomSurvivalForest|GBSA|LightGBM|lgb|blend|stack|stratified|isotonic|calibration|submission` (`**/state_art/*.ipynb`), 200 results

Read [](file:///Users/mellissahafis/Documents/WiDS_Global_Datathon_2026/state_art/0-97124-gbsa-rsf-lgb-survival-engine.ipynb)

Read [](file:///Users/mellissahafis/Documents/WiDS_Global_Datathon_2026/state_art/0-9716-tri-survival-stack-distancestratifiedblend.ipynb#1-1), lines 1 to 260

Read [](file:///Users/mellissahafis/Documents/WiDS_Global_Datathon_2026/state_art/0-9716-tri-survival-stack-distancestratifiedblend.ipynb#260-260), lines 260 to 620

Read [](file:///Users/mellissahafis/Documents/WiDS_Global_Datathon_2026/state_art/0-9716-tri-survival-stack-distancestratifiedblend.ipynb#620-620), lines 620 to 980

Read [](file:///Users/mellissahafis/Documents/WiDS_Global_Datathon_2026/state_art/0-9716-tri-survival-stack-distancestratifiedblend.ipynb#980-980), lines 980 to 1350

I’ve extracted the full logic of the first two notebooks; next I’ll review the ensemble notebook and the EDA notebook to identify which ideas are genuinely transferable versus leaderboard-overfit heuristics.

Read [](file:///Users/mellissahafis/Documents/WiDS_Global_Datathon_2026/state_art/wids-2026-ensemble-of-solutions-h-blend.ipynb#1-1), lines 1 to 420

Read [](file:///Users/mellissahafis/Documents/WiDS_Global_Datathon_2026/state_art/wids-2026-ensemble-of-solutions-h-blend.ipynb#420-420), lines 420 to 753

Read [](file:///Users/mellissahafis/Documents/WiDS_Global_Datathon_2026/state_art/wids2026-edanalysis.ipynb)

Review completed for all 4 notebooks, one by one, with metric-focused conclusions.

**Notebook 1 Review**
0-97124-gbsa-rsf-lgb-survival-engine.ipynb

What it does well:
- Strong survival backbone with model diversity: GBSA + CoxPH + zone-split LGB ([imports and architecture](state_art/0-97124-gbsa-rsf-lgb-survival-engine.ipynb#L22), 0-97124-gbsa-rsf-lgb-survival-engine.ipynb, 0-97124-gbsa-rsf-lgb-survival-engine.ipynb, 0-97124-gbsa-rsf-lgb-survival-engine.ipynb).
- Proper censor-aware binary targets for horizon models via unknown masking ([target function](state_art/0-97124-gbsa-rsf-lgb-survival-engine.ipynb#L174)).
- Uses IPCW weighting for LGB horizon classifiers ([IPCW function](state_art/0-97124-gbsa-rsf-lgb-survival-engine.ipynb#L179), 0-97124-gbsa-rsf-lgb-survival-engine.ipynb).
- Enforces monotonicity before submission (0-97124-gbsa-rsf-lgb-survival-engine.ipynb, 0-97124-gbsa-rsf-lgb-survival-engine.ipynb).

Risks / weaknesses:
- Hardcoded zone thresholds and blend weights are leaderboard-tuned heuristics, not re-estimated from local validation (0-97124-gbsa-rsf-lgb-survival-engine.ipynb).
- Uses fixed 72h=1.0 for all rows ([72h constant](state_art/0-97124-gbsa-rsf-lgb-survival-engine.ipynb#L690)). This can work with current censoring behavior, but is brittle if evaluation distribution shifts.
- Some feature engineering drops potentially useful variables globally without ablation logs ([drop cols](state_art/0-97124-gbsa-rsf-lgb-survival-engine.ipynb#L154)).

**Notebook 2 Review**
0-9716-tri-survival-stack-distancestratifiedblend.ipynb

What it does well:
- Most complete metric-aware notebook: explicitly codes competition-style hybrid score and weighted Brier (24/48/72) ([metric cell](state_art/0-9716-tri-survival-stack-distancestratifiedblend.ipynb#L632)).
- Best model diversity among all notebooks: GBSA + CoxPH + RSF + zone-split LGB ([pipeline description](state_art/0-9716-tri-survival-stack-distancestratifiedblend.ipynb#L30), 0-9716-tri-survival-stack-distancestratifiedblend.ipynb).
- Good engineering discipline: near/far separation, feature sets per zone, and repeated CV-bagging with many seeds ([feature engineering](state_art/0-9716-tri-survival-stack-distancestratifiedblend.ipynb#L510), 0-9716-tri-survival-stack-distancestratifiedblend.ipynb).
- Includes diagnostic timing model and intentionally sets its weight to 0 when unstable ([timing diagnostics](state_art/0-9716-tri-survival-stack-distancestratifiedblend.ipynb#L969), 0-9716-tri-survival-stack-distancestratifiedblend.ipynb).

Risks / weaknesses:
- Still uses 72h=1.0 and heavy public-LB-driven choices ([72h treatment and lock decisions](state_art/0-9716-tri-survival-stack-distancestratifiedblend.ipynb#L96), 0-9716-tri-survival-stack-distancestratifiedblend.ipynb).
- Very high complexity and large seed sweeps for tiny data (221 rows), which can hide overfit behind averaging.
- OOF weight search is performed; even though constrained to far-zone later, this remains easy to overfit without strict external validation ([search block](state_art/0-9716-tri-survival-stack-distancestratifiedblend.ipynb#L1298)).

**Notebook 3 Review**
wids-2026-ensemble-of-solutions-h-blend.ipynb

What it does well:
- Pragmatic late-stage blending of multiple strong submissions ([source models and weights](state_art/wids-2026-ensemble-of-solutions-h-blend.ipynb#L23), wids-2026-ensemble-of-solutions-h-blend.ipynb).
- Per-horizon blending workflow is explicit (12h/24h/48h/72h separately) ([12h block](state_art/wids-2026-ensemble-of-solutions-h-blend.ipynb#L601), wids-2026-ensemble-of-solutions-h-blend.ipynb, wids-2026-ensemble-of-solutions-h-blend.ipynb, wids-2026-ensemble-of-solutions-h-blend.ipynb).

Risks / weaknesses:
- It is mostly a ranking/position-based blending heuristic engine, not metric-grounded survival modeling ([h_blend internals](state_art/wids-2026-ensemble-of-solutions-h-blend.ipynb#L170)).
- Depends on precomputed external submissions; not reproducible as a standalone modeling pipeline.
- No direct local computation of competition hybrid metric to justify blend changes.

**Notebook 4 Review**
wids2026-edanalysis.ipynb

What it does well:
- Clean exploratory walkthrough of targets and feature groups (wids2026-edanalysis.ipynb, wids2026-edanalysis.ipynb, wids2026-edanalysis.ipynb).
- Useful initial feature correlation scan ([correlation matrix](state_art/wids2026-edanalysis.ipynb#L481), wids2026-edanalysis.ipynb).

Risks / weaknesses:
- Entirely plot-centric, not text-centric; hard for AI-readable EDA reuse.
- Not explicitly tied to competition metric behavior (censor-aware Brier and hybrid tradeoff not analyzed).
- A few inplace transformations are ad hoc and not justified (e.g., manual shifts/logs) (wids2026-edanalysis.ipynb, wids2026-edanalysis.ipynb).

**Final Conclusions: What is good to do**
- Use multi-model survival diversity: GBSA + CoxPH + RSF/LGB can help when data is small.
- Keep censor-aware labeling and IPCW weighting for horizon classifiers.
- Evaluate locally with competition-faithful hybrid metric every time.
- Keep near/far stratification as a feature/modeling concept, but re-validate thresholds.
- Enforce monotonicity at the end of prediction pipeline.
- Prefer diagnostics-driven inclusion of extra components (like timing model), and turn off when unstable.

**Final Conclusions: What not to do**
- Do not rely only on public leaderboard heuristics as if they are universally valid.
- Do not assume fixed hardcoded blend weights are robust across splits/distributions.
- Do not over-index on giant seed sweeps without strict validation controls; 221 rows can still overfit through repeated tuning.
- Do not keep EDA only as plots if your downstream consumer is AI; generate text tables and numeric summaries.
- Do not use heuristic blend engines alone (rank-order blending) without metric-grounded validation.

If you want, next I can produce a single consolidated “best-practice notebook blueprint” from these 4, with only the robust parts kept and the risky parts removed.