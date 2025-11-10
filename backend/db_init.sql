-- DB initialization script for SmartRoom (Postgres)
-- Run as: psql -U postgres -f db_init.sql

CREATE TABLE IF NOT EXISTS rooms (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  gsi DOUBLE PRECISION DEFAULT 0.0,
  aq INTEGER,
  temp DOUBLE PRECISION,
  occupancy INTEGER,
  position JSONB
);

CREATE TYPE device_status AS ENUM ('ON','OFF');

CREATE TABLE IF NOT EXISTS devices (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT,
  status device_status DEFAULT 'OFF',
  room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
  services JSONB
);

CREATE TABLE IF NOT EXISTS agents (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  goal TEXT,
  rag_sources JSONB,
  active BOOLEAN DEFAULT TRUE,
  endpoint TEXT,
  weight DOUBLE PRECISION DEFAULT 0.33
);

CREATE TABLE IF NOT EXISTS decision_logs (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
  agent_id TEXT REFERENCES agents(id),
  room_id INTEGER REFERENCES rooms(id),
  decision TEXT,
  reasoning TEXT,
  comfort_score DOUBLE PRECISION,
  energy_score DOUBLE PRECISION,
  reliability_score DOUBLE PRECISION,
  context JSONB
);

CREATE TABLE IF NOT EXISTS slos (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  target_value DOUBLE PRECISION,
  metric TEXT,
  config JSONB
);

CREATE TABLE IF NOT EXISTS scenarios (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  active BOOLEAN DEFAULT FALSE,
  config JSONB
);

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE,
  hashed_password TEXT,
  is_admin BOOLEAN DEFAULT FALSE
);

-- Sample seed (lightweight) - you can remove or extend as needed
INSERT INTO rooms (name, gsi, aq, temp, occupancy, position)
VALUES
('Conference Room A', 0.84, 85, 24, 5, '{"x":100,"y":100}'),
('Conference Room B', 0.76, 78, 26, 3, '{"x":350,"y":100}'),
('Office Space', 0.92, 92, 23, 8, '{"x":100,"y":300}'),
('Lab Room', 0.68, 72, 27, 2, '{"x":350,"y":300}');

-- sample devices (names must match frontend expectations)
INSERT INTO devices (name, type, status, room_id, services)
VALUES
('AC','HVAC','ON',1,'[{"name":"TempFromWeatherStation","inputSource":"Weather Node","active":true,"controlledBy":"Claude"}]'),
('Light','Lighting','ON',1,'[{"name":"CameraLighting","inputSource":"Camera Sensor","active":true,"controlledBy":"Gemini"}]'),
('Fan','AirFlow','ON',1,'[{"name":"CirculateAir","inputSource":"Occupancy Sensor","active":true,"controlledBy":"Gemini"}]'),
('Camera','Security','ON',1,'[{"name":"Monitoring","inputSource":"Motion Sensor","active":true,"controlledBy":"GPT"}]'),
('AC','HVAC','ON',2,'[{"name":"TempControl","inputSource":"Temp Sensor","active":true,"controlledBy":"Claude"}]'),
('Light','Lighting','ON',2,'[{"name":"AutoLight","inputSource":"Light Sensor","active":true,"controlledBy":"Gemini"}]'),
('Fan','AirFlow','OFF',2,'[{"name":"CirculateAir","inputSource":"Occupancy Sensor","active":false}]');
