# WiDS Global Datathon 2026 — Competition Plan
**Wildfire Survival Analysis: Predicting Evacuation Zone Threats**

> Start: March 22, 2026 | Entry Deadline: April 24, 2026 | Final Submission: May 1, 2026
> Time remaining: ~6 weeks

---

## Executive Summary

This competition asks us to predict the **probability** that a wildfire will come within 5 km of an evacuation zone centroid within **12, 24, 48, and 72 hours** of ignition — using only the first 5 hours of observed data. It is framed as **right-censored survival analysis** on a small dataset (221 train rows). The evaluation metric is a hybrid of C-index (ranking) and Weighted Brier Score (calibration), with calibration weighted 70%.

The core challenge: **small data + censoring + calibration requirements** means simple ML won't win. Survival-aware methods and careful probability estimation are essential.

---

## Dataset at a Glance

| Split | Rows | Events (hit) | Censored |
|-------|------|-------------|----------|
| Train | 221  | 69 (31%)    | 152 (69%) |
| Test  | 95   | Unknown     | Unknown   |
| **Total** | **316** | — | — |

**Features (34 total)** across 5 categories:
- **Temporal coverage** (3): num_perimeters, time span, resolution flag
- **Growth dynamics** (11): area, radial growth, rates, log transforms
- **Centroid kinematics** (5): displacement, speed, bearing (sin/cos)
- **Distance to evac zones** (9): min distance, std, change, slope, closing speed, acceleration, R²
- **Directionality** (4): alignment cos/abs, cross-track, along-track speed
- **Temporal metadata** (3): start hour, day of week, month

**Target:** `time_to_hit_hours` (survival time) + `event` (1 = hit, 0 = censored)

---

## Evaluation Metric Deep Dive

```
Hybrid Score = 0.3 × C-index + 0.7 × (1 − Weighted Brier Score)
```

**Weighted Brier Score breakdown:**
```
WBS = 0.3 × Brier@24h + 0.4 × Brier@48h + 0.3 × Brier@72h
```
> Note: 12h appears in the submission but is NOT in the evaluation metric — it still must be monotone with 24h.

**Censoring-aware Brier computation:**
- Fires that hit before horizon H → true label = 1
- Fires censored after H → true label = 0
- Fires censored before H → **excluded** from that horizon's Brier

**Implications for modeling:**
1. Calibration matters far more than ranking (70% weight)
2. 48h predictions are the most important single output (40% of WBS)
3. Survival models that naturally produce calibrated probabilities are preferred over classifiers
4. Probabilities must be monotone: `prob_12h ≤ prob_24h ≤ prob_48h ≤ prob_72h`

---

## Competition Planning — Week by Week

### ✅ Week 1 (Mar 22–28): EDA & Baseline
*Goal: Understand the data deeply, establish a working submission pipeline*

**Tasks:**
- [ ] Download data from Kaggle (`train.csv`, `test.csv`, `sample_submission.csv`, `metaData.csv`)
- [ ] Exploratory Data Analysis
  - Distribution of `time_to_hit_hours` and `event`
  - Kaplan-Meier survival curves (overall, by quartile of key features)
  - Correlation matrix of features
  - Feature distributions: check for skewness, outliers, missing values
  - Temporal patterns: month, day of week, hour effects
  - Class imbalance: 31% event rate
- [ ] Baseline models (simple, just to get a valid submission):
  - Constant probability baseline (e.g., `prob_Xh = 0.31` for all horizons)
  - Cox Proportional Hazards model (lifelines library)
  - Convert to probabilities at 12h, 24h, 48h, 72h via survival function
- [ ] Set up local validation framework:
  - Implement C-index calculation (use `lifelines.statistics` or `sksurv`)
  - Implement censoring-aware Brier score at each horizon
  - Implement full hybrid score
  - Use stratified cross-validation respecting censoring (5-fold)

**Key libraries to install:**
```bash
pip install lifelines scikit-survival pandas numpy scikit-learn matplotlib seaborn
```

**Deliverables:** First valid Kaggle submission + local CV score baseline

---

### 🔬 Week 2 (Mar 29 – Apr 4): Survival Modeling Core
*Goal: Build survival-specific models and understand their calibration*

**Models to explore:**

| Model | Library | Notes |
|-------|---------|-------|
| Cox PH | lifelines | Interpretable baseline |
| Regularized Cox (Lasso/Ridge) | lifelines | Handles collinearity |
| Weibull AFT | lifelines | Parametric, good calibration |
| Log-Normal AFT | lifelines | Alternative parametric |
| Random Survival Forest | scikit-survival | Handles non-linearities |
| Gradient Boosting Survival (GBSA) | scikit-survival | Often best ranking |

**Calibration focus:**
- Plot calibration curves at each horizon
- Use Platt scaling / isotonic regression on CV OOF predictions if needed
- Ensure monotonicity post-processing is clean (cumulative max trick)

**Feature engineering ideas:**
- `dist_min_ci_0_5h / closing_speed_m_per_h` → estimated time to reach evac zone
- `area_growth_rate_ha_per_h × alignment_abs` → directed threat index
- Interaction: `closing_speed × alignment_cos` → directional threat
- Flag: `dist_min_ci_0_5h < 5000` → already very close
- Log transform distances and rates (many will be skewed)

**Deliverables:** 3–5 models evaluated on local CV, feature importance analysis

---

### 🛠️ Week 3 (Apr 5–11): Feature Engineering & Model Tuning
*Goal: Push model quality through better features and hyperparameter search*

**Advanced feature ideas:**
- Ratio features: `projected_advance_m / dist_min_ci_0_5h` (fraction of gap closed)
- Acceleration signals: `dist_accel_m_per_h2` sign and magnitude
- Time-of-year risk proxies: fire season indicators (summer months)
- Quality flags: `low_temporal_resolution_0_5h` interaction terms
- Composite spread score: weighted combination of growth + alignment + closing speed

**Hyperparameter tuning:**
- Random Survival Forest: `n_estimators`, `max_features`, `min_samples_leaf`
- GBSA: learning rate, depth, number of trees, subsample
- Use Optuna or RandomizedSearchCV with survival-aware CV

**Regularization for small data:**
- L1/L2 regularization on Cox
- Feature selection via permutation importance
- Keep feature set lean (< 20 features) to avoid overfitting on 221 rows

**Deliverables:** Best single model, feature set locked for ensembling

---

### 🎯 Week 4 (Apr 12–18): Ensembling & Calibration
*Goal: Ensemble diverse models, ensure calibration is strong*

**Ensembling strategies:**
- Simple average of survival probabilities across models
- Weighted average (weights tuned on CV hybrid score)
- Stacking: use OOF survival probabilities as meta-features for a calibrated regressor

**Calibration techniques:**
- **Isotonic regression** on OOF predictions at each horizon (risk: overfitting on small data)
- **Beta calibration** (more flexible than Platt)
- **IPCW-aware calibration** (inverse probability of censoring weighting)
- Compare calibrated vs uncalibrated on held-out CV fold

**Monotonicity enforcement:**
```python
# Post-processing: cumulative max to enforce prob_12h <= prob_24h <= prob_48h <= prob_72h
probs = np.maximum.accumulate(probs, axis=1)
```

**Validation sanity checks:**
- Are probabilities in [0, 1]? ✓
- Are they monotone row-wise? ✓
- Do event_ids match test set exactly? ✓
- No missing/extra/duplicate IDs? ✓

**Deliverables:** Ensemble model with better hybrid score than any individual model

---

### 🚀 Week 5 (Apr 19–24): Competition Strategy & Submission Polish
*Goal: Final model selection, entry deadline (Apr 24)*

**Model selection:**
- Compare top 3 ensembles on local CV
- Prioritize Brier score improvement (70% weight) over C-index
- Consider uncertainty: prefer stable models over marginally better but noisy ones

**Submission strategy:**
- Submit multiple candidates before April 24 entry deadline
- Use public leaderboard to validate local CV alignment
- Keep at least 2 final submission slots for May 1

**Risk management:**
- Save all model artifacts (weights, transformers, seeds)
- Document every experiment in a notebook or MLflow
- Lock a "safe" submission that passes all schema checks

**Deliverables:** At least 3 valid Kaggle submissions, entry form accepted

---

### 🏁 Week 6 (Apr 25 – May 1): Final Stretch
*Goal: Final optimizations, submit best by May 1*

**Last-mile improvements:**
- Retrain best model on full train set (not just CV folds)
- Final calibration check with leave-one-out or bootstrap
- Try any remaining ideas: neural survival models (DeepHit, DeepSurv) if time allows
- Hyperparameter fine-tuning with additional Kaggle submissions

**Final submission checklist:**
- [ ] Schema: `event_id, prob_12h, prob_24h, prob_48h, prob_72h`
- [ ] 95 rows exactly, IDs match test set
- [ ] All probabilities in [0, 1]
- [ ] Monotone row-wise: `prob_12h ≤ prob_24h ≤ prob_48h ≤ prob_72h`
- [ ] No NaN, no inf values

---

## Technical Architecture

### Recommended Model Stack

```
Tier 1 — Survival Models (primary):
├── Cox PH (regularized)         → good C-index
├── Weibull AFT                  → good calibration
├── Random Survival Forest       → captures non-linearities
└── Gradient Boosting Survival   → strong all-around

Tier 2 — Probability Calibration:
├── IPCW-weighted isotonic regression
└── Platt scaling per horizon

Tier 3 — Ensemble:
└── Weighted average (weights tuned on CV hybrid score)
```

### Validation Framework

```python
# 5-fold stratified CV (stratify on event indicator)
# For each fold:
#   1. Fit model on train folds
#   2. Predict survival probabilities at 12h, 24h, 48h, 72h on val fold
#   3. Enforce monotonicity
#   4. Compute C-index on val fold
#   5. Compute IPCW Brier at 24h, 48h, 72h
#   6. Compute weighted Brier: 0.3×@24h + 0.4×@48h + 0.3×@72h
#   7. Compute hybrid: 0.3×C-index + 0.7×(1 - WBS)
# Average across folds → local CV score
```

---

## Key Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Overfitting (221 rows only) | High | Strong regularization, lean feature sets, bootstrap validation |
| Poor calibration | High | Use parametric survival models (AFT), calibration post-processing |
| Leaking test-time info | Medium | Features strictly from first 5h — audit carefully |
| Monotonicity violations | Low | Post-process with cumulative max |
| Schema mismatch on submission | Low | Validate before every Kaggle submission |
| Public LB divergence from local CV | Medium | Use 5-fold CV religiously, report both scores |

---

## Resources & References

**Libraries:**
- `lifelines` — Cox PH, AFT models, Kaplan-Meier, C-index
- `scikit-survival` — Random Survival Forest, GBSA, IPCW Brier
- `optuna` — Hyperparameter optimization

**Key reading:**
- Brier Score for survival data (Graf et al., 1999)
- IPCW (Inverse Probability of Censoring Weighting) for evaluation
- Random Survival Forests (Ishwaran et al., 2008)
- DeepHit / DeepSurv (if exploring neural approaches in Week 6)

**Kaggle assets:**
- Competition: https://www.kaggle.com/competitions/WiDSWorldWide_GlobalDathon26
- Data files: `train.csv`, `test.csv`, `sample_submission.csv`, `metaData.csv`

---

## Success Criteria

| Milestone | Target |
|-----------|--------|
| Baseline hybrid score | > 0.55 |
| Week 2 single best model | > 0.62 |
| Week 4 ensemble | > 0.68 |
| Final submission | Competitive top 20% |

> These targets are estimates — calibrate after seeing the public leaderboard.

---

*Plan created: March 22, 2026 | Competition closes: May 1, 2026*