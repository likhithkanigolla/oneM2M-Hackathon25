import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Room } from "@/store/useRooms";
import { Users, Thermometer, Wind } from "lucide-react";
import { cn } from "@/lib/utils";

interface RoomCardProps {
  room: Room;
  onClick: () => void;
}

const getGSIColor = (gsi: number) => {
  if (gsi >= 0.8) return "success";
  if (gsi >= 0.6) return "warning";
  return "danger";
};

const getGSIGlow = (gsi: number) => {
  if (gsi >= 0.8) return "glow-energy";
  if (gsi >= 0.6) return "glow-reliability";
  return "glow-comfort";
};

export const RoomCard = ({ room, onClick }: RoomCardProps) => {
  const gsiColor = getGSIColor(room.gsi);
  const gsiGlow = getGSIGlow(room.gsi);

  return (
    <Card
      className={cn(
        "cursor-pointer transition-all hover:scale-[1.02] hover:border-primary/50",
        "bg-gradient-to-br from-card to-card/80 backdrop-blur-sm",
        gsiGlow
      )}
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg font-semibold">{room.name}</CardTitle>
          <Badge
            variant="outline"
            className={cn(
              "font-mono text-sm",
              gsiColor === "success" && "border-energy text-energy",
              gsiColor === "warning" && "border-reliability text-reliability",
              gsiColor === "danger" && "border-danger text-danger"
            )}
          >
            GSI {(room.gsi * 100).toFixed(0)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-3 gap-3">
          <div className="flex flex-col items-center gap-1 rounded-lg bg-muted/50 p-2">
            <Thermometer className="h-4 w-4 text-comfort" />
            <span className="text-xs text-muted-foreground">Temp</span>
            <span className="text-sm font-semibold">{room.temp}°C</span>
          </div>
          <div className="flex flex-col items-center gap-1 rounded-lg bg-muted/50 p-2">
            <Wind className="h-4 w-4 text-comfort" />
            <span className="text-xs text-muted-foreground">AQ</span>
            <span className="text-sm font-semibold">{room.aq}</span>
          </div>
          <div className="flex flex-col items-center gap-1 rounded-lg bg-muted/50 p-2">
            <Users className="h-4 w-4 text-accent" />
            <span className="text-xs text-muted-foreground">People</span>
            <span className="text-sm font-semibold">{room.occupancy}</span>
          </div>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Devices</span>
          <div className="flex gap-1">
            {room.devices.map((device) => (
              <div
                key={device.name}
                className={cn(
                  "h-2 w-2 rounded-full",
                  device.status === "ON" ? "bg-energy animate-pulse-slow" : "bg-muted"
                )}
                title={`${device.name}: ${device.status}`}
              />
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
