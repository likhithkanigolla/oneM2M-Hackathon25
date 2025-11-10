import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Settings, Plus, Trash2, Edit } from "lucide-react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

interface SLO {
  id: string;
  name: string;
  description: string;
  weight: number;
  active: boolean;
}

export default function SLOConfig() {
  const [slos, setSlos] = useState<SLO[]>([
    {
      id: "1",
      name: "Comfort",
      description: "Maintain optimal temperature and air quality for occupant satisfaction",
      weight: 0.4,
      active: true,
    },
    {
      id: "2",
      name: "Energy Efficiency",
      description: "Minimize power consumption while meeting operational requirements",
      weight: 0.3,
      active: true,
    },
    {
      id: "3",
      name: "Reliability",
      description: "Ensure consistent device operation and system uptime",
      weight: 0.3,
      active: true,
    },
  ]);

  const [editingSLO, setEditingSLO] = useState<SLO | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleWeightChange = (id: string, newWeight: number) => {
    setSlos((prev) =>
      prev.map((slo) => (slo.id === id ? { ...slo, weight: newWeight } : slo))
    );
    toast.success("Weight updated", {
      description: "SLO weight has been adjusted",
    });
  };

  const handleToggle = (id: string) => {
    setSlos((prev) =>
      prev.map((slo) => (slo.id === id ? { ...slo, active: !slo.active } : slo))
    );
  };

  const handleDelete = (id: string) => {
    setSlos((prev) => prev.filter((slo) => slo.id !== id));
    toast.success("SLO deleted");
  };

  const handleSave = () => {
    if (editingSLO) {
      if (editingSLO.id === "new") {
        setSlos((prev) => [...prev, { ...editingSLO, id: Date.now().toString() }]);
        toast.success("New SLO added");
      } else {
        setSlos((prev) => prev.map((slo) => (slo.id === editingSLO.id ? editingSLO : slo)));
        toast.success("SLO updated");
      }
      setEditingSLO(null);
      setIsDialogOpen(false);
    }
  };

  const totalWeight = slos.reduce((sum, slo) => sum + slo.weight, 0);

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
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button
              onClick={() => {
                setEditingSLO({
                  id: "new",
                  name: "",
                  description: "",
                  weight: 0.1,
                  active: true,
                });
              }}
              className="gap-2"
            >
              <Plus className="h-4 w-4" />
              Add SLO
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingSLO?.id === "new" ? "Add New SLO" : "Edit SLO"}
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Name</Label>
                <Input
                  value={editingSLO?.name || ""}
                  onChange={(e) =>
                    setEditingSLO((prev) => prev ? { ...prev, name: e.target.value } : null)
                  }
                  placeholder="e.g., Security"
                />
              </div>
              <div>
                <Label>Description</Label>
                <Textarea
                  value={editingSLO?.description || ""}
                  onChange={(e) =>
                    setEditingSLO((prev) => prev ? { ...prev, description: e.target.value } : null)
                  }
                  placeholder="Describe the objective..."
                />
              </div>
              <div>
                <Label>Weight: {editingSLO?.weight.toFixed(2)}</Label>
                <Slider
                  value={[editingSLO?.weight || 0]}
                  onValueChange={([value]) =>
                    setEditingSLO((prev) => prev ? { ...prev, weight: value } : null)
                  }
                  min={0}
                  max={1}
                  step={0.05}
                  className="mt-2"
                />
              </div>
              <div className="flex items-center justify-between">
                <Label>Active</Label>
                <Switch
                  checked={editingSLO?.active}
                  onCheckedChange={(checked) =>
                    setEditingSLO((prev) => prev ? { ...prev, active: checked } : null)
                  }
                />
              </div>
              <Button onClick={handleSave} className="w-full">
                Save
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Weight Summary */}
      <Card className="bg-gradient-to-br from-card to-card/80">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Weight</p>
              <p className="text-3xl font-bold">{totalWeight.toFixed(2)}</p>
            </div>
            {totalWeight !== 1 && (
              <div className="text-warning text-sm">
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
                    {!slo.active && (
                      <span className="text-xs text-muted-foreground font-normal">
                        (Inactive)
                      </span>
                    )}
                  </CardTitle>
                  <p className="text-sm text-muted-foreground mt-1">
                    {slo.description}
                  </p>
                </div>
                <Switch checked={slo.active} onCheckedChange={() => handleToggle(slo.id)} />
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
                  disabled={!slo.active}
                />
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setEditingSLO(slo);
                    setIsDialogOpen(true);
                  }}
                  className="gap-2"
                >
                  <Edit className="h-3 w-3" />
                  Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDelete(slo.id)}
                  className="gap-2 text-danger"
                >
                  <Trash2 className="h-3 w-3" />
                  Delete
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
