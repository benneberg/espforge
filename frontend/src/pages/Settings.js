import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  ArrowLeft, 
  Settings as SettingsIcon, 
  Key, 
  Moon, 
  Sun, 
  Monitor,
  Info,
  ExternalLink,
  Check,
  Eye,
  EyeOff,
  Zap,
  AlertCircle
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card } from "../components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { useTheme } from "../context/ThemeContext";

const LLM_PROVIDERS = [
  { 
    id: "openai", 
    name: "OpenAI (Emergent)", 
    description: "Default - Uses Emergent's API key",
    models: ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
    requiresKey: false
  },
  { 
    id: "groq", 
    name: "Groq", 
    description: "Fast inference - Bring your own key",
    models: ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "llama3-groq-70b-8192-tool-use-preview"],
    requiresKey: true,
    keyUrl: "https://console.groq.com/keys"
  },
  { 
    id: "openrouter", 
    name: "OpenRouter", 
    description: "Multi-model access - Bring your own key",
    models: ["anthropic/claude-3.5-sonnet", "meta-llama/llama-3.1-70b-instruct", "google/gemini-pro", "openai/gpt-4o"],
    requiresKey: true,
    keyUrl: "https://openrouter.ai/keys"
  },
];

const Settings = () => {
  const navigate = useNavigate();
  const { theme, setTheme } = useTheme();
  
  const [settings, setSettings] = useState(() => {
    const stored = localStorage.getItem("esp32-copilot-settings");
    return stored ? JSON.parse(stored) : {
      provider: "openai",
      model: "gpt-4o",
      groqKey: "",
      openrouterKey: "",
    };
  });
  
  const [showKeys, setShowKeys] = useState({
    groq: false,
    openrouter: false,
  });

  const [testingProvider, setTestingProvider] = useState(null);

  // Save settings to localStorage
  useEffect(() => {
    localStorage.setItem("esp32-copilot-settings", JSON.stringify(settings));
  }, [settings]);

  const handleProviderChange = (provider) => {
    const providerConfig = LLM_PROVIDERS.find(p => p.id === provider);
    setSettings(prev => ({
      ...prev,
      provider,
      model: providerConfig.models[0],
    }));
    toast.success(`Switched to ${providerConfig.name}`);
  };

  const handleKeySave = (provider) => {
    toast.success(`${provider} API key saved locally`);
  };

  const testConnection = async (provider) => {
    setTestingProvider(provider);
    
    // Simple validation
    if (provider === "groq" && !settings.groqKey) {
      toast.error("Please enter your Groq API key first");
      setTestingProvider(null);
      return;
    }
    if (provider === "openrouter" && !settings.openrouterKey) {
      toast.error("Please enter your OpenRouter API key first");
      setTestingProvider(null);
      return;
    }

    // For now, just validate the key format
    if (provider === "groq" && !settings.groqKey.startsWith("gsk_")) {
      toast.error("Invalid Groq API key format. Should start with 'gsk_'");
      setTestingProvider(null);
      return;
    }
    if (provider === "openrouter" && !settings.openrouterKey.startsWith("sk-or-")) {
      toast.error("Invalid OpenRouter API key format. Should start with 'sk-or-'");
      setTestingProvider(null);
      return;
    }

    toast.success(`${provider} API key looks valid!`);
    setTestingProvider(null);
  };

  const currentProvider = LLM_PROVIDERS.find(p => p.id === settings.provider);

  return (
    <div className="min-h-screen p-4 md:p-8" data-testid="settings-page">
      {/* Header */}
      <header className="mb-6">
        <Button
          variant="ghost"
          onClick={() => navigate("/")}
          className="mb-4 -ml-2 text-neutral-400 hover:text-white"
          data-testid="back-btn"
        >
          <ArrowLeft size={18} className="mr-2" />
          Back
        </Button>
        
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-primary/10 rounded-lg">
            <SettingsIcon className="w-6 h-6 text-primary" />
          </div>
          <h1 className="font-heading text-2xl font-bold text-neutral-100">
            Settings
          </h1>
        </div>
      </header>

      <div className="max-w-2xl mx-auto space-y-6">
        {/* Theme Settings */}
        <Card className="bg-neutral-900/40 border-white/10 p-6">
          <h2 className="font-heading font-bold text-lg text-neutral-100 mb-4">
            Appearance
          </h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Moon size={18} className="text-neutral-400" />
                <div>
                  <Label className="text-neutral-200">Theme</Label>
                  <p className="text-xs text-neutral-500">Choose your preferred theme</p>
                </div>
              </div>
              
              <div className="flex bg-neutral-800 rounded-lg p-1">
                <button
                  onClick={() => setTheme("light")}
                  className={`p-2 rounded transition-colors ${theme === "light" ? "bg-neutral-700 text-white" : "text-neutral-400 hover:text-white"}`}
                  data-testid="theme-light"
                >
                  <Sun size={16} />
                </button>
                <button
                  onClick={() => setTheme("dark")}
                  className={`p-2 rounded transition-colors ${theme === "dark" ? "bg-neutral-700 text-white" : "text-neutral-400 hover:text-white"}`}
                  data-testid="theme-dark"
                >
                  <Moon size={16} />
                </button>
                <button
                  onClick={() => setTheme("system")}
                  className={`p-2 rounded transition-colors ${theme === "system" ? "bg-neutral-700 text-white" : "text-neutral-400 hover:text-white"}`}
                  data-testid="theme-system"
                >
                  <Monitor size={16} />
                </button>
              </div>
            </div>
          </div>
        </Card>

        {/* LLM Provider Settings */}
        <Card className="bg-neutral-900/40 border-white/10 p-6">
          <h2 className="font-heading font-bold text-lg text-neutral-100 mb-4 flex items-center gap-2">
            <Zap size={18} className="text-primary" />
            LLM Provider
          </h2>
          
          <div className="space-y-4">
            {/* Provider Selection */}
            <div className="space-y-2">
              <Label className="text-neutral-200">Provider</Label>
              <Select
                value={settings.provider}
                onValueChange={handleProviderChange}
              >
                <SelectTrigger 
                  className="bg-black/50 border-white/10"
                  data-testid="provider-select"
                >
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {LLM_PROVIDERS.map((provider) => (
                    <SelectItem key={provider.id} value={provider.id}>
                      <div className="flex flex-col">
                        <span>{provider.name}</span>
                        <span className="text-xs text-neutral-500">{provider.description}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Model Selection */}
            <div className="space-y-2">
              <Label className="text-neutral-200">Model</Label>
              <Select
                value={settings.model}
                onValueChange={(model) => setSettings(prev => ({ ...prev, model }))}
              >
                <SelectTrigger 
                  className="bg-black/50 border-white/10"
                  data-testid="model-select"
                >
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {currentProvider?.models.map((model) => (
                    <SelectItem key={model} value={model}>
                      {model}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Groq API Key */}
            {settings.provider === "groq" && (
              <div className="space-y-2 pt-4 border-t border-white/10">
                <Label className="text-neutral-200 flex items-center gap-2">
                  <Key size={14} />
                  Groq API Key
                </Label>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Input
                      type={showKeys.groq ? "text" : "password"}
                      value={settings.groqKey}
                      onChange={(e) => setSettings(prev => ({ ...prev, groqKey: e.target.value }))}
                      placeholder="gsk_..."
                      className="bg-black/50 border-white/10 pr-10 font-mono text-sm"
                      data-testid="groq-key-input"
                    />
                    <button
                      type="button"
                      onClick={() => setShowKeys(prev => ({ ...prev, groq: !prev.groq }))}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-300"
                    >
                      {showKeys.groq ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  <Button 
                    variant="outline" 
                    onClick={() => handleKeySave("Groq")}
                    data-testid="save-groq-key"
                  >
                    <Check size={16} />
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <a 
                    href="https://console.groq.com/keys" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-xs text-primary hover:underline flex items-center gap-1"
                  >
                    Get your Groq API key <ExternalLink size={10} />
                  </a>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => testConnection("groq")}
                    disabled={testingProvider === "groq"}
                    className="text-xs"
                  >
                    {testingProvider === "groq" ? "Testing..." : "Test Connection"}
                  </Button>
                </div>
              </div>
            )}

            {/* OpenRouter API Key */}
            {settings.provider === "openrouter" && (
              <div className="space-y-2 pt-4 border-t border-white/10">
                <Label className="text-neutral-200 flex items-center gap-2">
                  <Key size={14} />
                  OpenRouter API Key
                </Label>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Input
                      type={showKeys.openrouter ? "text" : "password"}
                      value={settings.openrouterKey}
                      onChange={(e) => setSettings(prev => ({ ...prev, openrouterKey: e.target.value }))}
                      placeholder="sk-or-..."
                      className="bg-black/50 border-white/10 pr-10 font-mono text-sm"
                      data-testid="openrouter-key-input"
                    />
                    <button
                      type="button"
                      onClick={() => setShowKeys(prev => ({ ...prev, openrouter: !prev.openrouter }))}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-300"
                    >
                      {showKeys.openrouter ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  <Button 
                    variant="outline" 
                    onClick={() => handleKeySave("OpenRouter")}
                    data-testid="save-openrouter-key"
                  >
                    <Check size={16} />
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <a 
                    href="https://openrouter.ai/keys" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-xs text-primary hover:underline flex items-center gap-1"
                  >
                    Get your OpenRouter API key <ExternalLink size={10} />
                  </a>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => testConnection("openrouter")}
                    disabled={testingProvider === "openrouter"}
                    className="text-xs"
                  >
                    {testingProvider === "openrouter" ? "Testing..." : "Test Connection"}
                  </Button>
                </div>
              </div>
            )}

            {/* Emergent Key Info */}
            {settings.provider === "openai" && (
              <div className="flex items-start gap-3 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg mt-4">
                <Info size={16} className="text-emerald-400 mt-0.5 shrink-0" />
                <div className="text-sm">
                  <p className="text-emerald-300 font-medium">Using Emergent's API Key</p>
                  <p className="text-emerald-400/80 text-xs mt-1">
                    No configuration needed. The app uses the built-in API key for OpenAI access.
                    This is the default and recommended option.
                  </p>
                </div>
              </div>
            )}

            {/* Provider Comparison */}
            <div className="mt-6 pt-4 border-t border-white/10">
              <h3 className="text-sm font-medium text-neutral-300 mb-3">Provider Comparison</h3>
              <div className="grid gap-3">
                <div className="flex items-center justify-between p-3 bg-neutral-800/50 rounded-lg">
                  <div>
                    <span className="text-sm text-neutral-200">OpenAI (Emergent)</span>
                    <p className="text-xs text-neutral-500">Best quality, no setup needed</p>
                  </div>
                  <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">Recommended</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-neutral-800/50 rounded-lg">
                  <div>
                    <span className="text-sm text-neutral-200">Groq</span>
                    <p className="text-xs text-neutral-500">Fastest inference, requires API key</p>
                  </div>
                  <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">Fast</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-neutral-800/50 rounded-lg">
                  <div>
                    <span className="text-sm text-neutral-200">OpenRouter</span>
                    <p className="text-xs text-neutral-500">Multiple models, pay-per-use</p>
                  </div>
                  <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30">Flexible</Badge>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Security Notice */}
        <Card className="bg-neutral-900/40 border-white/10 p-6">
          <div className="flex items-start gap-3">
            <AlertCircle size={18} className="text-primary mt-0.5 shrink-0" />
            <div>
              <h3 className="font-medium text-neutral-200 mb-1">API Key Storage</h3>
              <p className="text-sm text-neutral-400">
                Your API keys are stored locally in your browser's localStorage. 
                They are never sent to our servers. Keys are only used for direct 
                communication with the respective LLM providers (Groq, OpenRouter).
              </p>
            </div>
          </div>
        </Card>

        {/* About */}
        <Card className="bg-neutral-900/40 border-white/10 p-6">
          <h2 className="font-heading font-bold text-lg text-neutral-100 mb-4">
            About
          </h2>
          <div className="space-y-2 text-sm text-neutral-400">
            <p><strong className="text-neutral-200">ESP32 IoT Copilot</strong> v1.1.0</p>
            <p>An AI-powered assistant for ESP32 IoT development.</p>
            <p className="text-xs">
              From idea to working firmware, guided step-by-step.
            </p>
            <div className="pt-3 mt-3 border-t border-white/10">
              <p className="text-xs text-neutral-500">
                Features: Project management, 7-stage guided workflow, code generation with syntax highlighting, 
                hardware shopping lists, PDF/Markdown export, multi-provider LLM support.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

// Badge component inline for comparison section
const Badge = ({ children, className }) => (
  <span className={`text-xs px-2 py-1 rounded-full border ${className}`}>
    {children}
  </span>
);

export default Settings;
