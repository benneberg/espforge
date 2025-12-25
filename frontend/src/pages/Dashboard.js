import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Cpu, FolderOpen, RefreshCw } from "lucide-react";
import axios from "axios";
import { Button } from "../components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "../components/ui/tabs";
import ProjectCard from "../components/ProjectCard";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const Dashboard = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [error, setError] = useState(null);

  const fetchProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = filter !== "all" ? { status: filter } : {};
      const response = await axios.get(`${API}/projects`, { params });
      setProjects(response.data);
    } catch (err) {
      console.error("Failed to fetch projects:", err);
      setError("Failed to load projects");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [filter]);

  const filteredProjects = projects;

  return (
    <div className="min-h-screen p-4 md:p-8" data-testid="dashboard">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Cpu className="w-6 h-6 text-primary" />
          </div>
          <h1 className="font-heading text-2xl md:text-3xl font-bold text-neutral-100">
            ESP32 Copilot
          </h1>
        </div>
        <p className="text-neutral-400 text-sm md:text-base">
          Your AI-powered IoT development assistant
        </p>
      </header>

      {/* Filter Tabs */}
      <div className="flex items-center justify-between mb-6 gap-4">
        <Tabs value={filter} onValueChange={setFilter} className="w-full max-w-md">
          <TabsList className="bg-neutral-900/50 border border-white/10">
            <TabsTrigger 
              value="all" 
              className="data-[state=active]:bg-primary data-[state=active]:text-black"
              data-testid="filter-all"
            >
              All
            </TabsTrigger>
            <TabsTrigger 
              value="active"
              className="data-[state=active]:bg-primary data-[state=active]:text-black"
              data-testid="filter-active"
            >
              Active
            </TabsTrigger>
            <TabsTrigger 
              value="completed"
              className="data-[state=active]:bg-primary data-[state=active]:text-black"
              data-testid="filter-completed"
            >
              Completed
            </TabsTrigger>
            <TabsTrigger 
              value="archived"
              className="data-[state=active]:bg-primary data-[state=active]:text-black"
              data-testid="filter-archived"
            >
              Archived
            </TabsTrigger>
          </TabsList>
        </Tabs>

        <Button
          variant="ghost"
          size="icon"
          onClick={fetchProjects}
          disabled={loading}
          className="shrink-0"
          data-testid="refresh-projects"
        >
          <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
        </Button>
      </div>

      {/* Projects Grid */}
      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div 
              key={i} 
              className="h-40 rounded-lg skeleton"
            />
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-16">
          <p className="text-red-400 mb-4">{error}</p>
          <Button onClick={fetchProjects} variant="outline">
            Try Again
          </Button>
        </div>
      ) : filteredProjects.length === 0 ? (
        <div className="text-center py-16" data-testid="empty-state">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-neutral-800 flex items-center justify-center">
            <FolderOpen size={32} className="text-neutral-500" />
          </div>
          <h2 className="text-xl font-heading font-bold text-neutral-300 mb-2">
            No projects yet
          </h2>
          <p className="text-neutral-500 mb-6">
            Create your first ESP32 project to get started
          </p>
          <Button 
            onClick={() => navigate("/create")}
            className="bg-primary text-black hover:bg-primary/90 glow-primary"
            data-testid="create-first-project"
          >
            <Plus size={18} className="mr-2" />
            Create Project
          </Button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredProjects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}

      {/* Floating Create Button (mobile) */}
      {filteredProjects.length > 0 && (
        <Button
          onClick={() => navigate("/create")}
          className="fixed bottom-20 right-4 h-14 w-14 rounded-full bg-primary text-black hover:bg-primary/90 shadow-lg glow-primary-strong md:hidden"
          data-testid="fab-create"
        >
          <Plus size={24} />
        </Button>
      )}
    </div>
  );
};

export default Dashboard;
