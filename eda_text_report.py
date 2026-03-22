from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def horizon_labels(df: pd.DataFrame, horizon: int) -> tuple[pd.Series, pd.Series]:
    """Return (label, include_mask) for censor-aware horizon classification.

    Rules based on competition definition for Brier score:
    - hit by horizon => 1
    - no hit by horizon (event happened later OR censored after horizon) => 0
    - censored before horizon => excluded
    """
    t = df["time_to_hit_hours"]
    e = df["event"]

    y = pd.Series(np.nan, index=df.index, dtype="float64")
    include = pd.Series(True, index=df.index)

    y[(e == 1) & (t <= horizon)] = 1.0
    y[(e == 1) & (t > horizon)] = 0.0
    y[(e == 0) & (t >= horizon)] = 0.0
    include[(e == 0) & (t < horizon)] = False

    return y, include


def brier_score(y_true: pd.Series, y_prob: pd.Series) -> float:
    return float(np.mean((y_prob - y_true) ** 2))


def concordance_index_like(event_time: np.ndarray, event_observed: np.ndarray, risk_score: np.ndarray) -> float:
    """Simple Harrell-style C-index implementation (higher risk => earlier event)."""
    n = len(event_time)
    concordant = 0.0
    comparable = 0.0

    for i in range(n):
        for j in range(i + 1, n):
            ti, tj = event_time[i], event_time[j]
            ei, ej = event_observed[i], event_observed[j]
            ri, rj = risk_score[i], risk_score[j]

            # pair comparable if one had an observed event before the other time
            if ei == 1 and ti < tj:
                comparable += 1
                if ri > rj:
                    concordant += 1
                elif ri == rj:
                    concordant += 0.5
            elif ej == 1 and tj < ti:
                comparable += 1
                if rj > ri:
                    concordant += 1
                elif ri == rj:
                    concordant += 0.5

    if comparable == 0:
        return 0.5
    return concordant / comparable


def main() -> None:
    root = Path(__file__).resolve().parent
    data_dir = root / "WiDSWorldWide_GlobalDathon26"

    train = pd.read_csv(data_dir / "train.csv")
    test = pd.read_csv(data_dir / "test.csv")
    metadata = pd.read_csv(data_dir / "metaData.csv")

    target_cols = ["time_to_hit_hours", "event"]
    feature_cols = [c for c in train.columns if c not in ["event_id", *target_cols]]

    lines: list[str] = []
    lines.append("# Text-Only EDA Report (WiDS Global Datathon 2026)")
    lines.append("")
    lines.append("## 1. Competition-Aware Context")
    lines.append("- Task: predict cumulative hit probabilities by 12h/24h/48h/72h using only first-5-hour features.")
    lines.append("- Evaluation: Hybrid Score = 0.3 x C-index + 0.7 x (1 - Weighted Brier).")
    lines.append("- Weighted Brier = 0.3 x Brier@24h + 0.4 x Brier@48h + 0.3 x Brier@72h (censor-aware).")
    lines.append("")

    lines.append("## 2. Dataset Structure")
    lines.append(f"- Train shape: {train.shape[0]} rows x {train.shape[1]} columns")
    lines.append(f"- Test shape: {test.shape[0]} rows x {test.shape[1]} columns")
    lines.append(f"- Features available for modeling: {len(feature_cols)}")
    lines.append(f"- Metadata rows (column dictionary): {metadata.shape[0]}")
    lines.append("")

    lines.append("## 3. Missingness and Duplicates")
    lines.append(f"- Missing values in train: {int(train.isna().sum().sum())}")
    lines.append(f"- Missing values in test: {int(test.isna().sum().sum())}")
    lines.append(f"- Duplicate event_id in train: {int(train['event_id'].duplicated().sum())}")
    lines.append(f"- Duplicate event_id in test: {int(test['event_id'].duplicated().sum())}")
    lines.append("")

    lines.append("## 4. Target and Censoring Profile")
    event_counts = train["event"].value_counts().to_dict()
    event_rate = train["event"].mean()
    lines.append(f"- Event counts: {event_counts}")
    lines.append(f"- Event rate (hit within 72h): {event_rate:.4f}")
    lines.append(f"- Censoring rate: {(1 - event_rate):.4f}")
    lines.append(
        f"- time_to_hit_hours range: {train['time_to_hit_hours'].min():.4f} to {train['time_to_hit_hours'].max():.4f}"
    )

    hit_times = train.loc[train["event"] == 1, "time_to_hit_hours"]
    cens_times = train.loc[train["event"] == 0, "time_to_hit_hours"]
    lines.append(
        "- Hit-time quantiles (event=1): "
        f"q10={hit_times.quantile(0.10):.2f}, q25={hit_times.quantile(0.25):.2f}, "
        f"q50={hit_times.quantile(0.50):.2f}, q75={hit_times.quantile(0.75):.2f}, q90={hit_times.quantile(0.90):.2f}"
    )
    lines.append(
        "- Censor-time quantiles (event=0): "
        f"q10={cens_times.quantile(0.10):.2f}, q25={cens_times.quantile(0.25):.2f}, "
        f"q50={cens_times.quantile(0.50):.2f}, q75={cens_times.quantile(0.75):.2f}, q90={cens_times.quantile(0.90):.2f}"
    )
    lines.append("")

    lines.append("## 5. Censor-Aware Horizon Labeling (for Brier Evaluation)")
    horizon_stats: dict[int, dict[str, float]] = {}
    for h in [12, 24, 48, 72]:
        y_h, include_h = horizon_labels(train, h)
        y_inc = y_h[include_h]
        included = int(include_h.sum())
        excluded = int((~include_h).sum())
        positives = int(y_inc.sum())
        prevalence = float(y_inc.mean())
        horizon_stats[h] = {
            "included": included,
            "excluded": excluded,
            "positives": positives,
            "prevalence": prevalence,
        }
        lines.append(
            f"- Horizon {h}h: included={included}, excluded={excluded}, positives={positives}, prevalence={prevalence:.4f}"
        )
    lines.append("")

    lines.append("## 6. Metric-Aware Baseline (Constant Risk)")
    # Constant prediction equal to horizon prevalence on included set (strong Brier baseline)
    brier_scores: dict[int, float] = {}
    for h in [24, 48, 72]:
        y_h, include_h = horizon_labels(train, h)
        y_inc = y_h[include_h]
        p_const = pd.Series(float(y_inc.mean()), index=y_inc.index)
        brier_scores[h] = brier_score(y_inc, p_const)
        lines.append(
            f"- Brier@{h}h (constant p={float(y_inc.mean()):.4f}): {brier_scores[h]:.6f}"
        )

    weighted_brier = 0.3 * brier_scores[24] + 0.4 * brier_scores[48] + 0.3 * brier_scores[72]

    # C-index baseline with constant risk scores => expected near 0.5
    cidx_const = concordance_index_like(
        event_time=train["time_to_hit_hours"].to_numpy(),
        event_observed=train["event"].to_numpy(),
        risk_score=np.full(len(train), 0.5),
    )

    hybrid_const = 0.3 * cidx_const + 0.7 * (1 - weighted_brier)
    lines.append(f"- Weighted Brier baseline: {weighted_brier:.6f}")
    lines.append(f"- C-index baseline (constant risk): {cidx_const:.6f}")
    lines.append(f"- Hybrid baseline (constant risk): {hybrid_const:.6f}")
    lines.append("")

    lines.append("## 7. Feature Behavior Snapshot (Text-Only)")
    low_temp = train["low_temporal_resolution_0_5h"].value_counts().to_dict()
    perim_q = train["num_perimeters_0_5h"].quantile([0, 0.25, 0.5, 0.75, 1.0]).to_dict()

    lines.append(f"- low_temporal_resolution_0_5h counts: {low_temp}")
    lines.append(
        "- num_perimeters_0_5h quantiles: "
        + ", ".join([f"q{k:.2f}={v:.2f}" for k, v in perim_q.items()])
    )

    numeric_cols = train.select_dtypes(include="number")
    zero_fraction = (numeric_cols == 0).mean().sort_values(ascending=False)
    lines.append("- Top 12 columns by zero fraction:")
    for col, frac in zero_fraction.head(12).items():
        lines.append(f"  - {col}: {frac:.4f}")

    # Simple event-vs-censored shift for selected features
    key_features = [
        "dist_min_ci_0_5h",
        "area_growth_abs_0_5h",
        "closing_speed_m_per_h",
        "centroid_speed_m_per_h",
        "alignment_abs",
        "num_perimeters_0_5h",
    ]
    lines.append("- Event-vs-censored median comparison (event=1 minus event=0):")
    for col in key_features:
        med_event = train.loc[train["event"] == 1, col].median()
        med_cens = train.loc[train["event"] == 0, col].median()
        lines.append(
            f"  - {col}: median_event={med_event:.4f}, median_censored={med_cens:.4f}, delta={med_event - med_cens:.4f}"
        )
    lines.append("")

    lines.append("## 8. Interpretations")
    lines.append("- The dataset is small and heavily censored; robust validation is critical to avoid overfitting.")
    lines.append("- Because the hybrid metric weights Brier more than C-index, calibration quality (especially at 48h) must be a first-class objective.")
    lines.append("- Censor-aware exclusions increase with horizon; 72h is not simply a larger 24h task, it is a differently observed target." )
    lines.append("- Many dynamic features have high zero mass, indicating many incidents have minimal detected movement/growth in first 5h; models should handle spike-at-zero behavior." )
    lines.append("- Event prevalence changes across horizons under censor-aware inclusion, so horizon-specific calibration is preferable to one-size-fits-all thresholds.")
    lines.append("- Strong early directional/closing signals likely matter for ranking (C-index), while conservative probability shaping and post-calibration likely matter for Brier.")
    lines.append("")

    lines.append("## 9. Modeling Implications (Metric-Constrained)")
    lines.append("- Use survival-aware CV and avoid leakage from future-derived artifacts.")
    lines.append("- Train with horizon-aware objectives or convert survival outputs to cumulative risks at 12/24/48/72h.")
    lines.append("- Add calibration layer (isotonic/Platt/beta) per horizon, prioritizing 48h due to 0.4 weight.")
    lines.append("- Enforce submission monotonicity: prob_12h <= prob_24h <= prob_48h <= prob_72h.")
    lines.append("- Track validation with the same hybrid metric used by competition.")

    out_path = root / "EDA_TEXT_REPORT.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved report: {out_path}")


if __name__ == "__main__":
    main()
