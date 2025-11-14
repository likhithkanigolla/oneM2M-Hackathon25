# Google Gemini LLM Integration Guide

## 🤖 Overview

Your smart building management system now has an **AI brain** powered by Google Gemini! The system uses multiple specialized LLM agents that make intelligent decisions based on:

- **Admin-defined Global SLOs** (e.g., "at least one light on for surveillance")  
- **Operator Room-specific SLOs** (e.g., "meeting room needs AC at 22°C")
- **Real-time IoT sensor data** (temperature, occupancy, air quality)
- **Device status and capabilities**

## 🧠 LLM Agent Types

The system has **6 specialized agents**, each with their own goals and priorities:

### 1. **Security Agent** (Highest Priority)
- **Goal**: Maintain security and surveillance requirements
- **Focus**: Lighting for cameras, emergency access, security device status
- **SLO Example**: "Ensure at least one light remains on for surveillance"

### 2. **Comfort Agent**
- **Goal**: Maximize occupant comfort and wellbeing  
- **Focus**: Temperature, lighting, air quality for human comfort
- **SLO Example**: "Meeting rooms maintain 22-24°C during occupancy"

### 3. **Energy Agent**
- **Goal**: Optimize energy consumption and efficiency
- **Focus**: Turn off unused devices, efficient HVAC settings
- **SLO Example**: "Reduce energy consumption by 15% during peak hours"

### 4. **Emergency Agent** (Override Authority)
- **Goal**: Ensure safety and emergency response
- **Focus**: Fire safety, emergency lighting, crisis protocols
- **SLO Example**: "Emergency exits must be illuminated at all times"

### 5. **Environmental Agent**
- **Goal**: Maintain healthy indoor air quality
- **Focus**: Humidity, CO2 levels, ventilation, air filtering
- **SLO Example**: "Keep CO2 below 800ppm in occupied spaces"

### 6. **Occupancy Agent**
- **Goal**: Optimize systems based on occupancy patterns
- **Focus**: Adaptive lighting/HVAC based on people count
- **SLO Example**: "Pre-condition meeting rooms 15 minutes before scheduled use"

## ⚡ How Conflicts Are Resolved

When agents disagree, the system uses intelligent **conflict resolution**:

1. **Emergency Override**: Emergency agent can override all others
2. **Priority Weighting**: Higher priority agents have more influence  
3. **Majority Vote**: When priorities are close, majority rules
4. **Manual Escalation**: Complex conflicts get flagged for human review

## 🔧 Setup Instructions

### 1. Get Google AI API Key (FREE)
```bash
# Visit Google AI Studio
open https://aistudio.google.com/app/apikey

# Create a new API key (free tier available)
# Copy your API key
```

### 2. Install Dependencies
```bash
# Run the automated setup
./setup_llm.sh

# OR manual installation:
cd backend
pip install google-generativeai httpx
```

### 3. Configure Environment
```bash
# Add to backend/.env file:
GOOGLE_API_KEY=your_actual_api_key_here
```

### 4. Start the System
```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend  
cd frontend
npm run dev
```

## 🧪 Testing LLM Integration

### Check LLM Status
```bash
curl http://localhost:8000/api/llm/status
```

### Test Room Decision Making
```bash
curl -X POST http://localhost:8000/api/llm/test-decision/1 \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_data": {"temperature": 28, "occupancy": 5},
    "scenario": "Meeting in progress"
  }'
```

### Test Gemini API Directly
```bash
curl -X POST http://localhost:8000/api/llm/test-gemini
```

### View Available Agent Types
```bash
curl http://localhost:8000/api/llm/agent-types
```

## 📊 Dashboard Integration

The **existing dashboard** already displays LLM agent decisions:

### 1. **LLM Insights Page** (`/llm-insights`)
- Compare decisions from different agents
- View reasoning and confidence scores
- Historical performance trends
- Agent-specific SLO optimization

### 2. **Room Details Page** (`/rooms/:id`)
- Real-time agent decisions table
- Agent reasoning explanations  
- Conflict resolution status
- Emergency override indicators

### 3. **Analytics Page** (`/analytics`)
- Agent decision history
- SLO performance metrics
- System optimization trends

## 🔄 Real-World Decision Example

**Scenario**: Conference room with 8 people, 28°C temperature, security SLO requires lighting

**Agent Decisions**:
- **Security**: "Keep main light on (30% brightness)" - Priority 0.9
- **Comfort**: "Turn AC to 22°C, increase lighting" - Priority 0.8  
- **Energy**: "Use fan only, dim lights" - Priority 0.6
- **Environmental**: "Increase ventilation for CO2" - Priority 0.7

**Final Decision** (Conflict Resolution):
- AC set to 23°C (compromise between comfort & energy)
- Main light stays on at 50% (security + comfort needs)
- Fan activated for air circulation (environmental)
- Reasoning: "Balancing security requirements with occupant comfort during meeting"

## 🛡️ Fallback Behavior

If Google Gemini API is unavailable:
- Agents use **rule-based fallback logic**
- System continues operating safely
- Dashboard shows "LLM offline" status
- Decisions still logged for later analysis

## 🚀 API Endpoints

### LLM Testing
- `GET /api/llm/status` - Check LLM integration status
- `POST /api/llm/test-decision/{room_id}` - Test room decision making
- `POST /api/llm/test-gemini` - Direct Gemini API test
- `GET /api/llm/agent-types` - List available agents

### Analytics (Enhanced)
- `GET /api/analytics/agent-decisions/{room_id}` - Real LLM decisions
- `GET /api/analytics/historical-data` - Performance trends
- `GET /api/analytics/recent-events` - System events with LLM context

## 🎯 Benefits

### For Building Managers
- **Intelligent automation** that learns from SLOs and sensor data
- **Conflict resolution** between competing priorities  
- **Audit trail** of all AI decisions with explanations
- **Manual override** capabilities when needed

### For Operators
- **Room-specific optimization** based on usage patterns
- **Predictive adjustments** before occupants arrive
- **Energy savings** without sacrificing comfort
- **Emergency response** coordination

### For Occupants  
- **Optimal comfort** automatically maintained
- **Responsive environment** that adapts to activity
- **Health-focused** air quality management
- **Security assurance** with intelligent monitoring

## 🔍 Monitoring & Debugging

### View Live Decisions
```bash
# Watch decision logs in real-time
curl http://localhost:8000/api/analytics/agent-decisions/1

# Check agent performance
curl http://localhost:8000/api/analytics/historical-data
```

### Debug LLM Issues
```bash
# Check API key configuration
curl http://localhost:8000/api/llm/status

# Test with simple prompt
curl -X POST http://localhost:8000/api/llm/test-gemini
```

## 🌟 Your Building Now Has AI Intelligence!

The smart building management system now operates like a **digital brain**:

1. **Perceives** the environment through IoT sensors
2. **Thinks** using specialized LLM agents with different goals  
3. **Decides** optimal actions through intelligent conflict resolution
4. **Acts** by controlling devices and systems
5. **Learns** from outcomes to improve future decisions
6. **Explains** its reasoning for transparency and trust

This creates a truly **intelligent building** that balances security, comfort, energy efficiency, and safety automatically while respecting admin policies and operator preferences.