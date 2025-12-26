# ESP32 IoT LLM Copilot - Requirements & Architecture

## Original Problem Statement
Build a mobile-first, touch-optimized web application that acts as an LLM-powered copilot for ESP32 IoT projects. Guide users from idea → structured plan → wiring → firmware → working IoT project, with human approval at every step.

## User Requirements
1. **LLM Providers**: Both Groq and OpenRouter with settings toggle, Emergent LLM key as default
2. **Theme**: Auto-detect system preference with manual toggle (dark/light/system)
3. **Hardware Focus**: ESP32 only (Arduino core)
4. **Sensors Priority**: DHT22/DHT11, BME280, DS18B20, OLED SSD1306, Relay, Analog sensors

## Architecture

### Backend (FastAPI + MongoDB)
- **server.py**: Main API with project CRUD, stage management, LLM integration
- **MongoDB Collections**: `projects` (stores all project data)
- **LLM Integration**: emergentintegrations library with Emergent LLM key

### Frontend (React + Shadcn UI)
- **Pages**:
  - Dashboard (/) - Project list with filters
  - CreateProject (/create) - New project form
  - ProjectDetail (/project/:id) - 7-stage workflow view
  - Settings (/settings) - Theme and LLM provider config

- **Components**:
  - BottomNav - Mobile-first navigation
  - ProjectCard - Project list item
  - StageContent - Stage display with generate/approve actions
  - CodeBlock - Code display with copy functionality

### Data Model
```javascript
Project {
  id: string,
  name: string,
  idea: string,
  description?: string,
  target_hardware: string,
  status: "active" | "archived" | "completed",
  current_stage: "idea" | "requirements" | "hardware" | "architecture" | "code" | "explanation" | "iteration",
  stages: {
    [stage]: {
      content: string,
      generated_at: string,
      user_approved: boolean,
      notes?: string
    }
  },
  conversation_history: Array<{role, content, stage}>,
  created_at: string,
  updated_at: string
}
```

## Tasks Completed (Phase 1)
- [x] Project CRUD API endpoints
- [x] 7-stage workflow management
- [x] LLM integration with emergentintegrations
- [x] Hardware library with sensor/component database
- [x] Dashboard with project listing and filters
- [x] Create project page with example ideas
- [x] Project detail page with stage workflow
- [x] Stage generation and approval flow
- [x] Settings page with theme toggle
- [x] LLM provider selection (OpenAI/Groq/OpenRouter)
- [x] Mobile-first responsive design
- [x] Dark/light/system theme support
- [x] Code block component with copy functionality

## Tasks Completed (Phase 2)
- [x] Groq provider backend integration with user API keys
- [x] OpenRouter provider backend integration with user API keys
- [x] Code syntax highlighting with react-syntax-highlighter (Prism)
- [x] Project export to Markdown
- [x] Project export to PDF (jsPDF)
- [x] Project export to JSON
- [x] Hardware shopping list generator
- [x] Amazon shopping links for components
- [x] AliExpress shopping links for components
- [x] Price estimates for all components
- [x] Expanded hardware library (20 components)
- [x] Provider comparison section in Settings

## Tasks Completed (Phase 3)
- [x] ASCII Wiring Diagram Generator with deterministic pin mappings
- [x] Pin conflict detection and warnings
- [x] I2C/SPI/GPIO automatic pin assignment
- [x] Power notes and wiring best practices
- [x] Project Templates system (6 templates)
- [x] Template instantiation API
- [x] Templates page with difficulty badges
- [x] Debug Assistant with 4 error types (compilation, runtime, hardware, power)
- [x] LLM-powered error analysis and fix suggestions
- [x] Updated bottom navigation (4 items)

## Next Tasks (Phase 4)
- [ ] Arduino CLI compilation check (Dockerized)
- [ ] SVG wiring diagrams (optional visual enhancement)
- [ ] Project sharing via URL
- [ ] Mobile PWA support (offline caching, install prompt)
- [ ] Project versioning/history

## API Endpoints
- `GET /api/` - Health check
- `GET /api/health` - Health status
- `POST /api/projects` - Create project
- `GET /api/projects` - List projects (with status filter)
- `GET /api/projects/:id` - Get project
- `PATCH /api/projects/:id` - Update project
- `DELETE /api/projects/:id` - Delete project
- `POST /api/projects/:id/stages/:stage/approve` - Approve stage
- `POST /api/projects/:id/generate` - Generate stage content (supports provider/model/api_key)
- `GET /api/projects/:id/export/markdown` - Export project as Markdown
- `GET /api/projects/:id/export/json` - Export project as JSON
- `GET /api/hardware` - Get hardware library
- `POST /api/shopping-list` - Generate shopping list with links
