import { useState } from "react";
import { Cpu, Copy, Check, AlertTriangle, Zap, HelpCircle } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./ui/tooltip";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const WiringDiagram = ({ componentIds = [], onExplainRequest }) => {
  const [diagram, setDiagram] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [open, setOpen] = useState(false);

  const generateDiagram = async () => {
    if (componentIds.length === 0) {
      toast.error("No components selected");
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.post(`${API}/wiring-diagram`, {
        component_ids: componentIds
      });
      setDiagram(response.data);
    } catch (err) {
      console.error("Failed to generate wiring diagram:", err);
      toast.error("Failed to generate wiring diagram");
    } finally {
      setLoading(false);
    }
  };

  const copyDiagram = async () => {
    if (!diagram?.diagram) return;
    try {
      await navigator.clipboard.writeText(diagram.diagram);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      toast.success("Wiring diagram copied!");
    } catch (err) {
      toast.error("Failed to copy");
    }
  };

  const handleOpen = (isOpen) => {
    setOpen(isOpen);
    if (isOpen && !diagram) {
      generateDiagram();
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpen}>
      <DialogTrigger asChild>
        <Button 
          variant="outline" 
          size="sm"
          className="gap-2"
          data-testid="wiring-diagram-btn"
        >
          <Cpu size={14} />
          Wiring Diagram
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto bg-neutral-900 border-white/10">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 font-heading">
            <Cpu className="text-primary" size={20} />
            ASCII Wiring Diagram
          </DialogTitle>
          <p className="text-sm text-neutral-400">
            Deterministic pin assignments for your components
          </p>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="loading-spinner" />
          </div>
        ) : diagram ? (
          <div className="space-y-4">
            {/* Warnings */}
            {diagram.warnings && diagram.warnings.length > 0 && (
              <Card className="bg-red-500/10 border-red-500/30 p-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle size={18} className="text-red-400 mt-0.5 shrink-0" />
                  <div>
                    <h4 className="font-medium text-red-300 mb-2">Warnings</h4>
                    <ul className="text-sm text-red-400/80 space-y-1">
                      {diagram.warnings.map((warning, idx) => (
                        <li key={idx}>• {warning}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </Card>
            )}

            {/* Components badge list */}
            <div className="flex flex-wrap gap-2">
              {diagram.components?.map(comp => (
                <Badge 
                  key={comp.id}
                  variant="outline"
                  className="bg-secondary/10 text-secondary border-secondary/30"
                >
                  {comp.name}
                </Badge>
              ))}
            </div>

            {/* Diagram */}
            <div className="relative group">
              <div className="absolute top-2 right-2 z-10 flex gap-2">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={copyDiagram}
                        className="h-8 w-8 p-0 bg-neutral-800/80 hover:bg-neutral-700"
                        data-testid="copy-wiring-btn"
                      >
                        {copied ? (
                          <Check size={14} className="text-emerald-400" />
                        ) : (
                          <Copy size={14} className="text-neutral-400" />
                        )}
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Copy diagram</TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                
                {onExplainRequest && (
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onExplainRequest(diagram.diagram)}
                          className="h-8 w-8 p-0 bg-neutral-800/80 hover:bg-neutral-700"
                          data-testid="explain-wiring-btn"
                        >
                          <HelpCircle size={14} className="text-neutral-400" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Explain wiring</TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                )}
              </div>
              
              <pre className="bg-black/60 border border-white/10 rounded-sm p-4 overflow-x-auto font-mono text-sm text-neutral-200 whitespace-pre">
                {diagram.diagram}
              </pre>
            </div>

            {/* Pin Assignments Summary */}
            {diagram.pin_assignments && Object.keys(diagram.pin_assignments).length > 0 && (
              <Card className="bg-neutral-800/50 border-white/10 p-4">
                <h4 className="font-medium text-neutral-200 mb-3 flex items-center gap-2">
                  <Zap size={14} className="text-primary" />
                  Pin Summary
                </h4>
                <div className="grid gap-2 md:grid-cols-2">
                  {Object.entries(diagram.pin_assignments).map(([compId, pins]) => (
                    <div key={compId} className="text-sm">
                      <span className="text-neutral-400">{compId}:</span>
                      <span className="text-neutral-300 ml-2">
                        {Object.entries(pins).map(([pin, gpio]) => `${pin}→${gpio}`).join(", ")}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Regenerate button */}
            <div className="flex justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={generateDiagram}
                disabled={loading}
              >
                Regenerate Diagram
              </Button>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-neutral-500">
            <Cpu size={48} className="mx-auto mb-4 opacity-50" />
            <p>Select components to generate wiring diagram</p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default WiringDiagram;
