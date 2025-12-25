import { useNavigate } from "react-router-dom";
import { ChevronRight, Cpu, Archive, CheckCircle2 } from "lucide-react";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";

const STAGE_LABELS = {
  idea: "Idea",
  requirements: "Requirements",
  hardware: "Hardware",
  architecture: "Architecture",
  code: "Code",
  explanation: "Learning",
  iteration: "Iteration",
};

const STATUS_CONFIG = {
  active: { label: "Active", color: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" },
  archived: { label: "Archived", color: "bg-neutral-500/20 text-neutral-400 border-neutral-500/30" },
  completed: { label: "Complete", color: "bg-primary/20 text-primary border-primary/30" },
};

const ProjectCard = ({ project }) => {
  const navigate = useNavigate();
  const statusConfig = STATUS_CONFIG[project.status] || STATUS_CONFIG.active;
  
  // Calculate progress
  const stages = ["idea", "requirements", "hardware", "architecture", "code", "explanation", "iteration"];
  const currentIdx = stages.indexOf(project.current_stage);
  const completedStages = stages.slice(0, currentIdx).filter(stage => 
    project.stages?.[stage]?.user_approved
  ).length;
  const progress = Math.round((completedStages / (stages.length - 1)) * 100);

  return (
    <Card 
      className="project-card bg-neutral-900/40 border-white/10 hover:border-primary/30 p-4 cursor-pointer"
      onClick={() => navigate(`/project/${project.id}`)}
      data-testid={`project-card-${project.id}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <Cpu size={16} className="text-primary shrink-0" />
            <h3 className="font-heading font-bold text-neutral-100 truncate">
              {project.name}
            </h3>
          </div>
          
          <p className="text-sm text-neutral-400 line-clamp-2 mb-3">
            {project.idea}
          </p>
          
          <div className="flex items-center gap-2 flex-wrap">
            <Badge 
              variant="outline" 
              className={`text-xs ${statusConfig.color}`}
            >
              {project.status === "completed" && <CheckCircle2 size={10} className="mr-1" />}
              {project.status === "archived" && <Archive size={10} className="mr-1" />}
              {statusConfig.label}
            </Badge>
            
            <Badge variant="outline" className="text-xs bg-secondary/10 text-secondary border-secondary/30">
              {STAGE_LABELS[project.current_stage]}
            </Badge>
          </div>
        </div>
        
        <div className="flex flex-col items-end gap-2">
          <ChevronRight size={20} className="text-neutral-600" />
          
          {/* Progress indicator */}
          <div className="flex gap-0.5">
            {stages.map((stage, idx) => (
              <div
                key={stage}
                className={`w-1.5 h-1.5 rounded-full ${
                  idx < currentIdx 
                    ? "bg-emerald-500" 
                    : idx === currentIdx 
                      ? "bg-primary" 
                      : "bg-neutral-700"
                }`}
              />
            ))}
          </div>
        </div>
      </div>
      
      {/* Progress bar */}
      <div className="mt-3 h-1 bg-neutral-800 rounded-full overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-primary to-secondary transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>
    </Card>
  );
};

export default ProjectCard;
