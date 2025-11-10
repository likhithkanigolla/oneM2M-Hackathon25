import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useRooms, Room } from "@/store/useRooms";
import { Map } from "lucide-react";
import { cn } from "@/lib/utils";

export const RoomMap = () => {
  const { rooms, selectRoom } = useRooms();

  const getGSIColor = (gsi: number) => {
    if (gsi >= 0.8) return "fill-energy";
    if (gsi >= 0.6) return "fill-reliability";
    return "fill-danger";
  };

  const handleRoomClick = (room: Room) => {
    selectRoom(room);
  };

  return (
    <Card className="bg-gradient-to-br from-card to-card/80">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <Map className="h-5 w-5 text-primary" />
          Facility Layout
        </CardTitle>
      </CardHeader>
      <CardContent>
        <svg
          viewBox="0 0 600 500"
          className="w-full h-full border border-border/50 rounded-lg bg-background/50"
        >
          {/* Grid background */}
          <defs>
            <pattern
              id="grid"
              width="20"
              height="20"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 20 0 L 0 0 0 20"
                fill="none"
                stroke="hsl(var(--border))"
                strokeWidth="0.5"
                opacity="0.3"
              />
            </pattern>
          </defs>
          <rect width="600" height="500" fill="url(#grid)" />

          {/* Rooms */}
          {rooms.map((room) => {
            const x = room.position?.x || 0;
            const y = room.position?.y || 0;
            const width = 200;
            const height = 150;

            return (
              <g
                key={room.id}
                onClick={() => handleRoomClick(room)}
                className="cursor-pointer group"
              >
                <rect
                  x={x}
                  y={y}
                  width={width}
                  height={height}
                  className={cn(
                    "transition-all stroke-primary/50",
                    getGSIColor(room.gsi),
                    "fill-opacity-10 hover:fill-opacity-20 group-hover:stroke-primary"
                  )}
                  strokeWidth="2"
                  rx="8"
                />
                
                {/* Room label */}
                <text
                  x={x + width / 2}
                  y={y + 30}
                  textAnchor="middle"
                  className="fill-foreground text-sm font-semibold pointer-events-none"
                >
                  {room.name}
                </text>

                {/* GSI Badge */}
                <g transform={`translate(${x + 10}, ${y + 10})`}>
                  <rect
                    width="50"
                    height="20"
                    rx="4"
                    className="fill-background/90"
                  />
                  <text
                    x="25"
                    y="14"
                    textAnchor="middle"
                    className={cn(
                      "text-xs font-mono font-bold pointer-events-none",
                      getGSIColor(room.gsi).replace('fill-', 'fill-')
                    )}
                  >
                    {(room.gsi * 100).toFixed(0)}
                  </text>
                </g>

                {/* Device indicators */}
                <g transform={`translate(${x + 20}, ${y + 60})`}>
                  {room.devices.map((device, idx) => (
                    <g key={device.name} transform={`translate(${idx * 40}, 0)`}>
                      <circle
                        r="8"
                        className={cn(
                          "transition-all",
                          device.status === "ON"
                            ? "fill-energy animate-pulse-slow"
                            : "fill-muted"
                        )}
                      />
                      <text
                        y="25"
                        textAnchor="middle"
                        className="fill-muted-foreground text-xs pointer-events-none"
                      >
                        {device.name.slice(0, 3)}
                      </text>
                    </g>
                  ))}
                </g>

                {/* Stats */}
                <text
                  x={x + 20}
                  y={y + 120}
                  className="fill-muted-foreground text-xs pointer-events-none"
                >
                  {room.temp}°C • AQ {room.aq} • {room.occupancy} people
                </text>
              </g>
            );
          })}
        </svg>
      </CardContent>
    </Card>
  );
};
