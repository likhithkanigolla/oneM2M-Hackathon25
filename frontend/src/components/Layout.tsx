import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Button } from "./ui/button";
import { Plus, RefreshCw } from "lucide-react";
import { useScenarios } from "@/store/useScenarios";
import { Badge } from "./ui/badge";

export const Layout = () => {
  const { scenarios } = useScenarios();
  const activeScenarios = scenarios?.filter(scenario => scenario.active) || [];

  return (
    <div className="flex h-screen w-full bg-gradient-to-br from-background via-background to-background/90">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="h-16 border-b border-border/50 bg-card/30 backdrop-blur-md flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted/50">
              <div className="h-2 w-2 rounded-full bg-energy animate-pulse-slow" />
              <span className="text-sm font-medium">System Active</span>
            </div>
            {activeScenarios.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Active:</span>
                {activeScenarios.slice(0, 2).map((scenario) => (
                  <Badge key={scenario.id} variant="outline" className="text-xs">
                    {scenario.name}
                  </Badge>
                ))}
                {activeScenarios.length > 2 && (
                  <Badge variant="outline" className="text-xs">
                    +{activeScenarios.length - 2}
                  </Badge>
                )}
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" className="gap-2">
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
            <Button size="sm" className="gap-2">
              <Plus className="h-4 w-4" />
              Add Agent
            </Button>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
