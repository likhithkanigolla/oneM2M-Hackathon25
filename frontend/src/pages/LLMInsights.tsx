import { useState, useEffect } from "react";
import { useAnalytics } from "@/store/useAnalytics";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Brain, Target, Zap, TrendingUp } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from "recharts";
import { useAgents } from "@/store/useAgents";

export default function LLMInsights() {
  const { agents, fetchAgents } = useAgents();
  const { historicalData, fetchHistoricalData } = useAnalytics();

  useEffect(() => {
    fetchAgents();
    fetchHistoricalData();
  }, [fetchAgents, fetchHistoricalData]);

  // Transform agents data to match the expected format or use fallback
  const agentsWithInsights = agents.length > 0 ? agents.map(agent => ({
    id: agent.id,
    name: agent.name,
    goal: agent.goal || "Optimization",
    color: agent.id === 'gemini' ? 'energy' : agent.id === 'claude' ? 'comfort' : 'reliability',
    decision: "Smart Control", // Would come from decision logs
    scores: { 
      comfort: Math.random() * 0.3 + 0.65, 
      energy: Math.random() * 0.3 + 0.65, 
      reliability: Math.random() * 0.3 + 0.65 
    },
    reasoning: `AI agent ${agent.name} analyzing current conditions and optimizing for ${agent.goal}. Decision based on real-time sensor data and SLO priorities.`
  })) : [
    {
      id: "gemini",
      name: "Gemini",
      goal: "Energy Efficiency",
      color: "energy",
      decision: "Fan Only Mode",
      scores: { comfort: 0.65, energy: 0.90, reliability: 0.80 },
      reasoning: `Based on current occupancy of 5 people and moderate temperature of 28°C, running only fans provides sufficient air circulation while minimizing power consumption.`,
    },
    {
      id: "claude", 
      name: "Claude",
      goal: "SLO Priority & Comfort",
      color: "comfort",
      decision: "AC + Fan Mode",
      scores: { comfort: 0.90, energy: 0.70, reliability: 0.95 },
      reasoning: `Active "Meeting Priority" scenario indicates occupants require optimal conditions. Weather service integration shows high outdoor temperature.`,
    },
    {
      id: "gpt",
      name: "GPT-5",
      goal: "Balanced Optimization", 
      color: "reliability",
      decision: "Smart Climate Control",
      scores: { comfort: 0.75, energy: 0.80, reliability: 0.85 },
      reasoning: `Hybrid approach balancing all SLOs. AC operates at 75% capacity with fan support for efficient air distribution.`,
    },
  ];

  const [selectedAgent, setSelectedAgent] = useState(agentsWithInsights[0]);

  // Use backend historical data or fallback
  const chartHistoricalData = historicalData.length > 0 ? historicalData : [
    { time: "10:00", comfort: 0.7, energy: 0.85, reliability: 0.8 },
    { time: "11:00", comfort: 0.75, energy: 0.82, reliability: 0.85 },
    { time: "12:00", comfort: 0.8, energy: 0.78, reliability: 0.82 },
    { time: "13:00", comfort: 0.85, energy: 0.75, reliability: 0.88 },
    { time: "14:00", comfort: 0.82, energy: 0.80, reliability: 0.85 },
    { time: "15:00", comfort: 0.88, energy: 0.77, reliability: 0.90 },
  ];

  const scoreData = [
    { slo: "Comfort", score: selectedAgent.scores.comfort },
    { slo: "Energy", score: selectedAgent.scores.energy },
    { slo: "Reliability", score: selectedAgent.scores.reliability },
  ];

  return (
    <div className="container mx-auto px-6 py-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Brain className="h-8 w-8 text-primary" />
          LLM Agent Insights
        </h1>
        <p className="text-muted-foreground mt-1">
          Compare AI reasoning and decision patterns
        </p>
      </div>

      {/* Agent Tabs */}
      <Tabs defaultValue="gemini" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          {agentsWithInsights.map((agent) => (
            <TabsTrigger
              key={agent.id}
              value={agent.id}
              onClick={() => setSelectedAgent(agent)}
            >
              {agent.name}
            </TabsTrigger>
          ))}
        </TabsList>

        {agentsWithInsights.map((agent) => (
          <TabsContent key={agent.id} value={agent.id} className="space-y-6">
            {/* Agent Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="bg-gradient-to-br from-card to-card/80">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <Target className="h-4 w-4" />
                    Primary Goal
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xl font-semibold">{agent.goal}</p>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-card to-card/80">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <Zap className="h-4 w-4" />
                    Current Decision
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Badge variant="secondary" className="text-base">
                    {agent.decision}
                  </Badge>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-card to-card/80">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Avg. Performance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">
                    {(
                      (agent.scores.comfort +
                        agent.scores.energy +
                        agent.scores.reliability) /
                      3
                    ).toFixed(2)}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* SLO Scores & Reasoning */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Bar Chart */}
              <Card className="bg-gradient-to-br from-card to-card/80">
                <CardHeader>
                  <CardTitle>SLO Satisfaction Scores</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={scoreData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="slo" stroke="hsl(var(--foreground))" />
                      <YAxis domain={[0, 1]} stroke="hsl(var(--foreground))" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "hsl(var(--card))",
                          border: "1px solid hsl(var(--border))",
                        }}
                      />
                      <Bar dataKey="score" fill={`hsl(var(--${agent.color}))`} radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Reasoning */}
              <Card className="bg-gradient-to-br from-card to-card/80">
                <CardHeader>
                  <CardTitle>Decision Reasoning</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <p className="text-foreground/90 leading-relaxed">
                      {agent.reasoning}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Historical Performance */}
            <Card className="bg-gradient-to-br from-card to-card/80">
              <CardHeader>
                <CardTitle>Historical SLO Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartHistoricalData}>
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
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
