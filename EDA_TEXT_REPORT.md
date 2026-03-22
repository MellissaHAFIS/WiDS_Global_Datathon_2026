# Text-Only EDA Report (WiDS Global Datathon 2026)

## 1. Competition-Aware Context
- Task: predict cumulative hit probabilities by 12h/24h/48h/72h using only first-5-hour features.
- Evaluation: Hybrid Score = 0.3 x C-index + 0.7 x (1 - Weighted Brier).
- Weighted Brier = 0.3 x Brier@24h + 0.4 x Brier@48h + 0.3 x Brier@72h (censor-aware).

## 2. Dataset Structure
- Train shape: 221 rows x 37 columns
- Test shape: 95 rows x 35 columns
- Features available for modeling: 34
- Metadata rows (column dictionary): 37

## 3. Missingness and Duplicates
- Missing values in train: 0
- Missing values in test: 0
- Duplicate event_id in train: 0
- Duplicate event_id in test: 0

## 4. Target and Censoring Profile
- Event counts: {0: 152, 1: 69}
- Event rate (hit within 72h): 0.3122
- Censoring rate: 0.6878
- time_to_hit_hours range: 0.0012 to 66.9945
- Hit-time quantiles (event=1): q10=0.40, q25=0.89, q50=3.53, q75=14.32, q90=23.15
- Censor-time quantiles (event=0): q10=18.72, q25=38.18, q50=61.17, q75=65.11, q90=66.43

## 5. Censor-Aware Horizon Labeling (for Brier Evaluation)
- Horizon 12h: included=215, excluded=6, positives=49, prevalence=0.2279
- Horizon 24h: included=196, excluded=25, positives=63, prevalence=0.3214
- Horizon 48h: included=166, excluded=55, positives=66, prevalence=0.3976
- Horizon 72h: included=69, excluded=152, positives=69, prevalence=1.0000

## 6. Metric-Aware Baseline (Constant Risk)
- Brier@24h (constant p=0.3214): 0.218112
- Brier@48h (constant p=0.3976): 0.239512
- Brier@72h (constant p=1.0000): 0.000000
- Weighted Brier baseline: 0.161239
- C-index baseline (constant risk): 0.500000
- Hybrid baseline (constant risk): 0.737133

## 7. Feature Behavior Snapshot (Text-Only)
- low_temporal_resolution_0_5h counts: {1: 161, 0: 60}
- num_perimeters_0_5h quantiles: q0.00=1.00, q0.25=1.00, q0.50=1.00, q0.75=2.00, q1.00=17.00
- Top 12 columns by zero fraction:
  - projected_advance_m: 0.9186
  - closing_speed_abs_m_per_h: 0.9186
  - closing_speed_m_per_h: 0.9186
  - dist_change_ci_0_5h: 0.9186
  - dist_fit_r2_0_5h: 0.9140
  - dist_std_ci_0_5h: 0.9140
  - log1p_growth: 0.8914
  - centroid_speed_m_per_h: 0.8869
  - radial_growth_rate_m_per_h: 0.8869
  - spread_bearing_sin: 0.8869
  - spread_bearing_deg: 0.8869
  - along_track_speed: 0.8869
- Event-vs-censored median comparison (event=1 minus event=0):
  - dist_min_ci_0_5h: median_event=2429.8016, median_censored=128842.0693, delta=-126412.2677
  - area_growth_abs_0_5h: median_event=0.0000, median_censored=0.0000, delta=0.0000
  - closing_speed_m_per_h: median_event=0.0000, median_censored=0.0000, delta=0.0000
  - centroid_speed_m_per_h: median_event=0.0000, median_censored=0.0000, delta=0.0000
  - alignment_abs: median_event=0.0717, median_censored=0.0000, delta=0.0717
  - num_perimeters_0_5h: median_event=2.0000, median_censored=1.0000, delta=1.0000

## 8. Interpretations
- The dataset is small and heavily censored; robust validation is critical to avoid overfitting.
- Because the hybrid metric weights Brier more than C-index, calibration quality (especially at 48h) must be a first-class objective.
- Censor-aware exclusions increase with horizon; 72h is not simply a larger 24h task, it is a differently observed target.
- Many dynamic features have high zero mass, indicating many incidents have minimal detected movement/growth in first 5h; models should handle spike-at-zero behavior.
- Event prevalence changes across horizons under censor-aware inclusion, so horizon-specific calibration is preferable to one-size-fits-all thresholds.
- Strong early directional/closing signals likely matter for ranking (C-index), while conservative probability shaping and post-calibration likely matter for Brier.

## 9. Modeling Implications (Metric-Constrained)
- Use survival-aware CV and avoid leakage from future-derived artifacts.
- Train with horizon-aware objectives or convert survival outputs to cumulative risks at 12/24/48/72h.
- Add calibration layer (isotonic/Platt/beta) per horizon, prioritizing 48h due to 0.4 weight.
- Enforce submission monotonicity: prob_12h <= prob_24h <= prob_48h <= prob_72h.
- Track validation with the same hybrid metric used by competition.