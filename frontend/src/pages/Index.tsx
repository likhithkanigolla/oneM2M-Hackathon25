import { useNavigate } from "react-router-dom";
import { RoomCard } from "@/components/RoomCard";
import { GSIIndicator } from "@/components/GSIIndicator";
import { AgentCard } from "@/components/AgentCard";
import { ScenarioPanel } from "@/components/ScenarioPanel";
import { RoomMap } from "@/components/RoomMap";
import { useRooms } from "@/store/useRooms";
import { useAgents } from "@/store/useAgents";
import { Brain } from "lucide-react";

const Index = () => {
  const navigate = useNavigate();
  const { rooms, selectRoom } = useRooms();
  const { agents, toggleAgent } = useAgents();

  const handleRoomClick = (room: any) => {
    selectRoom(room);
    navigate(`/room/${room.id}`);
  };

  return (
    <div className="container mx-auto px-6 py-6 space-y-6 animate-fade-in">
      {/* Top Row: GSI + Active Scenarios */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GSIIndicator />
        <div className="lg:col-span-2">
          <ScenarioPanel />
        </div>
      </div>

      {/* Room Map */}
      <RoomMap />

      {/* Agents Section */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Brain className="h-5 w-5 text-accent" />
          <h2 className="text-xl font-semibold">AI Decision Agents</h2>
          <span className="text-sm text-muted-foreground ml-2">
            ({agents.filter((a) => a.active).length} active)
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onToggle={() => toggleAgent(agent.id)}
            />
          ))}
        </div>
      </div>

      {/* Rooms Grid */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Room Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {rooms.map((room) => (
            <RoomCard
              key={room.id}
              room={room}
              onClick={() => handleRoomClick(room)}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Index;
