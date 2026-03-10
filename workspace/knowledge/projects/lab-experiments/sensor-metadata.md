# Sensor Metadata — OpenClaw-Lab

## Known Devices

dev-001-labA  
• Location: Lab A – Shelf 3, environmental monitoring station  
• Type: multi-sensor node  
• Sensors:

- temperature     (°C)     expected interval: 10–20 s
- humidity        (%)      expected interval: 12–25 s
- pressure        (hPa)    occasional
• Typical operating hours: 08:00–20:00 UTC
• Last seen: (updated by monitor)

dev-002-labB  
• Location: Lab B – Chemical bench  
• Type: chemical assay node  
• Sensors:

- pH              (pH)      15–40 s
- conductivity    (mS/cm)   20–60 s
• Notes: sensitive to temperature changes

## Expected Message Format (all devices)

Minimum required fields:

- device_id: string
- sensor_type: string (temperature | humidity | pH | conductivity | pressure)
- value: number
- unit: string
- ts: ISO 8601 string

Optional / recommended:

- batch_seq: integer (for grouping)
- metadata: object (calibration, location tags, etc.)

Example:
{
  "device_id": "dev-001-labA",
  "sensor_type": "temperature",
  "value": 24.7,
  "unit": "°C",
  "ts": "2026-03-09T14:35:22.781Z"
}
