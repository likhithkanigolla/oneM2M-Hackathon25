-- Schema-accurate seed file for smartroom (Postgres)
-- WARNING: Intended for development. Review TRUNCATEs before running in any non-dev DB.

BEGIN;

-- Truncate dependent tables first to avoid FK conflicts
TRUNCATE TABLE sensor_data, sensor_alerts, decision_logs, devices, sensors, slos, scenarios, agents, users, rooms RESTART IDENTITY CASCADE;

-- Rooms
INSERT INTO rooms (name, gsi, aq, temp, occupancy, position) VALUES
('Conference Room A', 0.84, 85, 24.0, 5, '{"x":100,"y":100}'),
('Conference Room B', 0.76, 78, 26.0, 3, '{"x":350,"y":100}'),
('Office Space', 0.92, 92, 23.0, 8, '{"x":100,"y":300}'),
('Lab Room', 0.68, 72, 27.0, 2, '{"x":350,"y":300}');

-- Devices (associate with rooms by room_id)
INSERT INTO devices (name, type, status, room_id, services) VALUES
('AC Unit A1', 'HVAC', 'ON', 1, '{"capabilities": ["cool","heat"], "controlled_by": "claude"}'),
('Ceiling Light A1', 'Lighting', 'ON', 1, '{"capabilities": ["dim"], "controlled_by": "gemini"}'),
('Exhaust Fan A1', 'AirFlow', 'ON', 1, '{"capabilities": ["ventilate"], "controlled_by": "gemini"}'),
('Security Camera A1', 'Security', 'ON', 1, '{"capabilities": ["stream","record"], "controlled_by": "gpt"}'),
('AC Unit B1', 'HVAC', 'OFF', 2, '{"capabilities": ["cool","heat"], "controlled_by": "claude"}'),
('Ceiling Light B1', 'Lighting', 'ON', 2, '{"capabilities": ["dim"], "controlled_by": "gemini"}'),
('Office HVAC', 'HVAC', 'ON', 3, '{"capabilities": ["cool","heat"], "controlled_by": "claude"}'),
('Lab Vent', 'AirFlow', 'ON', 4, '{"capabilities": ["ventilate"], "controlled_by": "gemini"}');

-- Sensors
INSERT INTO sensors (id, name, sensor_type, room_id, location, unit, min_value, max_value, accuracy, active, sensor_metadata) VALUES
('temp_r1', 'Temp Sensor A1', 'temperature', 1, 'ceiling', '°C', -10, 50, 0.5, true, '{"manufacturer":"SensCorp","model":"T1000"}'),
('co2_r1', 'CO2 Sensor A1', 'co2', 1, 'wall', 'ppm', 0, 5000, 25.0, true, '{"manufacturer":"AirSense","model":"C200"}'),
('occ_r1', 'Occupancy Sensor A1', 'occupancy', 1, 'door', 'people', 0, 100, 1.0, true, '{"type":"camera_counting"}'),
('light_r1', 'Light Sensor A1', 'light_level', 1, 'ceiling', 'lux', 0, 10000, 2.0, true, '{"range":"0-10000"}'),
('temp_r2', 'Temp Sensor B1', 'temperature', 2, 'ceiling', '°C', -10, 50, 0.5, true, NULL),
('co2_r3', 'CO2 Sensor Office', 'co2', 3, 'wall', 'ppm', 0, 5000, 25.0, true, NULL);

-- Recent sensor readings (sensor_data)
INSERT INTO sensor_data (sensor_id, timestamp, value, quality, battery_level, signal_strength, reading_metadata) VALUES
('temp_r1', now() - interval '5 minutes', 24.1, 'good', 98.0, -60.0, '{"note":"stable"}'),
('co2_r1', now() - interval '5 minutes', 720.0, 'good', NULL, -55.0, NULL),
('occ_r1', now() - interval '2 minutes', 5.0, 'good', NULL, -50.0, NULL),
('light_r1', now() - interval '5 minutes', 350.0, 'good', NULL, -60.0, NULL),
('temp_r2', now() - interval '10 minutes', 26.2, 'good', 95.0, -62.0, NULL),
('co2_r3', now() - interval '7 minutes', 890.0, 'good', NULL, -58.0, NULL);

-- Agents
INSERT INTO agents (id, name, goal, rag_sources, active, endpoint, weight) VALUES
('gemini', 'Gemini AI', 'Optimize comfort and air quality', '["sensor","comfort"]', true, NULL, 0.40),
('claude', 'Claude AI', 'Energy efficiency optimization', '["energy","weather"]', true, NULL, 0.35),
('gpt', 'GPT AI', 'Security and reliability', '["security","reliability"]', true, NULL, 0.25);

-- SLOs (system-defined)
INSERT INTO slos (name, description, target_value, metric, weight, active, config) VALUES
('Temperature Comfort', 'Keep temperature between 22-24°C when occupied', 23.0, 'temperature', 0.25, true, '{"min_temp":22, "max_temp":24}'),
('CO2 Safety', 'Keep CO2 below 800 ppm for healthy air', 800.0, 'co2', 0.20, true, '{"max_co2":800}'),
('Energy Efficiency', 'Minimize energy usage while occupied', 0.8, 'energy_efficiency', 0.15, true, '{"target_efficiency":0.8}'),
('Security Coverage', 'Maintain at least one light on when area is unoccupied for surveillance', 1.0, 'security_lighting', 0.10, true, '{"min_lights":1}'),
('Humidity Control', 'Keep relative humidity between 40-60%', 50.0, 'humidity', 0.10, true, '{"min":40, "max":60}');

-- Scenarios
INSERT INTO scenarios (name, description, active, config, priority, trigger, impact) VALUES
('Meeting Priority', 'Prioritize comfort during meetings', false, '{"priority":"comfort","energy_reduction":0.1}', 'High', 'Meeting schedule detected', 'Increase comfort'),
('After Hours Energy Save', 'Aggressive energy savings after hours', true, '{"reduce_hvac": true, "reduce_lighting": true}', 'Critical', 'Time outside working hours', 'Energy -30%');

-- Users (passwords are bcrypt hashes generated locally)
INSERT INTO users (username, password, email, full_name, role, is_active, assigned_rooms) VALUES
('admin', '$2b$12$BP1.nj.OgQDXpI8ihwz8AurUcj/1pEaKdrkPWSq5zy90Le5YAca3.', 'admin@smartroom.ai', 'System Administrator', 'admin', true, '[1,2,3,4]'),
('operator_a', '$2b$12$iBckOBzcyHj57ZqAnHvzUu/1F1v5PqUli2kqxIBNTq02t41m.NKTK', 'operator.a@smartroom.ai', 'Operator A', 'operator', true, '[1,2]'),
('operator_b', '$2b$12$n1.uTH69p9Q974snakBGL.7yIaXevsIPGoqX0/M46XdFWRXusxoYm', 'operator.b@smartroom.ai', 'Operator B', 'operator', true, '[3,4]');

-- A few DecisionLog entries to seed system history (decisions made by agents)
INSERT INTO decision_logs (timestamp, agent_id, room_id, decision, reasoning, comfort_score, energy_score, reliability_score, context) VALUES
(now() - interval '30 minutes', 'gemini', 1, '{"decisions": [{"device_id": "Ceiling Light A1", "action": "turn_on", "parameters": {"brightness":0.3}}]}', 'Activated minimum lighting for security / during meeting prep', 0.8, 0.6, 0.9, '{"sensor_snapshot": {"co2":720, "temperature":24.1}}'),
(now() - interval '20 minutes', 'claude', 1, '{"decisions": [{"device_id": "AC Unit A1", "action": "turn_on", "parameters": {"mode":"cool"}}]}', 'Reduced temperature to meet comfort SLO', 0.9, 0.7, 0.95, '{"sensor_snapshot": {"temperature":25.5}}');

COMMIT;

-- End of seed file
