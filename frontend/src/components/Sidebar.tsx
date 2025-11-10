import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Building2,
  Settings,
  Brain,
  TrendingUp,
  Activity,
  Users,
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Rooms", href: "/rooms", icon: Building2 },
  { name: "SLO Config", href: "/slo", icon: Settings },
  { name: "LLM Insights", href: "/insights", icon: Brain },
  { name: "Analytics", href: "/analytics", icon: TrendingUp },
  { name: "Users", href: "/users", icon: Users },
];

export const Sidebar = () => {
  return (
    <aside className="w-64 border-r border-border/50 bg-card/30 backdrop-blur-md">
      <div className="flex h-16 items-center gap-3 px-6 border-b border-border/50">
        <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
          <Activity className="h-6 w-6 text-primary-foreground" />
        </div>
        <div>
          <h1 className="text-lg font-bold">Smart Room</h1>
          <p className="text-xs text-muted-foreground">Control Center</p>
        </div>
      </div>
      
      <nav className="p-4 space-y-1">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            end={item.href === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg transition-all",
                "hover:bg-primary/10 hover:text-primary",
                isActive
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground"
              )
            }
          >
            <item.icon className="h-5 w-5" />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};
