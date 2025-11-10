import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, Zap, Activity, Award } from "lucide-react";
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function Analytics() {
  // SLO Trends
  const sloTrends = [
    { time: "Mon", comfort: 0.85, energy: 0.78, reliability: 0.92 },
    { time: "Tue", comfort: 0.82, energy: 0.80, reliability: 0.88 },
    { time: "Wed", comfort: 0.88, energy: 0.75, reliability: 0.90 },
    { time: "Thu", comfort: 0.90, energy: 0.72, reliability: 0.95 },
    { time: "Fri", comfort: 0.87, energy: 0.77, reliability: 0.89 },
    { time: "Sat", comfort: 0.75, energy: 0.85, reliability: 0.80 },
    { time: "Sun", comfort: 0.70, energy: 0.90, reliability: 0.82 },
  ];

  // Energy Distribution
  const energyData = [
    { name: "Conference A", value: 18.5, color: "hsl(var(--comfort))" },
    { name: "Conference B", value: 15.2, color: "hsl(var(--energy))" },
    { name: "Office Space", value: 25.8, color: "hsl(var(--reliability))" },
    { name: "Lab Room", value: 22.3, color: "hsl(var(--accent))" },
  ];

  // Room Performance
  const roomPerformance = [
    { room: "Office Space", gsi: 0.92 },
    { room: "Conference A", gsi: 0.84 },
    { room: "Lab Room", gsi: 0.68 },
    { room: "Conference B", gsi: 0.76 },
  ].sort((a, b) => b.gsi - a.gsi);

  // Recent Events
  const recentEvents = [
    {
      time: "15:30",
      room: "Conference A",
      event: "Meeting Priority activated",
      impact: "Comfort ↑ 0.84 → 0.92",
    },
    {
      time: "14:45",
      room: "Office Space",
      event: "Energy Shortage scenario triggered",
      impact: "Power reduced 15%",
    },
    {
      time: "13:20",
      room: "Lab Room",
      event: "AQ threshold exceeded",
      impact: "Filter mode activated",
    },
    {
      time: "12:00",
      room: "Conference B",
      event: "Manual override applied",
      impact: "AC turned off",
    },
  ];

  return (
    <div className="container mx-auto px-6 py-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <TrendingUp className="h-8 w-8 text-primary" />
          Analytics & Trends
        </h1>
        <p className="text-muted-foreground mt-1">
          System performance insights and historical data
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Award className="h-4 w-4 text-energy" />
              Avg GSI
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">0.80</div>
            <p className="text-xs text-success mt-1">+5% from last week</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Zap className="h-4 w-4 text-energy" />
              Energy Saved
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">12.3%</div>
            <p className="text-xs text-muted-foreground mt-1">This week</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Activity className="h-4 w-4 text-primary" />
              Decisions Made
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">1,847</div>
            <p className="text-xs text-muted-foreground mt-1">Last 7 days</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-success" />
              Uptime
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">99.8%</div>
            <p className="text-xs text-success mt-1">Excellent</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* SLO Trends */}
        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader>
            <CardTitle>SLO Satisfaction Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={sloTrends}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="time" stroke="hsl(var(--foreground))" />
                <YAxis domain={[0, 1]} stroke="hsl(var(--foreground))" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="comfort"
                  stroke="hsl(var(--comfort))"
                  strokeWidth={2}
                  dot={{ fill: "hsl(var(--comfort))" }}
                />
                <Line
                  type="monotone"
                  dataKey="energy"
                  stroke="hsl(var(--energy))"
                  strokeWidth={2}
                  dot={{ fill: "hsl(var(--energy))" }}
                />
                <Line
                  type="monotone"
                  dataKey="reliability"
                  stroke="hsl(var(--reliability))"
                  strokeWidth={2}
                  dot={{ fill: "hsl(var(--reliability))" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Energy Distribution */}
        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader>
            <CardTitle>Energy Distribution by Room</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={energyData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry: any) => `${entry.name}: ${((entry.percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {energyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Room Performance */}
        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader>
            <CardTitle>Room Performance Ranking</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={roomPerformance} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis type="number" domain={[0, 1]} stroke="hsl(var(--foreground))" />
                <YAxis dataKey="room" type="category" stroke="hsl(var(--foreground))" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                  }}
                />
                <Bar dataKey="gsi" fill="hsl(var(--primary))" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Recent Events */}
        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader>
            <CardTitle>Recent Decision Events</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentEvents.map((event, idx) => (
                <div
                  key={idx}
                  className="flex gap-3 p-3 rounded-lg bg-muted/20 border border-border/50"
                >
                  <div className="text-xs text-muted-foreground font-mono whitespace-nowrap">
                    {event.time}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{event.room}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{event.event}</p>
                    <p className="text-xs text-primary mt-1">{event.impact}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
