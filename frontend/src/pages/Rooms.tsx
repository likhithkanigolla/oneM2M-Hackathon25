import { useNavigate } from "react-router-dom";
import { useEffect, useMemo } from "react";
import { useRooms } from "@/store/useRooms";
import { useAuth } from "@/store/useAuth";
import { RoomCard } from "@/components/RoomCard";
import { Building2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Rooms() {
  const navigate = useNavigate();
  const { rooms, selectRoom, fetchRooms } = useRooms();
  const { user } = useAuth();

  useEffect(() => {
    fetchRooms();
  }, [fetchRooms]);

  // Filter rooms based on user role and assignments
  const filteredRooms = useMemo(() => {
    if (!user) return [];
    
    if (user.role === 'admin') {
      // Admin can see all rooms
      return rooms;
    } else {
      // Operator can only see assigned rooms
      const assignedRoomIds = user.assigned_rooms || [];
      return rooms.filter(room => assignedRoomIds.includes(room.id));
    }
  }, [rooms, user]);

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
            Smart Rooms
          </h1>
          <p className="text-muted-foreground mt-1">
            {user?.role === 'admin' 
              ? `Manage and monitor all rooms (${filteredRooms.length} total)`
              : `Your assigned rooms (${filteredRooms.length} rooms)`}
          </p>
        </div>
        <Button onClick={handleRefresh} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Rooms Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredRooms.length > 0 ? (
          filteredRooms.map((room) => (
            <RoomCard
              key={room.id}
              room={room}
              onClick={() => handleRoomClick(room)}
            />
          ))
        ) : (
          <div className="col-span-full text-center py-8">
            <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-muted-foreground">
              {user?.role === 'admin' ? 'No rooms found' : 'No rooms assigned'}
            </h3>
            <p className="text-muted-foreground">
              {user?.role === 'admin' 
                ? 'Contact your administrator to set up rooms.' 
                : 'Contact your administrator to assign rooms to your account.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
