#!/usr/bin/env node

// Simple integration test for frontend-backend communication
// Run with: node test-integration.js

const API_BASE = 'http://localhost:8000';

async function testIntegration() {
  console.log('🧪 Testing backend integration...');
  
  try {
    // Test 1: Fetch all rooms
    console.log('\n1️⃣ Testing GET /api/rooms/');
    const roomsRes = await fetch(`${API_BASE}/api/rooms/`);
    if (!roomsRes.ok) throw new Error(`HTTP ${roomsRes.status}`);
    const rooms = await roomsRes.json();
    console.log(`✅ Found ${rooms.length} rooms`);
    console.log(`   Sample room: ${rooms[0]?.name || 'None'}`);
    
    // Test 2: Fetch single room
    if (rooms.length > 0) {
      const roomId = rooms[0].id;
      console.log(`\n2️⃣ Testing GET /api/rooms/${roomId}`);
      const roomRes = await fetch(`${API_BASE}/api/rooms/${roomId}`);
      if (!roomRes.ok) throw new Error(`HTTP ${roomRes.status}`);
      const room = await roomRes.json();
      console.log(`✅ Room details: ${room.name}, devices: ${room.devices?.length || 0}`);
    }
    
    // Test 3: Update device status
    if (rooms.length > 0 && rooms[0].devices?.length > 0) {
      const roomId = rooms[0].id;
      const deviceName = rooms[0].devices[0].name;
      const currentStatus = rooms[0].devices[0].status;
      const newStatus = currentStatus === 'ON' ? 'OFF' : 'ON';
      
      console.log(`\n3️⃣ Testing PATCH /api/rooms/${roomId}/devices/${deviceName}`);
      const patchRes = await fetch(`${API_BASE}/api/rooms/${roomId}/devices/${encodeURIComponent(deviceName)}?status=${newStatus}`, {
        method: 'PATCH'
      });
      if (!patchRes.ok) throw new Error(`HTTP ${patchRes.status}`);
      const updatedRoom = await patchRes.json();
      const updatedDevice = updatedRoom.devices.find(d => d.name === deviceName);
      console.log(`✅ Device ${deviceName}: ${currentStatus} → ${updatedDevice.status}`);
    }
    
    console.log('\n🎉 All tests passed! Frontend-backend integration is working.');
    
  } catch (error) {
    console.error('\n❌ Integration test failed:', error.message);
    process.exit(1);
  }
}

testIntegration();