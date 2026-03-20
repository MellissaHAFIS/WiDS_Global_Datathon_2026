Dataset Description
Data Limitations and Scarcity
This page describes the data, provided files, their formats, and the required submission format.

The dataset contains 316 wildfire events with verified early-stage perimeter observations and confirmed outcomes.

What you receive
Features computed strictly from the first five hours after initial perimeter detection. These represent early spread dynamics and spatial relationships to evacuation zones.

What you predict
Four probabilities for each fire. Each probability represents the likelihood that the fire comes within 5 km of an evacuation zone centroid by the horizon. prob_12h prob_24h prob_48h prob_72h

Understanding the labels
This is right-censored survival data. If a fire reaches an evacuation zone within 72 hours, event is 1 and time_to_hit_hours is observed. If a fire does not reach an evacuation zone within 72 hours, event is 0 and time_to_hit_hours is censored at the last available observation.

Why 316 fires and not 3,000
Most wildfires do not have both requirements needed for reliable labels. Early perimeter updates within the first five hours for feature extraction

Sufficient follow-up perimeter observations to confirm whether and when the threshold was reached. This constraint is structural, not accidental. It reflects how real incident data is collected. It also changes what good modeling looks like.

This competition therefore emphasizes:

Survival-aware modeling
Proper handling of censoring
Calibration over raw accuracy
Dataset Size
Train: 221 rows (69 hits, 152 censored)
Test: 95 rows
Total fires: 316
Submission Format
CSV with one row per event_id and four probability columns: event_id, prob_12h, prob_24h, prob_48h, prob_72h

Files
train.csv: Training data with features and targets
test.csv: Test data with features only (no targets)
sample_submission.csv: Example submission in the correct format
metaData.csv: Column definitions and data dictionary
Columns
Identifier
event_id: Anonymized fire event identifier (stable random remap, no temporal meaning)
Targets (train only)
time_to_hit_hours: Time from t0+5h until fire comes within 5 km of an evac zone (hours). For censored events (never hit within 72h), this is the last observed time within the window (<= 72).
event: Event indicator, 1 if fire hit within 72h, 0 if censored (never hit)
Temporal Coverage (first 5h only)
num_perimeters_0_5h: Number of perimeters within first 5 hours
dt_first_last_0_5h: Time span between first and last perimeter (hours)
low_temporal_resolution_0_5h: Flag, 1 if dt < 0.5h or only 1 perimeter, else 0
Growth Features
area_first_ha: Initial fire area at t0 (hectares)
area_growth_abs_0_5h: Absolute area growth (hectares)
area_growth_rel_0_5h: Relative area growth (fraction)
area_growth_rate_ha_per_h: Area growth rate (hectares/hour)
log1p_area_first: Log(1 + initial area)
log1p_growth: Log(1 + absolute growth)
log_area_ratio_0_5h: Log ratio of final to initial area
relative_growth_0_5h: Relative growth (same as area_growth_rel_0_5h)
radial_growth_m: Change in effective radius (meters)
radial_growth_rate_m_per_h: Rate of radial growth (meters/hour)
Centroid Kinematics
centroid_displacement_m: Total displacement of fire centroid (meters)
centroid_speed_m_per_h: Speed of centroid movement (meters/hour)
spread_bearing_deg: Bearing/direction of fire spread (degrees)
spread_bearing_sin: Sine of spread bearing (circular encoding)
spread_bearing_cos: Cosine of spread bearing (circular encoding)
Distance to Evacuation Zone Centroids
dist_min_ci_0_5h: Minimum distance to nearest evac zone centroid (meters)
dist_std_ci_0_5h: Standard deviation of distances
dist_change_ci_0_5h: Change in distance (d5 - d0, negative = closing)
dist_slope_ci_0_5h: Linear slope of distance vs time (meters/hour)
closing_speed_m_per_h: Speed at which fire is closing distance (m/hour, positive = closing)
closing_speed_abs_m_per_h: Absolute closing speed
projected_advance_m: Projected advance toward evac zone (d0 - d5)
dist_accel_m_per_h2: Acceleration in distance change (meters/hour^2)
dist_fit_r2_0_5h: R^2 of linear fit to distance vs time
Directionality
alignment_cos: Cosine of angle between fire motion and evac direction
alignment_abs: Absolute alignment between fire motion and evac direction (0-1, higher = more aligned)
cross_track_component: Sideways drift component
along_track_speed: Speed component toward/away from evac
Temporal Metadata
event_start_hour: Hour of day when fire started (0-23)
event_start_dayofweek: Day of week (0 = Monday, 6 = Sunday)
event_start_month: Month when fire started (1-12)
Acronyms and Short Terms
t0: Fire start time (first perimeter observation)
5h: Feature window length (first 5 hours after t0)
evac: Evacuation zone
ci: Centroid-to-centroid distance
Full column definitions are in metaData.csv.

File Descriptions
train.csv
221 rows. Contains:

event_id
34 features
time_to_hit_hours
event
test.csv
95 rows. Contains:

event_id
34 features (No targets)
sample_submission.csv
Correct schema example. 95 rows with placeholder probabilities.

metaData.csv
Data dictionary describing:

Column meanings
Feature categories
Target definitions