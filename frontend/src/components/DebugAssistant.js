import { useState } from "react";
import { Bug, Send, Loader2, AlertCircle, Wrench, Zap, Battery, Code } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Card } from "./ui/card";
import { Label } from "./ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ERROR_TYPES = [
  { id: "compilation", label: "Compilation Error", icon: Code, description: "Compiler errors, missing libraries, syntax issues" },
  { id: "runtime", label: "Runtime Error", icon: AlertCircle, description: "Crashes, exceptions, watchdog resets" },
  { id: "hardware", label: "Hardware Issue", icon: Wrench, description: "Wiring problems, component failures, signal issues" },
  { id: "power", label: "Power Problem", icon: Battery, description: "Brownouts, insufficient current, sleep issues" },
];

const DebugAssistant = ({ projectId }) => {
  const [open, setOpen] = useState(false);
  const [errorType, setErrorType] = useState("compilation");
  const [logContent, setLogContent] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  // Get LLM settings from localStorage
  const getSettings = () => {
    const stored = localStorage.getItem("esp32-copilot-settings");
    return stored ? JSON.parse(stored) : {
      provider: "openai",
      model: "gpt-4o",
      groqKey: "",
      openrouterKey: "",
    };
  };

  const analyzeError = async () => {
    if (!logContent.trim()) {
      toast.error("Please paste your error log or message");
      return;
    }

    setLoading(true);
    setAnalysis(null);

    try {
      const settings = getSettings();
      
      const requestData = {
        project_id: projectId,
        error_type: errorType,
        log_content: logContent,
        provider: settings.provider,
        model: settings.model,
      };

      // Add API key if needed
      if (settings.provider === "groq" && settings.groqKey) {
        requestData.api_key = settings.groqKey;
      } else if (settings.provider === "openrouter" && settings.openrouterKey) {
        requestData.api_key = settings.openrouterKey;
      }

      const response = await axios.post(`${API}/debug`, requestData);
      setAnalysis(response.data.analysis);
      toast.success("Analysis complete!");
    } catch (err) {
      console.error("Debug analysis failed:", err);
      const errorMsg = err.response?.data?.detail || "Analysis failed. Please try again.";
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const renderAnalysis = (content) => {
    if (!content) return null;
    
    // Simple markdown-like rendering
    return content.split('\n').map((line, idx) => {
      if (line.startsWith('## ')) {
        return <h3 key={idx} className="text-lg font-bold text-primary mt-4 mb-2">{line.slice(3)}</h3>;
      }
      if (line.startsWith('### ')) {
        return <h4 key={idx} className="text-base font-semibold text-neutral-200 mt-3 mb-1">{line.slice(4)}</h4>;
      }
      if (line.startsWith('- ') || line.startsWith('• ')) {
        return <li key={idx} className="text-neutral-300 ml-4">{line.slice(2)}</li>;
      }
      if (line.startsWith('```')) {
        return null; // Handle code blocks separately
      }
      if (line.trim() === '') {
        return <br key={idx} />;
      }
      return <p key={idx} className="text-neutral-300 leading-relaxed">{line}</p>;
    });
  };

  const selectedErrorType = ERROR_TYPES.find(e => e.id === errorType);
  const Icon = selectedErrorType?.icon || Bug;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button 
          variant="outline" 
          size="sm"
          className="gap-2"
          data-testid="debug-assistant-btn"
        >
          <Bug size={14} />
          Debug
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto bg-neutral-900 border-white/10">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 font-heading">
            <Bug className="text-primary" size={20} />
            Debug Assistant
          </DialogTitle>
          <p className="text-sm text-neutral-400">
            Paste your error logs or describe the issue for AI-powered debugging help
          </p>
        </DialogHeader>

        <div className="space-y-4">
          {/* Error Type Selection */}
          <div className="space-y-2">
            <Label className="text-neutral-200">Error Type</Label>
            <div className="grid grid-cols-2 gap-2">
              {ERROR_TYPES.map(type => {
                const TypeIcon = type.icon;
                const isSelected = errorType === type.id;
                return (
                  <button
                    key={type.id}
                    onClick={() => setErrorType(type.id)}
                    className={`flex items-start gap-3 p-3 rounded-lg border text-left transition-colors ${
                      isSelected 
                        ? "bg-primary/10 border-primary/30" 
                        : "bg-neutral-800/50 border-white/10 hover:border-white/20"
                    }`}
                    data-testid={`error-type-${type.id}`}
                  >
                    <TypeIcon size={18} className={isSelected ? "text-primary" : "text-neutral-400"} />
                    <div>
                      <div className={`font-medium ${isSelected ? "text-primary" : "text-neutral-200"}`}>
                        {type.label}
                      </div>
                      <div className="text-xs text-neutral-500">{type.description}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Log Input */}
          <div className="space-y-2">
            <Label className="text-neutral-200">Error Log / Description</Label>
            <Textarea
              value={logContent}
              onChange={(e) => setLogContent(e.target.value)}
              placeholder={`Paste your ${selectedErrorType?.label.toLowerCase() || 'error'} here...\n\nExamples:\n- Compiler output\n- Serial monitor output\n- Crash dump\n- Description of behavior`}
              className="bg-black/50 border-white/10 min-h-[150px] font-mono text-sm"
              data-testid="debug-log-input"
            />
          </div>

          {/* Analyze Button */}
          <Button
            onClick={analyzeError}
            disabled={loading || !logContent.trim()}
            className="w-full bg-primary text-black hover:bg-primary/90"
            data-testid="analyze-btn"
          >
            {loading ? (
              <>
                <Loader2 size={16} className="mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Send size={16} className="mr-2" />
                Analyze Error
              </>
            )}
          </Button>

          {/* Analysis Results */}
          {analysis && (
            <Card className="bg-neutral-800/50 border-white/10 p-4 mt-4">
              <div className="flex items-center gap-2 mb-4">
                <Icon size={18} className="text-primary" />
                <h3 className="font-heading font-bold text-neutral-100">
                  Analysis Results
                </h3>
              </div>
              <div className="prose prose-invert prose-sm max-w-none">
                {renderAnalysis(analysis)}
              </div>
            </Card>
          )}

          {/* Tips */}
          <Card className="bg-neutral-800/30 border-white/5 p-4">
            <h4 className="text-sm font-medium text-neutral-300 mb-2">Tips for better analysis</h4>
            <ul className="text-xs text-neutral-500 space-y-1">
              <li>• Include the complete error message, not just the first line</li>
              <li>• For runtime issues, include Serial output before the crash</li>
              <li>• Mention any recent code changes</li>
              <li>• Describe what you expected vs what happened</li>
            </ul>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default DebugAssistant;
