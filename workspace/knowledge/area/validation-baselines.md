# Validation Baselines — OpenClaw-Lab

Used by: analyst agent

## Strict Operating Ranges (must never be committed outside these)

temperature     15.0 – 35.0 °C     (biological assays)
humidity        30 – 70 %          (most lab environments)
pH              6.0 – 8.0          (neutral to slightly acidic/basic)
conductivity    0.1 – 12.0 mS/cm   (aqueous solutions)
pressure        950 – 1050 hPa     (ambient lab)

## Anomaly Thresholds

Temperature:

- max delta in 60 s:          3.0 °C
- max z-score (from baseline): 2.8

Humidity:

- max delta in 60 s:          12 %
- inverse correlation with temp expected (coeff < -0.6)

pH:

- max delta in 5 min:         0.9
- should remain stable unless experiment explicitly changes it

Conductivity:

- spikes > 30% without pH change → suspicious

## Expected Correlations (negative = inverse)

temperature ↔ humidity      expected: -0.65 to -0.90
temperature ↔ conductivity  expected: +0.40 to +0.75 (warmer = higher conductivity)
pH ↔ conductivity           usually weak / context dependent

## Rejection Criteria (immediate reject)

- value NaN / null / non-numeric when numeric expected
- timestamp older than 15 minutes (stale data)
- device_id unknown (not in sensor-metadata.md)
- missing required fields after first message from device
