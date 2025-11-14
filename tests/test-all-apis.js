#!/usr/bin/env node

// Comprehensive API test for all backend endpoints
// Run with: node test-all-apis.js

const API_BASE = 'http://localhost:8000';

async function testAllAPIs() {
  console.log('🧪 Testing all backend APIs...\n');
  
  try {
    // Test Agents API
    console.log('1️⃣ Testing Agents API');
    const agentsRes = await fetch(`${API_BASE}/api/agents/`);
    if (!agentsRes.ok) throw new Error(`Agents API failed: ${agentsRes.status}`);
    const agents = await agentsRes.json();
    console.log(`✅ Agents: Found ${agents.length} agents`);
    if (agents.length > 0) {
      console.log(`   Sample: ${agents[0].name} (${agents[0].active ? 'active' : 'inactive'})`);
    }
    
    // Test SLOs API
    console.log('\n2️⃣ Testing SLOs API');
    const slosRes = await fetch(`${API_BASE}/api/slos/`);
    if (!slosRes.ok) throw new Error(`SLOs API failed: ${slosRes.status}`);
    const slos = await slosRes.json();
    console.log(`✅ SLOs: Found ${slos.length} SLOs`);
    if (slos.length > 0) {
      console.log(`   Sample: ${slos[0].name} (target: ${slos[0].target_value})`);
    }
    
    // Test Scenarios API
    console.log('\n3️⃣ Testing Scenarios API');
    const scenariosRes = await fetch(`${API_BASE}/api/scenarios/`);
    if (!scenariosRes.ok) throw new Error(`Scenarios API failed: ${scenariosRes.status}`);
    const scenarios = await scenariosRes.json();
    console.log(`✅ Scenarios: Found ${scenarios.length} scenarios`);
    if (scenarios.length > 0) {
      console.log(`   Sample: ${scenarios[0].name} (${scenarios[0].active ? 'active' : 'inactive'})`);
    }
    
    // Test Users API
    console.log('\n4️⃣ Testing Users API');
    const usersRes = await fetch(`${API_BASE}/api/users/`);
    if (!usersRes.ok) throw new Error(`Users API failed: ${usersRes.status}`);
    const users = await usersRes.json();
    console.log(`✅ Users: Found ${users.length} users`);
    if (users.length > 0) {
      console.log(`   Sample: ${users[0].username} (admin: ${users[0].is_admin})`);
    }
    
    // Test Analytics API
    console.log('\n5️⃣ Testing Analytics API');
    const analyticsRes = await fetch(`${API_BASE}/api/analytics/system-overview`);
    if (!analyticsRes.ok) throw new Error(`Analytics API failed: ${analyticsRes.status}`);
    const analytics = await analyticsRes.json();
    console.log(`✅ Analytics: System overview retrieved`);
    console.log(`   Total rooms: ${analytics.total_rooms}, Active agents: ${analytics.active_agents}, Avg GSI: ${analytics.average_gsi.toFixed(2)}`);
    
    // Test existing Rooms API
    console.log('\n6️⃣ Testing Rooms API');
    const roomsRes = await fetch(`${API_BASE}/api/rooms/`);
    if (!roomsRes.ok) throw new Error(`Rooms API failed: ${roomsRes.status}`);
    const rooms = await roomsRes.json();
    console.log(`✅ Rooms: Found ${rooms.length} rooms`);
    
    console.log('\n🎉 All API endpoints are working!\n');
    console.log('📋 Available endpoints:');
    console.log('  • GET /api/rooms/ - list rooms');
    console.log('  • GET /api/agents/ - list AI agents');
    console.log('  • GET /api/slos/ - list SLOs');
    console.log('  • GET /api/scenarios/ - list scenarios');
    console.log('  • GET /api/users/ - list users');
    console.log('  • GET /api/analytics/system-overview - system metrics');
    console.log('  • PATCH /api/agents/{id}/toggle - toggle agent');
    console.log('  • PATCH /api/scenarios/{id}/toggle - toggle scenario');
    console.log('  • PATCH /api/rooms/{id}/devices/{name}?status=ON|OFF - update device');
    
  } catch (error) {
    console.error('\n❌ API test failed:', error.message);
    process.exit(1);
  }
}

testAllAPIs();