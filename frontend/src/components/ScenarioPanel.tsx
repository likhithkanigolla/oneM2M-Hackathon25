import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { useScenarios } from "@/store/useScenarios";
import { AlertTriangle, Clock, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

const priorityColors = {
  Low: "text-muted-foreground border-muted",
  Medium: "text-warning border-warning",
  High: "text-reliability border-reliability",
  Critical: "text-danger border-danger",
};

const priorityIcons = {
  Low: Clock,
  Medium: Zap,
  High: AlertTriangle,
  Critical: AlertTriangle,
};

export const ScenarioPanel = () => {
  const { scenarios, toggleScenario } = useScenarios();

  return (
    <Card className="bg-gradient-to-br from-card to-card/80">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <Zap className="h-5 w-5 text-accent" />
          Active Scenarios
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {scenarios.map((scenario) => {
          const priority = scenario.priority || 'Medium';
          const Icon = priorityIcons[priority] || Clock;
          
          return (
            <div
              key={scenario.id}
              className={cn(
                "flex items-center justify-between rounded-lg border p-3 transition-colors",
                scenario.active ? "border-primary/20 bg-primary/5" : "border-border/50 bg-muted/20"
              )}
            >
              <div className="flex items-center gap-3 flex-1">
                <Icon
                  className={cn(
                    "h-4 w-4",
                    scenario.active ? priorityColors[priority] || "text-primary" : "text-muted-foreground"
                  )}
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium">{scenario.name}</span>
                    <Badge
                      variant="outline"
                      className={cn(
                        "text-xs",
                        scenario.active ? priorityColors[priority] || "text-primary" : "text-muted-foreground"
                      )}
                    >
                      {priority}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {scenario.trigger || scenario.description || "No trigger info"}
                  </p>
                </div>
                <div className="text-right mr-2">
                  <p className="text-xs font-medium text-accent">
                    {scenario.impact || "Impact varies"}
                  </p>
                </div>
              </div>
              <Switch checked={scenario.active} onCheckedChange={() => toggleScenario(scenario.id)} />
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
};
