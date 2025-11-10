import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Users as UsersIcon, Shield, User, Building2 } from "lucide-react";

export default function Users() {
  const currentUser = {
    name: "Admin User",
    role: "admin",
    email: "admin@smartroom.ai",
    assignedRooms: [1, 2, 3, 4],
  };

  const users = [
    {
      id: 1,
      name: "Admin User",
      role: "admin",
      email: "admin@smartroom.ai",
      assignedRooms: [1, 2, 3, 4],
      lastActive: "Just now",
    },
    {
      id: 2,
      name: "Operator A",
      role: "operator",
      email: "operator.a@smartroom.ai",
      assignedRooms: [1, 2],
      lastActive: "5 mins ago",
    },
    {
      id: 3,
      name: "Operator B",
      role: "operator",
      email: "operator.b@smartroom.ai",
      assignedRooms: [3, 4],
      lastActive: "1 hour ago",
    },
  ];

  return (
    <div className="container mx-auto px-6 py-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <UsersIcon className="h-8 w-8 text-primary" />
          User Management
        </h1>
        <p className="text-muted-foreground mt-1">
          Manage user roles and room assignments
        </p>
      </div>

      {/* Current User */}
      <Card className="bg-gradient-to-br from-card to-card/80 border-primary/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Current User
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-lg font-semibold">{currentUser.name}</p>
              <p className="text-sm text-muted-foreground">{currentUser.email}</p>
            </div>
            <Badge variant="default" className="gap-2">
              <Shield className="h-3 w-3" />
              {currentUser.role.toUpperCase()}
            </Badge>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-2">Access Level</p>
            <p className="text-sm">
              {currentUser.role === "admin"
                ? "Full system access - All rooms and configurations"
                : `Limited to assigned rooms (${currentUser.assignedRooms.length} rooms)`}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* All Users */}
      <div>
        <h2 className="text-xl font-semibold mb-4">All Users</h2>
        <div className="grid gap-4">
          {users.map((user) => (
            <Card key={user.id} className="bg-gradient-to-br from-card to-card/80">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-lg">{user.name}</h3>
                      <Badge
                        variant={user.role === "admin" ? "default" : "secondary"}
                        className="gap-1"
                      >
                        {user.role === "admin" ? (
                          <Shield className="h-3 w-3" />
                        ) : (
                          <User className="h-3 w-3" />
                        )}
                        {user.role}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{user.email}</p>
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-muted-foreground" />
                        <span>
                          {user.role === "admin"
                            ? "All Rooms"
                            : `${user.assignedRooms.length} Rooms`}
                        </span>
                      </div>
                      <div className="text-muted-foreground">
                        Last active: {user.lastActive}
                      </div>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    Edit
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Role Descriptions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Shield className="h-5 w-5 text-primary" />
              Admin Role
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>✓ View all rooms and devices</li>
              <li>✓ Configure SLOs and weights</li>
              <li>✓ Manage AI agents</li>
              <li>✓ Access analytics and insights</li>
              <li>✓ Override any decision</li>
              <li>✓ User management</li>
            </ul>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-card to-card/80">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <User className="h-5 w-5 text-accent" />
              Operator Role
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>✓ View assigned rooms only</li>
              <li>✓ Monitor device status</li>
              <li>✓ View AI decisions</li>
              <li>✓ Override assigned room devices</li>
              <li>✗ Cannot modify SLOs</li>
              <li>✗ Cannot manage users</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
