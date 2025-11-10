import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Brain, Plus, Edit2, Trash2, Bot, RefreshCw } from "lucide-react";
import { useAgents, Agent } from "@/store/useAgents";
import { useAuth } from "@/store/useAuth";
import { useToast } from "@/hooks/use-toast";

interface AgentFormData {
  id: string;
  name: string;
  goal: string;
  rag_sources: string[];
  active: boolean;
  endpoint?: string;
  weight: number;
}

export default function Agents() {
  const { agents, fetchAgents, createAgent, updateAgent, deleteAgent, toggleAgent } = useAgents();
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  
  const [formData, setFormData] = useState<AgentFormData>({
    id: '',
    name: '',
    goal: '',
    rag_sources: [],
    active: true,
    endpoint: '',
    weight: 0.33,
  });

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  // Check if user is admin
  const isAdmin = user?.role === 'admin';

  const handleCreateAgent = async () => {
    if (!isAdmin) {
      toast({ title: "Unauthorized", description: "Only admins can create agents", variant: "destructive" });
      return;
    }

    try {
      await createAgent(formData);
      toast({ title: "Success", description: "Agent created successfully" });
      setIsCreateOpen(false);
      resetForm();
    } catch (error) {
      toast({ title: "Error", description: "Failed to create agent", variant: "destructive" });
    }
  };

  const handleUpdateAgent = async () => {
    if (!isAdmin || !editingAgent) {
      toast({ title: "Unauthorized", description: "Only admins can update agents", variant: "destructive" });
      return;
    }

    try {
      await updateAgent(editingAgent.id, formData);
      toast({ title: "Success", description: "Agent updated successfully" });
      setIsEditOpen(false);
      setEditingAgent(null);
      resetForm();
    } catch (error) {
      toast({ title: "Error", description: "Failed to update agent", variant: "destructive" });
    }
  };

  const handleDeleteAgent = async (id: string) => {
    if (!isAdmin) {
      toast({ title: "Unauthorized", description: "Only admins can delete agents", variant: "destructive" });
      return;
    }

    try {
      await deleteAgent(id);
      toast({ title: "Success", description: "Agent deleted successfully" });
    } catch (error) {
      toast({ title: "Error", description: "Failed to delete agent", variant: "destructive" });
    }
  };

  const handleToggleAgent = async (id: string) => {
    try {
      await toggleAgent(id);
      toast({ title: "Success", description: "Agent status updated" });
    } catch (error) {
      toast({ title: "Error", description: "Failed to update agent status", variant: "destructive" });
    }
  };

  const openEditDialog = (agent: Agent) => {
    setEditingAgent(agent);
    setFormData({
      id: agent.id,
      name: agent.name,
      goal: agent.goal,
      rag_sources: agent.rag_sources,
      active: agent.active,
      endpoint: agent.endpoint || '',
      weight: agent.weight,
    });
    setIsEditOpen(true);
  };

  const resetForm = () => {
    setFormData({
      id: '',
      name: '',
      goal: '',
      rag_sources: [],
      active: true,
      endpoint: '',
      weight: 0.33,
    });
  };

  const updateFormField = (field: keyof AgentFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const updateRagSources = (value: string) => {
    const sources = value.split(',').map(s => s.trim()).filter(s => s);
    updateFormField('rag_sources', sources);
  };

  return (
    <div className="container mx-auto px-6 py-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Bot className="h-8 w-8 text-primary" />
            AI Agents
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage AI decision-making agents ({agents.length} total, {agents.filter(a => a.active).length} active)
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={fetchAgents} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          {isAdmin && (
            <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Agent
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Create New Agent</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="id">Agent ID</Label>
                    <Input
                      id="id"
                      value={formData.id}
                      onChange={(e) => updateFormField('id', e.target.value)}
                      placeholder="e.g., gemini, claude, gpt"
                    />
                  </div>
                  <div>
                    <Label htmlFor="name">Name</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => updateFormField('name', e.target.value)}
                      placeholder="Agent display name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="goal">Goal</Label>
                    <Textarea
                      id="goal"
                      value={formData.goal}
                      onChange={(e) => updateFormField('goal', e.target.value)}
                      placeholder="Agent's primary objective"
                      rows={2}
                    />
                  </div>
                  <div>
                    <Label htmlFor="rag_sources">RAG Sources</Label>
                    <Input
                      id="rag_sources"
                      value={formData.rag_sources.join(', ')}
                      onChange={(e) => updateRagSources(e.target.value)}
                      placeholder="sensor, comfort, energy (comma-separated)"
                    />
                  </div>
                  <div>
                    <Label htmlFor="weight">Weight</Label>
                    <Input
                      id="weight"
                      type="number"
                      min="0"
                      max="1"
                      step="0.01"
                      value={formData.weight}
                      onChange={(e) => updateFormField('weight', parseFloat(e.target.value) || 0)}
                      placeholder="Decision weight (0-1)"
                    />
                  </div>
                  <div>
                    <Label htmlFor="endpoint">Endpoint (Optional)</Label>
                    <Input
                      id="endpoint"
                      value={formData.endpoint}
                      onChange={(e) => updateFormField('endpoint', e.target.value)}
                      placeholder="API endpoint URL"
                    />
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="active"
                      checked={formData.active}
                      onCheckedChange={(checked) => updateFormField('active', checked)}
                    />
                    <Label htmlFor="active">Active</Label>
                  </div>
                </div>
                <DialogFooter>
                  <Button onClick={handleCreateAgent} disabled={!formData.id || !formData.name}>
                    Create Agent
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          )}
        </div>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <Card key={agent.id} className="bg-gradient-to-br from-card to-card/80">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-primary/20 flex items-center justify-center">
                    <Brain className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{agent.name}</CardTitle>
                    <Badge variant={agent.active ? "default" : "secondary"} className="text-xs">
                      {agent.active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                </div>
                {isAdmin && (
                  <div className="flex gap-1">
                    <Button variant="ghost" size="sm" onClick={() => openEditDialog(agent)}>
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Delete Agent</AlertDialogTitle>
                          <AlertDialogDescription>
                            Are you sure you want to delete "{agent.name}"? This action cannot be undone.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction onClick={() => handleDeleteAgent(agent.id)}>
                            Delete
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Goal</p>
                <p className="text-sm">{agent.goal}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">RAG Sources</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {agent.rag_sources.map((source, idx) => (
                    <Badge key={idx} variant="outline" className="text-xs">
                      {source}
                    </Badge>
                  ))}
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Weight</p>
                  <p className="text-sm font-mono">{(agent.weight * 100).toFixed(1)}%</p>
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={agent.active}
                    onCheckedChange={() => handleToggleAgent(agent.id)}
                    disabled={!isAdmin}
                  />
                  <Label className="text-xs">Active</Label>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Edit Dialog */}
      <Dialog open={isEditOpen} onOpenChange={(open) => {
        setIsEditOpen(open);
        if (!open) {
          setEditingAgent(null);
          resetForm();
        }
      }}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Agent: {editingAgent?.name}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-name">Name</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => updateFormField('name', e.target.value)}
                placeholder="Agent display name"
              />
            </div>
            <div>
              <Label htmlFor="edit-goal">Goal</Label>
              <Textarea
                id="edit-goal"
                value={formData.goal}
                onChange={(e) => updateFormField('goal', e.target.value)}
                placeholder="Agent's primary objective"
                rows={2}
              />
            </div>
            <div>
              <Label htmlFor="edit-rag_sources">RAG Sources</Label>
              <Input
                id="edit-rag_sources"
                value={formData.rag_sources.join(', ')}
                onChange={(e) => updateRagSources(e.target.value)}
                placeholder="sensor, comfort, energy (comma-separated)"
              />
            </div>
            <div>
              <Label htmlFor="edit-weight">Weight</Label>
              <Input
                id="edit-weight"
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={formData.weight}
                onChange={(e) => updateFormField('weight', parseFloat(e.target.value) || 0)}
                placeholder="Decision weight (0-1)"
              />
            </div>
            <div>
              <Label htmlFor="edit-endpoint">Endpoint (Optional)</Label>
              <Input
                id="edit-endpoint"
                value={formData.endpoint}
                onChange={(e) => updateFormField('endpoint', e.target.value)}
                placeholder="API endpoint URL"
              />
            </div>
            <div className="flex items-center space-x-2">
              <Switch
                id="edit-active"
                checked={formData.active}
                onCheckedChange={(checked) => updateFormField('active', checked)}
              />
              <Label htmlFor="edit-active">Active</Label>
            </div>
          </div>
          <DialogFooter>
            <Button onClick={handleUpdateAgent} disabled={!formData.name}>
              Update Agent
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Permission Notice for Operators */}
      {!isAdmin && (
        <Card className="bg-gradient-to-br from-muted/50 to-muted/30 border-dashed">
          <CardContent className="p-6 text-center">
            <Brain className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-muted-foreground mb-2">
              View Only Access
            </h3>
            <p className="text-muted-foreground">
              Agent management is restricted to administrators. You can view agent details and toggle activation status only.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}