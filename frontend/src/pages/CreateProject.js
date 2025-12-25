import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Cpu, Zap, Lightbulb } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";
import { Card } from "../components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const EXAMPLE_IDEAS = [
  "Smart plant watering system with soil moisture sensor",
  "Temperature and humidity monitor with OLED display",
  "Motion-activated LED strip controller",
  "WiFi-enabled garage door opener with status notification",
  "Air quality monitor with PM2.5 and CO2 sensors",
];

const HARDWARE_OPTIONS = [
  "ESP32 DevKit V1",
  "ESP32 NodeMCU-32S",
  "ESP32-WROOM-32",
  "ESP32-S2",
  "ESP32-S3",
  "ESP32-C3",
];

const CreateProject = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    idea: "",
    description: "",
    target_hardware: "ESP32 DevKit V1",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.idea.trim()) {
      toast.error("Please fill in the project name and idea");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await axios.post(`${API}/projects`, formData);
      toast.success("Project created successfully!");
      navigate(`/project/${response.data.id}`);
    } catch (err) {
      console.error("Failed to create project:", err);
      toast.error("Failed to create project. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const useExample = (idea) => {
    setFormData(prev => ({ ...prev, idea }));
    // Generate a name from the idea
    const name = idea.split(" ").slice(0, 4).join(" ");
    setFormData(prev => ({ ...prev, name }));
  };

  return (
    <div className="min-h-screen p-4 md:p-8" data-testid="create-project-page">
      {/* Header */}
      <header className="mb-6">
        <Button
          variant="ghost"
          onClick={() => navigate("/")}
          className="mb-4 -ml-2 text-neutral-400 hover:text-white"
          data-testid="back-btn"
        >
          <ArrowLeft size={18} className="mr-2" />
          Back to Projects
        </Button>
        
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Zap className="w-6 h-6 text-primary" />
          </div>
          <h1 className="font-heading text-2xl font-bold text-neutral-100">
            New Project
          </h1>
        </div>
        <p className="text-neutral-400 text-sm">
          Describe your ESP32 project idea and we'll help you build it
        </p>
      </header>

      <div className="max-w-2xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Project Name */}
          <div className="space-y-2">
            <Label htmlFor="name" className="text-neutral-200">
              Project Name
            </Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="e.g., Smart Garden Monitor"
              className="bg-black/50 border-white/10 focus:border-primary/50"
              data-testid="project-name-input"
            />
          </div>

          {/* Idea */}
          <div className="space-y-2">
            <Label htmlFor="idea" className="text-neutral-200">
              Project Idea
            </Label>
            <Textarea
              id="idea"
              value={formData.idea}
              onChange={(e) => setFormData(prev => ({ ...prev, idea: e.target.value }))}
              placeholder="Describe what you want to build. Be specific about sensors, features, and connectivity..."
              className="bg-black/50 border-white/10 focus:border-primary/50 min-h-[120px]"
              data-testid="project-idea-input"
            />
          </div>

          {/* Description (optional) */}
          <div className="space-y-2">
            <Label htmlFor="description" className="text-neutral-200">
              Additional Details <span className="text-neutral-500">(optional)</span>
            </Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Any specific requirements, constraints, or goals..."
              className="bg-black/50 border-white/10 focus:border-primary/50 min-h-[80px]"
              data-testid="project-description-input"
            />
          </div>

          {/* Target Hardware */}
          <div className="space-y-2">
            <Label className="text-neutral-200">Target Hardware</Label>
            <Select
              value={formData.target_hardware}
              onValueChange={(value) => setFormData(prev => ({ ...prev, target_hardware: value }))}
            >
              <SelectTrigger 
                className="bg-black/50 border-white/10"
                data-testid="hardware-select"
              >
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {HARDWARE_OPTIONS.map((hw) => (
                  <SelectItem key={hw} value={hw}>
                    <div className="flex items-center gap-2">
                      <Cpu size={14} className="text-primary" />
                      {hw}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Submit */}
          <Button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-primary text-black hover:bg-primary/90 h-12 text-base font-medium glow-primary"
            data-testid="create-project-btn"
          >
            {isSubmitting ? (
              <>
                <div className="loading-spinner mr-2" />
                Creating...
              </>
            ) : (
              <>
                <Zap size={18} className="mr-2" />
                Create Project
              </>
            )}
          </Button>
        </form>

        {/* Example Ideas */}
        <div className="mt-10">
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb size={18} className="text-primary" />
            <h2 className="font-heading font-bold text-neutral-300">
              Need inspiration?
            </h2>
          </div>
          
          <div className="grid gap-2">
            {EXAMPLE_IDEAS.map((idea, idx) => (
              <Card
                key={idx}
                onClick={() => useExample(idea)}
                className="bg-neutral-900/40 border-white/10 hover:border-primary/30 p-3 cursor-pointer transition-all"
                data-testid={`example-idea-${idx}`}
              >
                <p className="text-sm text-neutral-300">{idea}</p>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateProject;
