import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { useRooms } from "@/store/useRooms";
import { RoomCard } from "@/components/RoomCard";
import { Building2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Rooms() {
  const navigate = useNavigate();
  const { rooms, selectRoom, fetchRooms } = useRooms();

  useEffect(() => {
    fetchRooms();
  }, [fetchRooms]);

  const handleRoomClick = (room: any) => {
    selectRoom(room);
    navigate(`/room/${room.id}`);
  };

  const handleRefresh = async () => {
    await fetchRooms();
  };

  return (
    <div className="container mx-auto px-6 py-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Building2 className="h-8 w-8 text-primary" />
            All Rooms
          </h1>
          <p className="text-muted-foreground mt-1">
            Monitor and control all smart rooms in your facility
          </p>
        </div>
        <Button onClick={handleRefresh} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Rooms Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {rooms.map((room) => (
          <RoomCard
            key={room.id}
            room={room}
            onClick={() => handleRoomClick(room)}
          />
        ))}
      </div>
    </div>
  );
}
