import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Agent } from "@/store/useAgents";
import { Brain, Database } from "lucide-react";

interface AgentCardProps {
  agent: Agent;
  onToggle: () => void;
}

export const AgentCard = ({ agent, onToggle }: AgentCardProps) => {
  return (
    <Card className="bg-gradient-to-br from-card to-card/80">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            <CardTitle className="text-base font-semibold">{agent.name}</CardTitle>
          </div>
          <Switch checked={agent.active} onCheckedChange={onToggle} />
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <p className="text-sm text-muted-foreground mb-2">Goal</p>
          <p className="text-sm font-medium">{agent.goal}</p>
        </div>
        
        <div>
          <p className="text-sm text-muted-foreground mb-2 flex items-center gap-1">
            <Database className="h-3 w-3" />
            RAG Sources
          </p>
          <div className="flex flex-wrap gap-1">
            {(agent.rag_sources || []).map((source) => (
              <Badge key={source} variant="secondary" className="text-xs">
                {source}
              </Badge>
            ))}
          </div>
        </div>

        <div className="pt-2 border-t border-border">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Fusion Weight</span>
            <span className="font-mono font-semibold text-primary">
              {(agent.weight * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
