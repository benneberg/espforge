import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  ArrowLeft, 
  Thermometer, 
  Monitor, 
  Zap, 
  Battery, 
  AlertTriangle, 
  Leaf,
  Loader2,
  ChevronRight,
  BookOpen
} from "lucide-react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ICON_MAP = {
  thermometer: Thermometer,
  monitor: Monitor,
  zap: Zap,
  battery: Battery,
  "alert-triangle": AlertTriangle,
  leaf: Leaf,
};

const DIFFICULTY_COLORS = {
  beginner: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  intermediate: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  advanced: "bg-red-500/20 text-red-400 border-red-500/30",
};

const Templates = () => {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(null);

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const response = await axios.get(`${API}/templates`);
        setTemplates(response.data);
      } catch (err) {
        console.error("Failed to fetch templates:", err);
        toast.error("Failed to load templates");
      } finally {
        setLoading(false);
      }
    };
    fetchTemplates();
  }, []);

  const createFromTemplate = async (templateId) => {
    setCreating(templateId);
    try {
      const response = await axios.post(`${API}/templates/${templateId}/instantiate`);
      toast.success("Project created from template!");
      navigate(`/project/${response.data.id}`);
    } catch (err) {
      console.error("Failed to create project:", err);
      toast.error("Failed to create project from template");
    } finally {
      setCreating(null);
    }
  };

  return (
    <div className="min-h-screen p-4 md:p-8" data-testid="templates-page">
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
            <BookOpen className="w-6 h-6 text-primary" />
          </div>
          <h1 className="font-heading text-2xl font-bold text-neutral-100">
            Project Templates
          </h1>
        </div>
        <p className="text-neutral-400 text-sm">
          Start with a pre-configured project and learn as you build
        </p>
      </header>

      {/* Templates Grid */}
      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-48 rounded-lg skeleton" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {templates.map((template) => {
            const Icon = ICON_MAP[template.icon] || Thermometer;
            const difficultyColor = DIFFICULTY_COLORS[template.difficulty] || DIFFICULTY_COLORS.beginner;
            
            return (
              <Card
                key={template.id}
                className="bg-neutral-900/40 border-white/10 hover:border-primary/30 p-5 transition-all cursor-pointer group"
                onClick={() => createFromTemplate(template.id)}
                data-testid={`template-${template.id}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Icon className="w-5 h-5 text-primary" />
                  </div>
                  <Badge variant="outline" className={`text-xs ${difficultyColor}`}>
                    {template.difficulty}
                  </Badge>
                </div>
                
                <h3 className="font-heading font-bold text-lg text-neutral-100 mb-2 group-hover:text-primary transition-colors">
                  {template.name}
                </h3>
                
                <p className="text-sm text-neutral-400 mb-4 line-clamp-2">
                  {template.description}
                </p>

                {/* Features */}
                <div className="flex flex-wrap gap-1 mb-4">
                  {template.features?.slice(0, 3).map((feature, idx) => (
                    <Badge 
                      key={idx}
                      variant="outline"
                      className="text-xs bg-neutral-800/50 border-neutral-700 text-neutral-400"
                    >
                      {feature}
                    </Badge>
                  ))}
                  {template.features?.length > 3 && (
                    <Badge 
                      variant="outline"
                      className="text-xs bg-neutral-800/50 border-neutral-700 text-neutral-500"
                    >
                      +{template.features.length - 3} more
                    </Badge>
                  )}
                </div>

                {/* Learning Topics */}
                {template.learning_topics && (
                  <div className="text-xs text-neutral-500 mb-4">
                    <span className="text-neutral-400">You'll learn:</span>{" "}
                    {template.learning_topics.slice(0, 2).join(", ")}
                    {template.learning_topics.length > 2 && "..."}
                  </div>
                )}

                {/* Components count */}
                <div className="flex items-center justify-between pt-3 border-t border-white/10">
                  <span className="text-xs text-neutral-500">
                    {template.components?.length || 0} components
                  </span>
                  
                  <Button
                    size="sm"
                    disabled={creating === template.id}
                    className="bg-primary/10 text-primary hover:bg-primary/20 border-0"
                    onClick={(e) => {
                      e.stopPropagation();
                      createFromTemplate(template.id);
                    }}
                    data-testid={`use-template-${template.id}`}
                  >
                    {creating === template.id ? (
                      <Loader2 size={14} className="animate-spin" />
                    ) : (
                      <>
                        Use Template
                        <ChevronRight size={14} className="ml-1" />
                      </>
                    )}
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {!loading && templates.length === 0 && (
        <div className="text-center py-16">
          <BookOpen size={48} className="mx-auto text-neutral-600 mb-4" />
          <h2 className="text-xl font-heading font-bold text-neutral-300 mb-2">
            No templates available
          </h2>
          <p className="text-neutral-500">
            Templates will appear here when available
          </p>
        </div>
      )}
    </div>
  );
};

export default Templates;
