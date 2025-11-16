import { useNavigate } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import { useRooms, Room } from "@/store/useRooms";
import { useAuth } from "@/store/useAuth";
import { RoomCard } from "@/components/RoomCard";
import { Building2, RefreshCw, Plus, Edit2, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";

interface RoomFormData {
  name: string;
  gsi: number;
  aq: number;
  temp: number;
  occupancy: number;
  position?: { x: number; y: number };
}

export default function Rooms() {
  const navigate = useNavigate();
  const { rooms, selectRoom, fetchRooms, createRoom, updateRoom, deleteRoom } = useRooms();
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);
  
  const [formData, setFormData] = useState<RoomFormData>({
    name: '',
    gsi: 0.75,
    aq: 80,
    temp: 22,
    occupancy: 0,
    position: { x: 100, y: 100 },
  });

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

  // Check if user is admin
  const isAdmin = user?.role === 'admin';

  const handleRoomClick = (room: any) => {
    selectRoom(room);
    navigate(`/room/${room.id}`);
  };

  const handleRefresh = async () => {
    await fetchRooms();
  };

  const handleCreateRoom = async () => {
    if (!isAdmin) {
      toast({ title: "Unauthorized", description: "Only admins can create rooms", variant: "destructive" });
      return;
    }

    try {
      await createRoom(formData);
      toast({ title: "Success", description: "Room created successfully" });
      setIsCreateOpen(false);
      resetForm();
    } catch (error) {
      toast({ title: "Error", description: "Failed to create room", variant: "destructive" });
    }
  };

  const handleUpdateRoom = async () => {
    if (!isAdmin || !editingRoom) {
      toast({ title: "Unauthorized", description: "Only admins can update rooms", variant: "destructive" });
      return;
    }

    try {
      await updateRoom(editingRoom.id, formData);
      toast({ title: "Success", description: "Room updated successfully" });
      setIsEditOpen(false);
      setEditingRoom(null);
      resetForm();
    } catch (error) {
      toast({ title: "Error", description: "Failed to update room", variant: "destructive" });
    }
  };

  const handleDeleteRoom = async (id: number) => {
    if (!isAdmin) {
      toast({ title: "Unauthorized", description: "Only admins can delete rooms", variant: "destructive" });
      return;
    }

    try {
      await deleteRoom(id);
      toast({ title: "Success", description: "Room deleted successfully" });
    } catch (error) {
      toast({ title: "Error", description: "Failed to delete room", variant: "destructive" });
    }
  };

  const openEditDialog = (room: Room) => {
    setEditingRoom(room);
    setFormData({
      name: room.name,
      gsi: room.gsi,
      aq: room.aq,
      temp: room.temp,
      occupancy: room.occupancy,
      position: room.position,
    });
    setIsEditOpen(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      gsi: 0.75,
      aq: 80,
      temp: 22,
      occupancy: 0,
      position: { x: 100, y: 100 },
    });
  };

  const updateFormField = (field: keyof RoomFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="container mx-auto px-6 py-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Building2 className="h-8 w-8 text-primary" />
            BuildSense AI-IoT Platforms
          </h1>
          <p className="text-muted-foreground mt-1">
            {user?.role === 'admin' 
              ? `Manage and monitor all rooms (${filteredRooms.length} total)`
              : `Your assigned rooms (${filteredRooms.length} rooms)`}
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleRefresh} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          {isAdmin && (
            <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Room
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Create New Room</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="name">Room Name</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => updateFormField('name', e.target.value)}
                      placeholder="e.g., Conference Room C"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="gsi">GSI</Label>
                      <Input
                        id="gsi"
                        type="number"
                        min="0"
                        max="1"
                        step="0.01"
                        value={formData.gsi}
                        onChange={(e) => updateFormField('gsi', parseFloat(e.target.value) || 0)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="aq">Air Quality</Label>
                      <Input
                        id="aq"
                        type="number"
                        min="0"
                        max="100"
                        value={formData.aq}
                        onChange={(e) => updateFormField('aq', parseInt(e.target.value) || 0)}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="temp">Temperature (°C)</Label>
                      <Input
                        id="temp"
                        type="number"
                        min="0"
                        max="50"
                        value={formData.temp}
                        onChange={(e) => updateFormField('temp', parseFloat(e.target.value) || 0)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="occupancy">Occupancy</Label>
                      <Input
                        id="occupancy"
                        type="number"
                        min="0"
                        value={formData.occupancy}
                        onChange={(e) => updateFormField('occupancy', parseInt(e.target.value) || 0)}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="x">Position X</Label>
                      <Input
                        id="x"
                        type="number"
                        min="0"
                        value={formData.position?.x || 0}
                        onChange={(e) => updateFormField('position', { ...formData.position, x: parseInt(e.target.value) || 0 })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="y">Position Y</Label>
                      <Input
                        id="y"
                        type="number"
                        min="0"
                        value={formData.position?.y || 0}
                        onChange={(e) => updateFormField('position', { ...formData.position, y: parseInt(e.target.value) || 0 })}
                      />
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button onClick={handleCreateRoom} disabled={!formData.name}>
                    Create Room
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          )}
        </div>
      </div>

      {/* Rooms Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredRooms.length > 0 ? (
          filteredRooms.map((room) => (
            <RoomCard
              key={room.id}
              room={room}
              onClick={() => handleRoomClick(room)}
              showAdminActions={isAdmin}
              onEdit={openEditDialog}
              onDelete={(room) => {
                // Store room for deletion confirmation
                const confirmDelete = () => {
                  if (window.confirm(`Are you sure you want to delete "${room.name}"? This action cannot be undone.`)) {
                    handleDeleteRoom(room.id);
                  }
                };
                confirmDelete();
              }}
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
                ? 'Create your first room to get started.' 
                : 'Contact your administrator to assign rooms to your account.'}
            </p>
          </div>
        )}
      </div>

      {/* Edit Room Dialog */}
      <Dialog open={isEditOpen} onOpenChange={(open) => {
        setIsEditOpen(open);
        if (!open) {
          setEditingRoom(null);
          resetForm();
        }
      }}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Room: {editingRoom?.name}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-name">Room Name</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => updateFormField('name', e.target.value)}
                placeholder="e.g., Conference Room C"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-gsi">GSI</Label>
                <Input
                  id="edit-gsi"
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={formData.gsi}
                  onChange={(e) => updateFormField('gsi', parseFloat(e.target.value) || 0)}
                />
              </div>
              <div>
                <Label htmlFor="edit-aq">Air Quality</Label>
                <Input
                  id="edit-aq"
                  type="number"
                  min="0"
                  max="100"
                  value={formData.aq}
                  onChange={(e) => updateFormField('aq', parseInt(e.target.value) || 0)}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-temp">Temperature (°C)</Label>
                <Input
                  id="edit-temp"
                  type="number"
                  min="0"
                  max="50"
                  value={formData.temp}
                  onChange={(e) => updateFormField('temp', parseFloat(e.target.value) || 0)}
                />
              </div>
              <div>
                <Label htmlFor="edit-occupancy">Occupancy</Label>
                <Input
                  id="edit-occupancy"
                  type="number"
                  min="0"
                  value={formData.occupancy}
                  onChange={(e) => updateFormField('occupancy', parseInt(e.target.value) || 0)}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-x">Position X</Label>
                <Input
                  id="edit-x"
                  type="number"
                  min="0"
                  value={formData.position?.x || 0}
                  onChange={(e) => updateFormField('position', { ...formData.position, x: parseInt(e.target.value) || 0 })}
                />
              </div>
              <div>
                <Label htmlFor="edit-y">Position Y</Label>
                <Input
                  id="edit-y"
                  type="number"
                  min="0"
                  value={formData.position?.y || 0}
                  onChange={(e) => updateFormField('position', { ...formData.position, y: parseInt(e.target.value) || 0 })}
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button onClick={handleUpdateRoom} disabled={!formData.name}>
              Update Room
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Permission Notice for Operators */}
      {!isAdmin && (
        <Card className="bg-gradient-to-br from-muted/50 to-muted/30 border-dashed">
          <CardContent className="p-6 text-center">
            <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-muted-foreground mb-2">
              View Only Access
            </h3>
            <p className="text-muted-foreground">
              Room management is restricted to administrators. You can view room details and device status only.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
