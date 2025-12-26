import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "./components/ui/sonner";
import { ThemeProvider } from "./context/ThemeContext";
import Dashboard from "./pages/Dashboard";
import ProjectDetail from "./pages/ProjectDetail";
import Settings from "./pages/Settings";
import CreateProject from "./pages/CreateProject";
import Templates from "./pages/Templates";
import BottomNav from "./components/BottomNav";
import "./App.css";

function App() {
  return (
    <ThemeProvider>
      <div className="min-h-screen bg-background">
        <BrowserRouter>
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/create" element={<CreateProject />} />
              <Route path="/templates" element={<Templates />} />
              <Route path="/project/:id" element={<ProjectDetail />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
          <BottomNav />
          <Toaster position="top-center" />
        </BrowserRouter>
      </div>
    </ThemeProvider>
  );
}

export default App;
