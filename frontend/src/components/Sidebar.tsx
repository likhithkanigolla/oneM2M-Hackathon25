import { NavLink } from "react-router-dom";
import { useAuth } from "@/store/useAuth";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Building2,
  Settings,
  Brain,
  TrendingUp,
  Activity,
  Users,
  LogOut,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard, roles: ["admin", "operator"] },
  { name: "Rooms", href: "/rooms", icon: Building2, roles: ["admin", "operator"] },
  { name: "SLO Config", href: "/slo", icon: Settings, roles: ["admin", "operator"] },
  { name: "LLM Insights", href: "/insights", icon: Brain, roles: ["admin", "operator"] },
  { name: "Analytics", href: "/analytics", icon: TrendingUp, roles: ["admin", "operator"] },
  { name: "Users", href: "/users", icon: Users, roles: ["admin"] },
];

export const Sidebar = () => {
  const { user, logout } = useAuth();

  // Filter navigation based on user role
  const filteredNavigation = navigation.filter(item => 
    user?.role && item.roles.includes(user.role)
  );

  return (
    <aside className="w-64 border-r border-border/50 bg-card/30 backdrop-blur-md flex flex-col">
      <div className="flex h-16 items-center gap-3 px-6 border-b border-border/50">
        <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
          <Activity className="h-6 w-6 text-primary-foreground" />
        </div>
        <div>
          <h1 className="text-lg font-bold">Smart Room</h1>
          <p className="text-xs text-muted-foreground">Control Center</p>
        </div>
      </div>
      
      <nav className="p-4 space-y-1 flex-1">
        {filteredNavigation.map((item) => (
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
            {item.name}
          </NavLink>
        ))}
      </nav>
      
      {/* User info and logout */}
      <div className="p-4 border-t border-border/50">
        <div className="flex items-center gap-3 mb-3">
          <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
            <span className="text-sm font-medium text-primary">
              {user?.full_name?.charAt(0) || user?.username?.charAt(0)}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.full_name || user?.username}</p>
            <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
          </div>
        </div>
        <Button 
          onClick={logout}
          variant="outline" 
          size="sm" 
          className="w-full gap-2"
        >
          <LogOut className="h-4 w-4" />
          Logout
        </Button>
      </div>
    </aside>
  );
};
