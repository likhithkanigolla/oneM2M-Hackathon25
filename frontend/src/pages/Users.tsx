import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { Users as UsersIcon, Shield, User, Plus, Edit2, Trash2, Building2 } from "lucide-react";
import { useAuth } from "@/store/useAuth";

interface User {
  id: number;
  username: string;
  full_name: string;
  role: string;
  assigned_rooms?: number[];
}

interface Room {
  id: number;
  name: string;
}

export default function Users() {
  const { user: currentUser, token } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isRoomAssignOpen, setIsRoomAssignOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [assigningRoomsUser, setAssigningRoomsUser] = useState<User | null>(null);
  const [selectedRooms, setSelectedRooms] = useState<number[]>([]);
  const [formData, setFormData] = useState({
    username: "",
    full_name: "",
    password: "",
    role: "operator"
  });

  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const fetchUsers = async () => {
    try {
      if (!token) {
        console.error('No token available');
        setLoading(false);
        return;
      }
      
      const response = await fetch(`${API_BASE}/api/auth/users`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRooms = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/rooms/`);
      if (response.ok) {
        const data = await response.json();
        setRooms(data);
      }
    } catch (error) {
      console.error('Error fetching rooms:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (!token) {
        console.error('No token available');
        return;
      }

      const url = editingUser 
        ? `${API_BASE}/api/auth/users/${editingUser.id}` 
        : `${API_BASE}/api/auth/register`;
        
      const method = editingUser ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        fetchUsers();
        setIsDialogOpen(false);
        setEditingUser(null);
        setFormData({ username: "", full_name: "", password: "", role: "operator" });
      }
    } catch (error) {
      console.error('Error saving user:', error);
    }
  };

  const handleDelete = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user?')) return;
    
    try {
      if (!token) {
        console.error('No token available');
        return;
      }

      const response = await fetch(`${API_BASE}/api/auth/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        fetchUsers();
      }
    } catch (error) {
      console.error('Error deleting user:', error);
    }
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      full_name: user.full_name,
      password: "",
      role: user.role
    });
    setIsDialogOpen(true);
  };

  const resetForm = () => {
    setFormData({ username: "", full_name: "", password: "", role: "operator" });
    setEditingUser(null);
  };

  const handleAssignRooms = (user: User) => {
    setAssigningRoomsUser(user);
    setSelectedRooms(user.assigned_rooms || []);
    setIsRoomAssignOpen(true);
  };

  const saveRoomAssignments = async () => {
    if (!assigningRoomsUser || !token) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/auth/users/${assigningRoomsUser.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          assigned_rooms: selectedRooms
        }),
      });

      if (response.ok) {
        fetchUsers();
        setIsRoomAssignOpen(false);
        setAssigningRoomsUser(null);
      }
    } catch (error) {
      console.error('Error saving room assignments:', error);
    }
  };

  useEffect(() => {
    if (token) {
      fetchUsers();
      fetchRooms();
    }
  }, [token]);

  return (
    <div className="container mx-auto px-6 py-6 space-y-6 animate-fade-in">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <UsersIcon className="h-8 w-8 text-primary" />
            User Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage system users and their roles
          </p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={resetForm}>
              <Plus className="h-4 w-4 mr-2" />
              Add User
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>{editingUser ? 'Edit User' : 'Add New User'}</DialogTitle>
              <DialogDescription>
                {editingUser ? 'Update user information and role.' : 'Create a new user account.'}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                  disabled={!!editingUser}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="full_name">Full Name</Label>
                <Input
                  id="full_name"
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  required
                />
              </div>
              {!editingUser && (
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    required
                  />
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="role">Role</Label>
                <Select value={formData.role} onValueChange={(value) => setFormData({...formData, role: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="operator">Operator</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit">
                  {editingUser ? 'Update' : 'Create'} User
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card className="bg-gradient-to-br from-card to-card/80 border-primary/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Current User
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-primary/20 flex items-center justify-center">
              <span className="text-lg font-semibold text-primary">
                {currentUser?.full_name?.charAt(0) || currentUser?.username?.charAt(0)}
              </span>
            </div>
            <div>
              <p className="font-semibold">{currentUser?.full_name}</p>
              <p className="text-sm text-muted-foreground">@{currentUser?.username}</p>
              <Badge variant={currentUser?.role === 'admin' ? 'default' : 'secondary'} className="mt-1">
                <Shield className="h-3 w-3 mr-1" />
                {currentUser?.role}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>All Users ({users.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-16 bg-muted rounded-lg"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {users.map((user) => (
                <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center">
                      <span className="font-medium text-primary">
                        {user.full_name?.charAt(0) || user.username?.charAt(0)}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium">{user.full_name}</p>
                      <p className="text-sm text-muted-foreground">@{user.username}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant={user.role === 'admin' ? 'default' : 'secondary'}>
                      {user.role}
                    </Badge>
                    <div className="text-sm text-muted-foreground">
                      {user.assigned_rooms && user.assigned_rooms.length > 0 
                        ? `${user.assigned_rooms.length} room(s)` 
                        : 'No rooms assigned'}
                    </div>
                    {currentUser?.role === 'admin' && (
                      <div className="flex gap-2">
                        <Button 
                          size="sm" 
                          variant="outline" 
                          onClick={() => handleAssignRooms(user)}
                          className="gap-1"
                        >
                          <Building2 className="h-4 w-4" />
                          Assign
                        </Button>
                        {user.id !== currentUser.id && (
                          <>
                            <Button size="sm" variant="outline" onClick={() => handleEdit(user)}>
                              <Edit2 className="h-4 w-4" />
                            </Button>
                            <Button size="sm" variant="outline" onClick={() => handleDelete(user.id)}>
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Room Assignment Dialog */}
      <Dialog open={isRoomAssignOpen} onOpenChange={setIsRoomAssignOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Assign Rooms to {assigningRoomsUser?.full_name}</DialogTitle>
            <DialogDescription>
              Select the rooms this user can access and manage.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 max-h-60 overflow-y-auto">
            {rooms.map((room) => (
              <div key={room.id} className="flex items-center space-x-2">
                <Checkbox
                  id={`room-${room.id}`}
                  checked={selectedRooms.includes(room.id)}
                  onCheckedChange={(checked) => {
                    if (checked) {
                      setSelectedRooms([...selectedRooms, room.id]);
                    } else {
                      setSelectedRooms(selectedRooms.filter(id => id !== room.id));
                    }
                  }}
                />
                <Label htmlFor={`room-${room.id}`} className="flex-1">
                  {room.name}
                </Label>
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setIsRoomAssignOpen(false)}>
              Cancel
            </Button>
            <Button onClick={saveRoomAssignments}>
              Save Assignments
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
