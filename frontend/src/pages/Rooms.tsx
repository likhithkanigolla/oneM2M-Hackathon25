import { useNavigate } from "react-router-dom";
import { useRooms } from "@/store/useRooms";
import { RoomCard } from "@/components/RoomCard";
import { Building2 } from "lucide-react";

export default function Rooms() {
  const navigate = useNavigate();
  const { rooms, selectRoom } = useRooms();

  const handleRoomClick = (room: any) => {
    selectRoom(room);
    navigate(`/room/${room.id}`);
  };

  return (
    <div className="container mx-auto px-6 py-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Building2 className="h-8 w-8 text-primary" />
          All Rooms
        </h1>
        <p className="text-muted-foreground mt-1">
          Monitor and control all smart rooms in your facility
        </p>
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
