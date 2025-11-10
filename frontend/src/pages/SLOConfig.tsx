import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Settings, Plus, Trash2, Edit, Shield, User } from "lucide-react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";
import { useSLOs } from "@/store/useSLOs";
import { useAuth } from "@/store/useAuth";

interface SLOFormData {
  name: string;
  description: string;
  target_value: number;
  metric: string;
  weight: number;
  active: boolean;
  is_system_defined: boolean;
}

export default function SLOConfig() {
  const { slos, loading, error, fetchSLOs, createSLO, updateSLO, deleteSLO } = useSLOs();
  const { user } = useAuth();
  const [editingSLO, setEditingSLO] = useState<any>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [sloForm, setSloForm] = useState<SLOFormData>({
    name: "",
    description: "",
    target_value: 0,
    metric: "",
    weight: 0.1,
    active: true,
    is_system_defined: false,
  });

  const isAdmin = user?.role === "admin";

  useEffect(() => {
    fetchSLOs();
  }, [fetchSLOs]);

  const resetForm = () => {
    setSloForm({
      name: "",
      description: "",
      target_value: 0,
      metric: "",
      weight: 0.1,
      active: true,
      is_system_defined: false,
    });
  };

  const updateSloForm = (field: keyof SLOFormData, value: any) => {
    setSloForm(prev => ({ ...prev, [field]: value }));
  };

  const openCreateDialog = () => {
    resetForm();
    setEditingSLO(null);
    setIsDialogOpen(true);
  };

  const openEditDialog = (slo: any) => {
    setSloForm({
      name: slo.name,
      description: slo.description || "",
      target_value: slo.target_value || 0,
      metric: slo.metric || "",
      weight: slo.weight,
      active: slo.active,
      is_system_defined: slo.is_system_defined,
    });
    setEditingSLO(slo);
    setIsDialogOpen(true);
  };

  const handleWeightChange = async (id: number, newWeight: number) => {
    try {
      await updateSLO(id, { weight: newWeight });
      toast.success("Weight updated successfully");
    } catch (error) {
      toast.error("Failed to update weight");
    }
  };

  const handleToggle = async (id: number) => {
    const slo = slos.find(s => s.id === id);
    if (!slo) return;

    try {
      await updateSLO(id, { active: !slo.active });
      toast.success(`SLO ${!slo.active ? 'activated' : 'deactivated'}`);
    } catch (error) {
      toast.error("Failed to update SLO status");
    }
  };

  const handleCreateSLO = async () => {
    try {
      await createSLO(sloForm);
      toast.success("SLO created successfully");
      setIsDialogOpen(false);
      resetForm();
    } catch (error) {
      toast.error("Failed to create SLO");
    }
  };

  const handleUpdateSLO = async () => {
    if (!editingSLO) return;

    try {
      await updateSLO(editingSLO.id, sloForm);
      toast.success("SLO updated successfully");
      setIsDialogOpen(false);
      resetForm();
      setEditingSLO(null);
    } catch (error) {
      toast.error("Failed to update SLO");
    }
  };

  const handleDeleteSLO = async (id: number) => {
    try {
      await deleteSLO(id);
      toast.success("SLO deleted successfully");
      setDeletingId(null);
    } catch (error) {
      toast.error("Failed to delete SLO");
    }
  };

  const canEditSLO = (slo: any) => {
    return isAdmin || slo.created_by === user?.username;
  };

  const canDeleteSLO = (slo: any) => {
    if (isAdmin) return true;
    if (slo.is_system_defined) return false;
    return slo.created_by === user?.username;
  };

  const getDeleteWarning = (slo: any) => {
    if (slo.is_system_defined) {
      return "This is a system-defined SLO. Only administrators can delete it.";
    }
    return "Are you sure you want to delete this SLO? This action cannot be undone.";
  };

  const totalWeight = slos.reduce((sum, slo) => sum + slo.weight, 0);

  if (loading) {
    return (
      <div className="container mx-auto px-6 py-6">
        <div className="text-center">Loading SLOs...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Settings className="h-8 w-8 text-primary" />
            SLO Configuration
          </h1>
          <p className="text-muted-foreground mt-1">
            Define and manage Service Level Objectives
          </p>
        </div>
        <Button onClick={openCreateDialog} className="gap-2">
          <Plus className="h-4 w-4" />
          Add SLO
        </Button>
      </div>

      {/* Weight Summary */}
      <Card className="bg-gradient-to-br from-card to-card/80">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Weight</p>
              <p className="text-3xl font-bold">{totalWeight.toFixed(2)}</p>
            </div>
            {Math.abs(totalWeight - 1) > 0.01 && (
              <div className="text-warning text-sm flex items-center gap-2">
                ⚠️ Weights should sum to 1.0
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* SLO List */}
      <div className="grid gap-4">
        {slos.map((slo) => (
          <Card key={slo.id} className="bg-gradient-to-br from-card to-card/80">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="flex items-center gap-3">
                    {slo.name}
                    <div className="flex items-center gap-2">
                      {slo.is_system_defined && (
                        <Badge variant="outline" className="text-xs">
                          <Shield className="h-3 w-3 mr-1" />
                          System
                        </Badge>
                      )}
                      <Badge variant="secondary" className="text-xs">
                        <User className="h-3 w-3 mr-1" />
                        {slo.created_by}
                      </Badge>
                      {!slo.active && (
                        <Badge variant="destructive" className="text-xs">
                          Inactive
                        </Badge>
                      )}
                    </div>
                  </CardTitle>
                  <p className="text-sm text-muted-foreground mt-1">
                    {slo.description}
                  </p>
                  {slo.metric && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Metric: {slo.metric} | Target: {slo.target_value}
                    </p>
                  )}
                </div>
                <Switch 
                  checked={slo.active} 
                  onCheckedChange={() => handleToggle(slo.id)}
                  disabled={!canEditSLO(slo)}
                />
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-sm">Weight</Label>
                  <span className="text-sm font-mono font-bold">
                    {(slo.weight * 100).toFixed(0)}%
                  </span>
                </div>
                <Slider
                  value={[slo.weight]}
                  onValueChange={([value]) => handleWeightChange(slo.id, value)}
                  min={0}
                  max={1}
                  step={0.05}
                  disabled={!slo.active || !canEditSLO(slo)}
                />
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => openEditDialog(slo)}
                  className="gap-2"
                  disabled={!canEditSLO(slo)}
                >
                  <Edit className="h-3 w-3" />
                  Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setDeletingId(slo.id)}
                  className="gap-2 text-destructive hover:text-destructive"
                  disabled={!canDeleteSLO(slo)}
                >
                  <Trash2 className="h-3 w-3" />
                  Delete
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Create/Edit SLO Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingSLO ? "Edit SLO" : "Create New SLO"}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="slo-name">Name</Label>
              <Input
                id="slo-name"
                value={sloForm.name}
                onChange={(e) => updateSloForm('name', e.target.value)}
                placeholder="e.g., Energy Efficiency"
              />
            </div>
            <div>
              <Label htmlFor="slo-description">Description</Label>
              <Textarea
                id="slo-description"
                value={sloForm.description}
                onChange={(e) => updateSloForm('description', e.target.value)}
                placeholder="Describe the objective..."
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="slo-metric">Metric</Label>
                <Select value={sloForm.metric} onValueChange={(value) => updateSloForm('metric', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select metric type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="energy_consumption">Energy Consumption</SelectItem>
                    <SelectItem value="comfort_score">Comfort Score</SelectItem>
                    <SelectItem value="reliability_score">Reliability Score</SelectItem>
                    <SelectItem value="response_time">Response Time</SelectItem>
                    <SelectItem value="uptime">Uptime</SelectItem>
                    <SelectItem value="custom">Custom</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="slo-target">Target Value</Label>
                <Input
                  id="slo-target"
                  type="number"
                  step="0.1"
                  value={sloForm.target_value}
                  onChange={(e) => updateSloForm('target_value', parseFloat(e.target.value) || 0)}
                  placeholder="0.95"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="slo-weight">Weight: {sloForm.weight.toFixed(2)}</Label>
              <Slider
                value={[sloForm.weight]}
                onValueChange={([value]) => updateSloForm('weight', value)}
                min={0}
                max={1}
                step={0.05}
                className="mt-2"
              />
            </div>
            {isAdmin && (
              <div className="flex items-center justify-between">
                <Label htmlFor="system-defined">System Defined</Label>
                <Switch
                  id="system-defined"
                  checked={sloForm.is_system_defined}
                  onCheckedChange={(checked) => updateSloForm('is_system_defined', checked)}
                />
              </div>
            )}
            <div className="flex items-center justify-between">
              <Label htmlFor="slo-active">Active</Label>
              <Switch
                id="slo-active"
                checked={sloForm.active}
                onCheckedChange={(checked) => updateSloForm('active', checked)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button 
              onClick={editingSLO ? handleUpdateSLO : handleCreateSLO}
              disabled={!sloForm.name || !sloForm.metric}
            >
              {editingSLO ? "Update SLO" : "Create SLO"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deletingId !== null} onOpenChange={() => setDeletingId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete SLO</AlertDialogTitle>
            <AlertDialogDescription>
              {deletingId && getDeleteWarning(slos.find(s => s.id === deletingId))}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deletingId && handleDeleteSLO(deletingId)}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
