# Long-term memory — Analyst

## Device baselines & patterns
• dev-001-labA
  - Temp typical range: 20.5–28.2 °C (95% CI from first week)
  - Humidity-temp correlation: -0.84 (strong inverse, as expected)
  - Avg message interval: 14.7 s

• dev-002-labB (chemical)
  - pH typical: 6.8–7.4
  - Conductivity spikes often follow pH drops >0.8

## Common anomalies observed
• pH calibration drift: +0.3–0.5 after 48 h idle
• Temp overshoot during equipment startup (first 3 readings)

## ML notes (if Torch enabled)
• Autoencoder baseline MSE: 0.042 (trained on first 500 clean points)
• Current anomaly threshold: reconstruction error > 0.18