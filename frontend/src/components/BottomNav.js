import { NavLink, useLocation } from "react-router-dom";
import { Home, Plus, Settings, Cpu } from "lucide-react";

const BottomNav = () => {
  const location = useLocation();
  
  const navItems = [
    { path: "/", icon: Home, label: "Projects" },
    { path: "/create", icon: Plus, label: "New" },
    { path: "/settings", icon: Settings, label: "Settings" },
  ];

  return (
    <nav 
      className="fixed bottom-0 left-0 right-0 h-16 bg-neutral-950/90 backdrop-blur-xl border-t border-white/10 z-50 bottom-nav"
      data-testid="bottom-nav"
    >
      <div className="flex items-center justify-around h-full max-w-md mx-auto px-4">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          
          return (
            <NavLink
              key={item.path}
              to={item.path}
              data-testid={`nav-${item.label.toLowerCase()}`}
              className={`flex flex-col items-center justify-center gap-1 px-4 py-2 rounded-lg transition-all ${
                isActive 
                  ? "text-primary" 
                  : "text-neutral-500 hover:text-neutral-300"
              }`}
            >
              <Icon 
                size={22} 
                className={isActive ? "drop-shadow-[0_0_8px_rgba(245,158,11,0.5)]" : ""} 
              />
              <span className="text-xs font-medium">{item.label}</span>
            </NavLink>
          );
        })}
      </div>
      
      {/* ESP32 logo watermark */}
      <div className="absolute left-4 top-1/2 -translate-y-1/2 hidden md:flex items-center gap-2 text-neutral-700">
        <Cpu size={18} />
        <span className="text-xs font-mono">ESP32 Copilot</span>
      </div>
    </nav>
  );
};

export default BottomNav;
