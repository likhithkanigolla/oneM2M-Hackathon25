import { useParams, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { useRooms } from "@/store/useRooms";
import { useAgents } from "@/store/useAgents";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Thermometer, Wind, Users, Zap, Clock } from "lucide-react";
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, ResponsiveContainer } from "recharts";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export default function RoomDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { rooms, updateRoomDevice, fetchRooms } = useRooms();
  const { agents, fetchAgents } = useAgents();

  useEffect(() => {
    fetchRooms();
    fetchAgents();
  }, [fetchRooms, fetchAgents]);

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

  // Mock SLO data for radar chart
  const sloData = [
    {
      slo: "Comfort",
      Gemini: 0.65,
      Claude: 0.90,
      GPT: 0.75,
    },
    {
      slo: "Energy",
      Gemini: 0.90,
      Claude: 0.70,
      GPT: 0.80,
    },
    {
      slo: "Reliability",
      Gemini: 0.80,
      Claude: 0.95,
      GPT: 0.85,
    },
  ];

  // Mock LLM decisions
  const llmDecisions = [
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

  const getGSIColor = (gsi: number) => {
    if (gsi >= 0.8) return "energy";
    if (gsi >= 0.6) return "reliability";
    return "danger";
  };

  return (
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
            <CardTitle>Device Control</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {room.devices.map((device) => (
              <div
                key={device.name}
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
                    onCheckedChange={() => handleDeviceToggle(device.name, device.status)}
                  />
                </div>
              </div>
            ))}
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
  );
}
