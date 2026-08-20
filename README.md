# WiDS Global Datathon 2026

## Overview

This repository contains code and data for the WiDS Global Datathon 2026 challenge: predicting the probability that a wildfire will threaten an evacuation zone within 12, 24, 48, and 72 hours, using only the first five hours of incident data.

- Kaggle Competition: [WiDSWorldWide_GlobalDathon26](https://www.kaggle.com/competitions/WiDSWorldWide_GlobalDathon26/overview)
- Competition closes: May 2, 2026.
- **Detailed solution writeup**: https://www.kaggle.com/competitions/WiDSWorldWide_GlobalDathon26/writeups/wids-global-datathon-2026-solution-kagglettes

## Problem Statement

Emergency managers must decide which communities to warn, when to warn them, and where to position scarce resources, often with incomplete information. The challenge is to build survival models that predict the probability a wildfire will threaten an evacuation zone within actionable time windows (12h, 24h, 48h, 72h), using only the earliest signals (first 5 hours after ignition).

## Data Description

- **Wildfire Events:** 316 events with early-stage perimeter observations and confirmed outcomes.
- **Features:** Computed strictly from the first five hours after initial perimeter detection, representing early spread dynamics and spatial relationships to evacuation zones.
- **Labels:** Right-censored survival data. If a fire reaches an evacuation zone within 72 hours, `event=1` and `time_to_hit_hours` is observed. Otherwise, `event=0` and `time_to_hit_hours` is censored.

### Files

- train.csv: 221 rows, features + targets (`event_id`, 34 features, `time_to_hit_hours`, `event`)
- test.csv: 95 rows, features only
- sample_submission.csv: Example submission format
- metaData.csv: Column definitions and data dictionary

### Features

- **Temporal Coverage:** Number of perimeters, time span, resolution flag
- **Growth:** Initial area, absolute/relative growth, growth rate, log transforms
- **Centroid Kinematics:** Displacement, speed, spread bearing (deg/sin/cos)
- **Distance to Evac Zone:** Minimum/standard deviation/change/slope/closing speed/advance/acceleration/fit R²
- **Directionality:** Alignment, cross-track, along-track speed
- **Temporal Metadata:** Start hour, day of week, month

See metaData.csv for full column definitions.

### Submission Format

CSV with columns: `event_id, prob_12h, prob_24h, prob_48h, prob_72h`
- Probabilities must be in [0, 1]
- Monotonicity enforced: `prob_12h <= prob_24h <= prob_48h <= prob_72h`
- IDs must match the test set exactly

## Evaluation

- **Hybrid Score:** `0.3 x C-index + 0.7 x (1 - Weighted Brier Score)`
  - C-index: Ranks fires by urgency
  - Weighted Brier Score: Calibration at 24h, 48h, 72h (48h weighted highest)

## Real-World Context

The dataset captures wildfire perimeter dynamics and their spatial relationship to evacuation zones. The goal is to support real-world decisions for emergency responders, balancing urgency and calibrated risk estimates.

## Prizes

- Top 5 teams: $3,000 Kaggle cash prize each
- Student, high school, and first-timer teams: $2,500 Kaggle cash prize each

## Acknowledgements

- WiDS Global Datathon Team
- Watch Duty: Real-time emergency alerts provider
- Contributors: Bryan Muñoz, María Cruz, Valentina Torres da Silva, Yao Yan, Gabe Schine, WiDS Worldwide, and WatchDuty

## Citation

Bryan Muñoz, María Cruz, Valentina Torres da Silva, Yao Yan, Gabe Schine, WiDS Worldwide, and WatchDuty. WiDS Global Datathon 2026. [Kaggle Competition](https://kaggle.com/competitions/WiDSWorldWide_GlobalDathon26), 2026.
