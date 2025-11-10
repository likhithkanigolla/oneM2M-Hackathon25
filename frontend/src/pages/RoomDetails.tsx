import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useRooms } from "@/store/useRooms";
import { useAgents } from "@/store/useAgents";
import { useDevices, Device } from "@/store/useDevices";
import { useAuth } from "@/store/useAuth";
import { useAnalytics } from "@/store/useAnalytics";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { ArrowLeft, Thermometer, Wind, Users, Zap, Clock, Plus, Edit2, Trash2, Settings } from "lucide-react";
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, ResponsiveContainer } from "recharts";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export default function RoomDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { rooms, updateRoomDevice, fetchRooms } = useRooms();
  const { agents, fetchAgents } = useAgents();
  const { devices, fetchRoomDevices, createDevice, updateDevice, deleteDevice, updateDeviceStatus } = useDevices();
  const { user } = useAuth();
  const { sloPerformance, agentDecisions, fetchSLOPerformance, fetchAgentDecisions } = useAnalytics();

  // Device management state
  const [isCreateDeviceOpen, setIsCreateDeviceOpen] = useState(false);
  const [isEditDeviceOpen, setIsEditDeviceOpen] = useState(false);
  const [editingDevice, setEditingDevice] = useState<Device | null>(null);
  const [deviceForm, setDeviceForm] = useState({
    name: '',
    type: '',
    status: 'OFF' as 'ON' | 'OFF',
    services: [] as any[],
  });

  useEffect(() => {
    fetchRooms();
    fetchAgents();
    if (id) {
      fetchRoomDevices(Number(id));
      fetchSLOPerformance(Number(id));
      fetchAgentDecisions(Number(id));
    }
  }, [fetchRooms, fetchAgents, fetchRoomDevices, fetchSLOPerformance, fetchAgentDecisions, id]);

  const isAdmin = user?.role === 'admin';

  const room = rooms.find((r) => r.id === Number(id));

  if (!room) {
    return (
      <div className="container mx-auto px-6 py-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Room Not Found</h2>
          <Button onClick={() => navigate("/")}>Back to Dashboard</Button>
        </div>
      </div>
    );
  }

  // Transform SLO data for radar chart - use backend data or fallback
  const sloData = sloPerformance.length > 0 ? [
    {
      slo: "Comfort",
      Gemini: sloPerformance.find(s => s.name === "Comfort")?.performance_score || 0.65,
      Claude: sloPerformance.find(s => s.name === "Comfort")?.performance_score || 0.90,
      GPT: sloPerformance.find(s => s.name === "Comfort")?.performance_score || 0.75,
    },
    {
      slo: "Energy",
      Gemini: sloPerformance.find(s => s.name === "Energy")?.performance_score || 0.90,
      Claude: sloPerformance.find(s => s.name === "Energy")?.performance_score || 0.70,
      GPT: sloPerformance.find(s => s.name === "Energy")?.performance_score || 0.80,
    },
    {
      slo: "Reliability",
      Gemini: sloPerformance.find(s => s.name === "Reliability")?.performance_score || 0.80,
      Claude: sloPerformance.find(s => s.name === "Reliability")?.performance_score || 0.95,
      GPT: sloPerformance.find(s => s.name === "Reliability")?.performance_score || 0.85,
    },
  ] : [
    // Fallback data while loading
    { slo: "Comfort", Gemini: 0.65, Claude: 0.90, GPT: 0.75 },
    { slo: "Energy", Gemini: 0.90, Claude: 0.70, GPT: 0.80 },
    { slo: "Reliability", Gemini: 0.80, Claude: 0.95, GPT: 0.85 },
  ];

  // Use backend agent decisions or fallback
  const llmDecisions = agentDecisions.length > 0 ? agentDecisions.map(decision => ({
    agent: decision.agent,
    goal: "Smart Decision Making",
    decision: decision.decision,
    comfort: decision.confidence > 0.8 ? 0.9 : 0.7,
    energy: decision.confidence,
    reliability: decision.confidence > 0.85 ? 0.95 : 0.8,
    reasoning: decision.reasoning,
  })) : [
    // Fallback data while loading
    {
      agent: "Gemini",
      goal: "Energy Efficiency",
      decision: "Fan Only",
      comfort: 0.65,
      energy: 0.90,
      reliability: 0.80,
      reasoning: "Low power consumption, sufficient air circulation for current occupancy",
    },
    {
      agent: "Claude",
      goal: "SLO Priority & Comfort",
      decision: "AC + Fan",
      comfort: 0.90,
      energy: 0.70,
      reliability: 0.95,
      reasoning: "Meeting active scenario prioritizes comfort, weather service optimizes AC usage",
    },
    {
      agent: "GPT-5",
      goal: "Security & Reliability",
      decision: "All Devices On",
      comfort: 0.75,
      energy: 0.80,
      reliability: 0.85,
      reasoning: "Maintain all systems operational for reliability, balanced approach",
    },
  ];

  const handleDeviceToggle = (deviceName: string, currentStatus: string) => {
    const newStatus = currentStatus === "ON" ? "OFF" : "ON";
    updateRoomDevice(room.id, deviceName, newStatus);
    toast.success(`${deviceName} turned ${newStatus}`, {
      description: "Manual override applied",
    });
  };

  // New device management handlers
  const handleCreateDevice = async () => {
    if (!isAdmin) {
      toast.error("Only administrators can create devices");
      return;
    }

    try {
      await createDevice({
        ...deviceForm,
        room_id: Number(id),
      });
      toast.success("Device created successfully");
      setIsCreateDeviceOpen(false);
      resetDeviceForm();
    } catch (error) {
      toast.error("Failed to create device");
    }
  };

  const handleUpdateDevice = async () => {
    if (!isAdmin || !editingDevice) return;

    try {
      await updateDevice(editingDevice.id, deviceForm);
      toast.success("Device updated successfully");
      setIsEditDeviceOpen(false);
      setEditingDevice(null);
      resetDeviceForm();
    } catch (error) {
      toast.error("Failed to update device");
    }
  };

  const handleDeleteDevice = async (deviceId: number, deviceName: string) => {
    if (!isAdmin) {
      toast.error("Only administrators can delete devices");
      return;
    }

    if (window.confirm(`Are you sure you want to delete "${deviceName}"?`)) {
      try {
        await deleteDevice(deviceId);
        toast.success("Device deleted successfully");
      } catch (error) {
        toast.error("Failed to delete device");
      }
    }
  };

  const handleDeviceStatusToggle = async (deviceId: number, currentStatus: string, deviceName: string) => {
    const newStatus = currentStatus === "ON" ? "OFF" : "ON";
    try {
      await updateDeviceStatus(deviceId, newStatus as 'ON' | 'OFF');
      toast.success(`${deviceName} turned ${newStatus}`);
    } catch (error) {
      toast.error("Failed to update device status");
    }
  };

  const openEditDevice = (device: Device) => {
    setEditingDevice(device);
    setDeviceForm({
      name: device.name,
      type: device.type,
      status: device.status,
      services: device.services || [],
    });
    setIsEditDeviceOpen(true);
  };

  const resetDeviceForm = () => {
    setDeviceForm({
      name: '',
      type: '',
      status: 'OFF',
      services: [],
    });
  };

  const updateDeviceForm = (field: string, value: any) => {
    setDeviceForm(prev => ({ ...prev, [field]: value }));
  };

  const getGSIColor = (gsi: number) => {
    if (gsi >= 0.8) return "energy";
    if (gsi >= 0.6) return "reliability";
    return "danger";
  };

  return (
    <>
      <div className="container mx-auto px-6 py-6 space-y-6 animate-fade-in">
        {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate("/")}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{room.name}</h1>
            <div className="flex items-center gap-3 mt-1">
              <Badge
                variant="outline"
                className={cn(
                  "font-mono",
                  `border-${getGSIColor(room.gsi)} text-${getGSIColor(room.gsi)}`
                )}
              >
                GSI {(room.gsi * 100).toFixed(0)}
              </Badge>
              <span className="text-sm text-muted-foreground flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Last updated: {new Date().toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Live Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Thermometer className="h-4 w-4 text-comfort" />
              Temperature
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{room.temp}°C</div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Wind className="h-4 w-4 text-comfort" />
              Air Quality
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{room.aq}</div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Users className="h-4 w-4 text-accent" />
              Occupancy
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{room.occupancy}</div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Zap className="h-4 w-4 text-energy" />
              Power Usage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {(room.devices.filter((d) => d.status === "ON").length * 12.5).toFixed(1)}W
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Device Controls & SLO Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Device Controls */}
        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Device Control</CardTitle>
              {isAdmin && (
                <Dialog open={isCreateDeviceOpen} onOpenChange={setIsCreateDeviceOpen}>
                  <DialogTrigger asChild>
                    <Button size="sm">
                      <Plus className="h-4 w-4 mr-2" />
                      Add Device
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Add New Device</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="device-name">Device Name</Label>
                        <Input
                          id="device-name"
                          value={deviceForm.name}
                          onChange={(e) => updateDeviceForm('name', e.target.value)}
                          placeholder="e.g., Smart Thermostat"
                        />
                      </div>
                      <div>
                        <Label htmlFor="device-type">Device Type</Label>
                        <Select value={deviceForm.type} onValueChange={(value) => updateDeviceForm('type', value)}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select device type" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="HVAC">HVAC</SelectItem>
                            <SelectItem value="Lighting">Lighting</SelectItem>
                            <SelectItem value="AirFlow">Air Flow</SelectItem>
                            <SelectItem value="Security">Security</SelectItem>
                            <SelectItem value="Sensor">Sensor</SelectItem>
                            <SelectItem value="Other">Other</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label htmlFor="device-status">Initial Status</Label>
                        <Select value={deviceForm.status} onValueChange={(value) => updateDeviceForm('status', value)}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="ON">ON</SelectItem>
                            <SelectItem value="OFF">OFF</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button onClick={handleCreateDevice} disabled={!deviceForm.name || !deviceForm.type}>
                        Create Device
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {devices.length > 0 ? devices.map((device) => (
              <div
                key={device.id}
                className="flex items-center justify-between p-4 rounded-lg border border-border/50 bg-muted/20"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={cn(
                      "h-3 w-3 rounded-full",
                      device.status === "ON" ? "bg-energy animate-pulse-slow" : "bg-muted"
                    )}
                  />
                  <div>
                    <p className="font-medium">{device.name}</p>
                    <p className="text-xs text-muted-foreground">{device.type}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-muted-foreground">{device.status}</span>
                  <Switch
                    checked={device.status === "ON"}
                    onCheckedChange={() => handleDeviceStatusToggle(device.id, device.status, device.name)}
                  />
                  {isAdmin && (
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openEditDevice(device)}
                        className="h-8 w-8 p-0"
                      >
                        <Edit2 className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteDevice(device.id, device.name)}
                        className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            )) : (
              <div className="text-center py-8 text-muted-foreground">
                <Settings className="h-12 w-12 mx-auto mb-4" />
                <p>No devices in this room</p>
                {isAdmin && <p className="text-sm">Add devices to get started</p>}
              </div>
            )}
          </CardContent>
        </Card>

        {/* SLO Radar Chart */}
        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader>
            <CardTitle>SLO Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={sloData}>
                <PolarGrid stroke="hsl(var(--border))" />
                <PolarAngleAxis dataKey="slo" stroke="hsl(var(--foreground))" />
                <PolarRadiusAxis angle={90} domain={[0, 1]} stroke="hsl(var(--muted-foreground))" />
                <Radar name="Gemini" dataKey="Gemini" stroke="hsl(var(--energy))" fill="hsl(var(--energy))" fillOpacity={0.3} />
                <Radar name="Claude" dataKey="Claude" stroke="hsl(var(--comfort))" fill="hsl(var(--comfort))" fillOpacity={0.3} />
                <Radar name="GPT" dataKey="GPT" stroke="hsl(var(--reliability))" fill="hsl(var(--reliability))" fillOpacity={0.3} />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* LLM Decisions Table */}
      <Card className="bg-gradient-to-br from-card to-card/80">
        <CardHeader>
          <CardTitle>AI Agent Decisions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 font-medium">Agent</th>
                  <th className="text-left py-3 px-4 font-medium">Goal</th>
                  <th className="text-left py-3 px-4 font-medium">Decision</th>
                  <th className="text-center py-3 px-4 font-medium">Comfort</th>
                  <th className="text-center py-3 px-4 font-medium">Energy</th>
                  <th className="text-center py-3 px-4 font-medium">Reliability</th>
                  <th className="text-left py-3 px-4 font-medium">Reasoning</th>
                </tr>
              </thead>
              <tbody>
                {llmDecisions.map((decision) => (
                  <tr key={decision.agent} className="border-b border-border/50">
                    <td className="py-3 px-4 font-medium">{decision.agent}</td>
                    <td className="py-3 px-4 text-sm text-muted-foreground">{decision.goal}</td>
                    <td className="py-3 px-4">
                      <Badge variant="secondary">{decision.decision}</Badge>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="text-comfort font-mono">{(decision.comfort * 100).toFixed(0)}%</span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="text-energy font-mono">{(decision.energy * 100).toFixed(0)}%</span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="text-reliability font-mono">{(decision.reliability * 100).toFixed(0)}%</span>
                    </td>
                    <td className="py-3 px-4 text-sm text-muted-foreground max-w-md">{decision.reasoning}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>

    {/* Edit Device Dialog */}
    <Dialog open={isEditDeviceOpen} onOpenChange={setIsEditDeviceOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Device</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="edit-device-name">Device Name</Label>
            <Input
              id="edit-device-name"
              value={deviceForm.name}
              onChange={(e) => updateDeviceForm('name', e.target.value)}
              placeholder="e.g., Smart Thermostat"
            />
          </div>
          <div>
            <Label htmlFor="edit-device-type">Device Type</Label>
            <Select value={deviceForm.type} onValueChange={(value) => updateDeviceForm('type', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select device type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="HVAC">HVAC</SelectItem>
                <SelectItem value="Lighting">Lighting</SelectItem>
                <SelectItem value="AirFlow">Air Flow</SelectItem>
                <SelectItem value="Security">Security</SelectItem>
                <SelectItem value="Sensor">Sensor</SelectItem>
                <SelectItem value="Other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="edit-device-status">Status</Label>
            <Select value={deviceForm.status} onValueChange={(value) => updateDeviceForm('status', value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ON">ON</SelectItem>
                <SelectItem value="OFF">OFF</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button onClick={handleUpdateDevice} disabled={!deviceForm.name || !deviceForm.type || !editingDevice}>
            Update Device
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
    </>
  );
}
