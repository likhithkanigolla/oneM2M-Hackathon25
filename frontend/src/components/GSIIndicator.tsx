import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useRooms } from "@/store/useRooms";
import { cn } from "@/lib/utils";

export const GSIIndicator = () => {
  const { rooms } = useRooms();
  
  const averageGSI = rooms.reduce((sum, room) => sum + room.gsi, 0) / rooms.length;
  const gsiPercentage = (averageGSI * 100).toFixed(1);
  
  const getGSIColor = (gsi: number) => {
    if (gsi >= 0.8) return { color: "energy", label: "Excellent" };
    if (gsi >= 0.6) return { color: "reliability", label: "Good" };
    if (gsi >= 0.4) return { color: "warning", label: "Fair" };
    return { color: "danger", label: "Poor" };
  };

  const gsiStatus = getGSIColor(averageGSI);

  return (
    <Card className="bg-gradient-to-br from-card to-card/80">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          Global Satisfaction Index
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="relative h-32 w-32 mx-auto">
          <svg className="h-full w-full -rotate-90" viewBox="0 0 120 120">
            <circle
              cx="60"
              cy="60"
              r="50"
              fill="none"
              stroke="hsl(var(--muted))"
              strokeWidth="10"
            />
            <circle
              cx="60"
              cy="60"
              r="50"
              fill="none"
              stroke={`hsl(var(--${gsiStatus.color}))`}
              strokeWidth="10"
              strokeDasharray={`${2 * Math.PI * 50}`}
              strokeDashoffset={`${2 * Math.PI * 50 * (1 - averageGSI)}`}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-bold">{gsiPercentage}</span>
            <span className="text-xs text-muted-foreground">%</span>
          </div>
        </div>
        <div className="text-center">
          <span
            className={cn(
              "inline-block rounded-full px-3 py-1 text-sm font-medium",
              `bg-${gsiStatus.color}/10 text-${gsiStatus.color}`
            )}
          >
            {gsiStatus.label}
          </span>
        </div>
      </CardContent>
    </Card>
  );
};
