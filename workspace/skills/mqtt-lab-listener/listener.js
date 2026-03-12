const mqtt = require('mqtt');
const fs = require('fs');
const path = require('path');

const broker = 'mqtt://localhost:1883';
const clientId = 'openclaw-lab-listener-' + Math.random().toString(16).substr(2, 8);

const client = mqtt.connect(broker, { clientId });

const logFile = path.join(process.env.HOME || '/home/node', '.openclaw/workspace/daily', new Date().toISOString().split('T')[0] + '-mqtt.log');

client.on('connect', () => {
  console.log('[MQTT Listener] Connected to broker');
  client.subscribe('/lab/#', (err) => {
    if (!err) {
      console.log('[MQTT Listener] Subscribed to /lab/#');
    }
  });
});

client.on('message', (topic, message) => {
  const payloadStr = message.toString();
  console.log(`[Received] ${topic} → ${payloadStr}`);

  // Try to parse as JSON
  let payload;
  try {
    payload = JSON.parse(payloadStr);
  } catch (e) {
    console.log('[Error] Invalid JSON');
    return;
  }

  // Create handoff format for monitor
  const handoff = {
    type: 'raw-reading',
    timestamp: new Date().toISOString(),
    device: payload.device_id || payload.device || 'unknown',
    sensor: payload.sensor_type || payload.sensor || 'unknown',
    value: payload.value,
    unit: payload.unit,
    topic: topic,
    payload: payload
  };

  const handoffText = `Delegate to monitor:\n${JSON.stringify(handoff, null, 2)}`;

  console.log(handoffText);

  // Append to daily log
  const logLine = `[${new Date().toISOString()}] ${topic} → ${payloadStr}\n${handoffText}\n---\n`;
  fs.appendFile(logFile, logLine, (err) => {
    if (err) console.error('[Log Error]', err);
  });
});

client.on('error', (err) => {
  console.error('[MQTT Error]', err);
});
