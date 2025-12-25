import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { 
  ArrowLeft, 
  Cpu, 
  MoreVertical, 
  Trash2, 
  Archive, 
  CheckCircle,
  Edit2,
  RefreshCw 
} from "lucide-react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../components/ui/alert-dialog";
import StageContent from "../components/StageContent";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const STAGES = [
  { key: "idea", label: "Idea", icon: "💡" },
  { key: "requirements", label: "Requirements", icon: "📋" },
  { key: "hardware", label: "Hardware", icon: "🔧" },
  { key: "architecture", label: "Architecture", icon: "🏗️" },
  { key: "code", label: "Code", icon: "💻" },
  { key: "explanation", label: "Learning", icon: "📚" },
  { key: "iteration", label: "Iteration", icon: "🔄" },
];

const ProjectDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generatingStage, setGeneratingStage] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState("");

  const fetchProject = async () => {
    try {
      const response = await axios.get(`${API}/projects/${id}`);
      setProject(response.data);
      setEditName(response.data.name);
    } catch (err) {
      console.error("Failed to fetch project:", err);
      toast.error("Failed to load project");
      navigate("/");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProject();
  }, [id]);

  const handleGenerate = async (stage, userMessage = null) => {
    setGeneratingStage(stage);
    try {
      const response = await axios.post(`${API}/projects/${id}/generate`, {
        project_id: id,
        stage: stage,
        user_message: userMessage,
      });
      
      // Update local state
      setProject(prev => ({
        ...prev,
        stages: {
          ...prev.stages,
          [stage]: {
            content: response.data.content,
            generated_at: new Date().toISOString(),
            user_approved: false,
          }
        }
      }));
      
      toast.success(`${stage} generated successfully!`);
    } catch (err) {
      console.error("Generation failed:", err);
      toast.error("Generation failed. Please try again.");
    } finally {
      setGeneratingStage(null);
    }
  };

  const handleApprove = async (stage, approved) => {
    try {
      const response = await axios.post(`${API}/projects/${id}/stages/${stage}/approve`, {
        stage: stage,
        approved: approved,
      });
      
      // Update local state
      setProject(prev => ({
        ...prev,
        current_stage: response.data.next_stage || prev.current_stage,
        stages: {
          ...prev.stages,
          [stage]: {
            ...prev.stages[stage],
            user_approved: approved,
          }
        }
      }));
      
      if (response.data.next_stage) {
        toast.success(`Moving to ${response.data.next_stage} stage`);
      }
    } catch (err) {
      console.error("Approval failed:", err);
      toast.error("Failed to update stage");
    }
  };

  const handleDelete = async () => {
    try {
      await axios.delete(`${API}/projects/${id}`);
      toast.success("Project deleted");
      navigate("/");
    } catch (err) {
      console.error("Delete failed:", err);
      toast.error("Failed to delete project");
    }
  };

  const handleStatusChange = async (status) => {
    try {
      await axios.patch(`${API}/projects/${id}`, { status });
      setProject(prev => ({ ...prev, status }));
      toast.success(`Project ${status}`);
    } catch (err) {
      console.error("Status update failed:", err);
      toast.error("Failed to update status");
    }
  };

  const handleNameUpdate = async () => {
    if (editName.trim() === project.name) {
      setIsEditing(false);
      return;
    }
    
    try {
      await axios.patch(`${API}/projects/${id}`, { name: editName });
      setProject(prev => ({ ...prev, name: editName }));
      setIsEditing(false);
      toast.success("Project name updated");
    } catch (err) {
      console.error("Name update failed:", err);
      toast.error("Failed to update name");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen p-4 md:p-8 flex items-center justify-center">
        <div className="loading-spinner" />
      </div>
    );
  }

  if (!project) {
    return null;
  }

  const currentStageIdx = STAGES.findIndex(s => s.key === project.current_stage);

  return (
    <div className="min-h-screen p-4 md:p-8" data-testid="project-detail">
      {/* Header */}
      <header className="mb-6">
        <Button
          variant="ghost"
          onClick={() => navigate("/")}
          className="mb-4 -ml-2 text-neutral-400 hover:text-white"
          data-testid="back-to-projects"
        >
          <ArrowLeft size={18} className="mr-2" />
          Back
        </Button>
        
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Cpu className="w-5 h-5 text-primary" />
              </div>
              
              {isEditing ? (
                <div className="flex items-center gap-2 flex-1">
                  <Input
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    className="bg-black/50 border-white/10 h-9"
                    autoFocus
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleNameUpdate();
                      if (e.key === 'Escape') setIsEditing(false);
                    }}
                    data-testid="edit-name-input"
                  />
                  <Button size="sm" onClick={handleNameUpdate}>Save</Button>
                </div>
              ) : (
                <h1 
                  className="font-heading text-xl md:text-2xl font-bold text-neutral-100 cursor-pointer hover:text-primary transition-colors"
                  onClick={() => setIsEditing(true)}
                  data-testid="project-title"
                >
                  {project.name}
                </h1>
              )}
            </div>
            
            <p className="text-neutral-400 text-sm line-clamp-2">
              {project.idea}
            </p>
            
            <div className="flex items-center gap-2 mt-3">
              <Badge 
                variant="outline" 
                className="bg-neutral-800/50 border-neutral-700 text-neutral-300"
              >
                {project.target_hardware}
              </Badge>
              <Badge 
                variant="outline"
                className={`${
                  project.status === 'completed' 
                    ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                    : project.status === 'archived'
                      ? 'bg-neutral-500/20 text-neutral-400 border-neutral-500/30'
                      : 'bg-primary/20 text-primary border-primary/30'
                }`}
              >
                {project.status}
              </Badge>
            </div>
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="ghost" 
                size="icon"
                data-testid="project-menu"
              >
                <MoreVertical size={18} />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuItem onClick={() => setIsEditing(true)}>
                <Edit2 size={14} className="mr-2" />
                Rename
              </DropdownMenuItem>
              <DropdownMenuItem onClick={fetchProject}>
                <RefreshCw size={14} className="mr-2" />
                Refresh
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              {project.status !== 'completed' && (
                <DropdownMenuItem onClick={() => handleStatusChange('completed')}>
                  <CheckCircle size={14} className="mr-2" />
                  Mark Complete
                </DropdownMenuItem>
              )}
              {project.status !== 'archived' && (
                <DropdownMenuItem onClick={() => handleStatusChange('archived')}>
                  <Archive size={14} className="mr-2" />
                  Archive
                </DropdownMenuItem>
              )}
              {project.status === 'archived' && (
                <DropdownMenuItem onClick={() => handleStatusChange('active')}>
                  <RefreshCw size={14} className="mr-2" />
                  Reactivate
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              <DropdownMenuItem 
                onClick={() => setDeleteDialogOpen(true)}
                className="text-red-400 focus:text-red-400"
                data-testid="delete-project-menu"
              >
                <Trash2 size={14} className="mr-2" />
                Delete Project
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      {/* Progress Overview */}
      <div className="mb-6 p-4 bg-neutral-900/40 border border-white/10 rounded-lg">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-neutral-400">Progress</span>
          <span className="text-sm font-mono text-primary">
            {currentStageIdx + 1} / {STAGES.length}
          </span>
        </div>
        <div className="flex gap-1">
          {STAGES.map((stage, idx) => {
            const stageData = project.stages?.[stage.key];
            const isCompleted = stageData?.user_approved;
            const isCurrent = project.current_stage === stage.key;
            
            return (
              <div
                key={stage.key}
                className={`flex-1 h-2 rounded-full transition-all ${
                  isCompleted 
                    ? 'bg-emerald-500' 
                    : isCurrent 
                      ? 'bg-primary animate-pulse-glow' 
                      : 'bg-neutral-800'
                }`}
              />
            );
          })}
        </div>
        <div className="flex justify-between mt-2 text-xs text-neutral-500">
          <span>Start</span>
          <span>Complete</span>
        </div>
      </div>

      {/* Stages */}
      <div className="space-y-4 max-w-3xl mx-auto">
        {STAGES.map((stage, idx) => {
          const stageData = project.stages?.[stage.key];
          const isCurrentStage = project.current_stage === stage.key;
          const isPreviousCompleted = idx === 0 || project.stages?.[STAGES[idx - 1].key]?.user_approved;
          
          return (
            <StageContent
              key={stage.key}
              stage={stage.key}
              stageData={stageData}
              isCurrentStage={isCurrentStage && isPreviousCompleted}
              onGenerate={(feedback) => handleGenerate(stage.key, feedback)}
              onApprove={(approved) => handleApprove(stage.key, approved)}
              isGenerating={generatingStage === stage.key}
            />
          );
        })}
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="bg-neutral-900 border-white/10">
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Project</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{project.name}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-neutral-800 border-white/10 hover:bg-neutral-700">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-red-600 hover:bg-red-700"
              data-testid="confirm-delete"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default ProjectDetail;
