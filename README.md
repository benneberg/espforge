# ESP32 IoT Copilot

<div align="center">

![ESP32 IoT Copilot](https://img.shields.io/badge/ESP32-IoT%20Copilot-F59E0B?style=for-the-badge&logo=espressif&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-6.0-47A248?style=for-the-badge&logo=mongodb&logoColor=white)

**Your AI-powered companion for ESP32 IoT development**

*From idea → structured plan → wiring → firmware → working project*

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Templates](#project-templates) • [API Reference](#api-reference)

</div>

---

## Overview

ESP32 IoT Copilot is a mobile-first web application that guides makers, hobbyists, and engineers through the complete lifecycle of ESP32 IoT projects. Using AI-powered assistance, it transforms a simple project idea into structured requirements, hardware recommendations, wiring diagrams, compilable firmware, and educational explanations—with human approval at every step.

### Why ESP32 Copilot?

- **Learn while building** — Not just code generation, but understanding
- **Deterministic wiring** — No hallucinated pin assignments
- **Stage-gated workflow** — Approve each step before proceeding
- **Multi-provider LLM support** — OpenAI, Groq, or OpenRouter
- **Mobile-first design** — Build from your phone or tablet

---

## Features

### 🎯 Guided 7-Stage Workflow

Each project follows a structured path with explicit approval gates:

| Stage | Description |
|-------|-------------|
| **1. Idea** | Define your project concept in plain language |
| **2. Requirements** | AI extracts functional, hardware, and communication requirements |
| **3. Hardware** | Component recommendations with wiring guidance |
| **4. Architecture** | Firmware structure, state machines, data flow |
| **5. Code** | Complete, compilable ESP32/Arduino firmware |
| **6. Explanation** | Learn what the code does and why |
| **7. Iteration** | Refine, debug, and improve based on feedback |

### 🔌 ASCII Wiring Diagram Generator

Deterministic pin mappings based on interface type:

```
ESP32                    BME280
--------------------------------------------------
3.3V                 --------> VCC
GND                  --------> GND
GPIO21               --------> SDA
GPIO22               --------> SCL
```

- Automatic I2C (GPIO21/22), SPI (GPIO18/19/23), ADC (GPIO32-39) assignment
- Pin conflict detection with warnings
- Pull-up resistor reminders
- Copy-to-clipboard for documentation

### 🛒 Hardware Shopping List

- 20+ components across sensors, displays, actuators, and boards
- Price estimates ($1-15 per component)
- Direct links to Amazon and AliExpress
- Total project cost calculation

### 🐛 Debug Assistant

AI-powered troubleshooting for four error categories:

| Type | Examples |
|------|----------|
| **Compilation** | Missing libraries, syntax errors, type mismatches |
| **Runtime** | Crashes, watchdog resets, memory issues |
| **Hardware** | Wiring problems, signal issues, component failures |
| **Power** | Brownouts, insufficient current, deep sleep issues |

### 📚 Project Templates

Get started instantly with pre-configured projects:

| Template | Difficulty | Components |
|----------|------------|------------|
| Temperature Logger | Beginner | BME280, Serial, MQTT |
| OLED Sensor Display | Beginner | SSD1306, DHT22 |
| Smart Relay Controller | Intermediate | Relay, Web Server |
| Battery-Powered Node | Intermediate | DS18B20, Deep Sleep |
| Motion Detection Alarm | Beginner | PIR, Buzzer, LED Strip |
| Smart Plant Monitor | Intermediate | Soil Moisture, Pump, OLED |

### 📤 Export Options

- **Markdown** — Full project documentation
- **PDF** — Professional formatted export
- **JSON** — Raw data for backup/portability

### 🎨 Adaptive Theming

- Dark mode optimized for code and OLED screens
- Light mode for outdoor/bright environments
- System preference detection with manual override

### 🔑 Multi-Provider LLM Support

| Provider | Setup | Best For |
|----------|-------|----------|
| **OpenAI (Emergent)** | No config needed | Quality, default choice |
| **Groq** | Bring your own key | Speed (fastest inference) |
| **OpenRouter** | Bring your own key | Model variety, pay-per-use |

---

## Quick Start

### Prerequisites

- Node.js 18+ and Yarn
- Python 3.10+
- MongoDB 6.0+

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/esp32-copilot.git
cd esp32-copilot

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MONGO_URL and EMERGENT_LLM_KEY

# Start backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Frontend setup (new terminal)
cd frontend
yarn install
yarn start
```

### Environment Variables

**Backend (`/backend/.env`)**
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="esp32_copilot"
CORS_ORIGINS="*"
EMERGENT_LLM_KEY="your-emergent-key"  # Required for default LLM
```

**Frontend (`/frontend/.env`)**
```env
REACT_APP_BACKEND_URL="http://localhost:8001"
```

---

## Documentation

### Creating Your First Project

1. **Click "New"** in the bottom navigation
2. **Enter your idea** — Be specific about sensors, features, and connectivity
3. **Select target hardware** — ESP32 DevKit V1 is recommended for beginners
4. **Click "Create Project"**

### Using the Workflow

1. **Idea Stage** — Your idea is automatically approved
2. **Click "Generate requirements"** — AI extracts structured requirements
3. **Review and approve** — Click "Approve & Continue" or provide feedback
4. **Repeat** for Hardware, Architecture, Code, and Explanation stages

### Using Templates

1. **Navigate to Templates** in bottom navigation
2. **Select a template** based on difficulty and learning goals
3. **Click "Use Template"** — A new project is created with pre-filled data
4. **Continue through the workflow** — Requirements and beyond are still AI-generated

### Using the Debug Assistant

1. **Open a project** and click the **Debug** button
2. **Select error type** — Compilation, Runtime, Hardware, or Power
3. **Paste your error log** — Include complete output for best results
4. **Click "Analyze Error"** — AI provides diagnosis and fix suggestions

### Generating Wiring Diagrams

1. **Open a project** and click **Wiring Diagram**
2. **Diagram is auto-generated** based on selected components
3. **Review warnings** for pin conflicts or power issues
4. **Copy diagram** for your documentation or README

---

## Project Structure

```
esp32-copilot/
├── backend/
│   ├── server.py           # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/        # Shadcn UI components
│   │   │   ├── BottomNav.js
│   │   │   ├── CodeBlock.js
│   │   │   ├── DebugAssistant.js
│   │   │   ├── ProjectCard.js
│   │   │   ├── ProjectExport.js
│   │   │   ├── ShoppingList.js
│   │   │   ├── StageContent.js
│   │   │   └── WiringDiagram.js
│   │   │
│   │   ├── pages/
│   │   │   ├── Dashboard.js
│   │   │   ├── CreateProject.js
│   │   │   ├── ProjectDetail.js
│   │   │   ├── Settings.js
│   │   │   └── Templates.js
│   │   │
│   │   ├── context/
│   │   │   └── ThemeContext.js
│   │   │
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.css
│   │
│   ├── package.json
│   └── tailwind.config.js
│
└── requirements.md         # Project documentation
```

---

## API Reference

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/projects` | Create a new project |
| `GET` | `/api/projects` | List all projects (with optional status filter) |
| `GET` | `/api/projects/:id` | Get project by ID |
| `PATCH` | `/api/projects/:id` | Update project |
| `DELETE` | `/api/projects/:id` | Delete project |

### Stage Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/projects/:id/stages/:stage/approve` | Approve or reject a stage |
| `POST` | `/api/projects/:id/generate` | Generate content for a stage |

### Export

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/projects/:id/export/markdown` | Export as Markdown |
| `GET` | `/api/projects/:id/export/json` | Export as JSON |

### Hardware & Tools

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/hardware` | Get hardware component library |
| `POST` | `/api/shopping-list` | Generate shopping list |
| `POST` | `/api/wiring-diagram` | Generate ASCII wiring diagram |

### Templates

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/templates` | Get all project templates |
| `GET` | `/api/templates/:id` | Get specific template |
| `POST` | `/api/templates/:id/instantiate` | Create project from template |

### Debug

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/debug` | Analyze error with AI assistance |

---

## Hardware Library

### Supported Components

**Sensors**
- DHT22 / DHT11 — Temperature & Humidity
- BME280 — Temperature, Humidity, Pressure (I2C)
- DS18B20 — Waterproof Temperature (OneWire)
- Capacitive Soil Moisture — Analog
- HC-SR501 PIR — Motion Detection
- HC-SR04 — Ultrasonic Distance

**Displays**
- SSD1306 OLED 0.96" — I2C
- LCD 16x2 with I2C — Character Display
- ST7789 TFT 1.3" — Color Display (SPI)

**Actuators**
- Relay Module (1/4 Channel) — Switching
- SG90 Micro Servo — PWM
- Mini Water Pump — Via Relay
- Active Buzzer — Audio Alert
- WS2812B LED Strip — Addressable RGB

**Essentials**
- ESP32 DevKit V1 — Development Board
- Breadboard 830 Points — Prototyping
- Jumper Wires Kit — Wiring
- Resistor Kit — Pull-ups, Current Limiting

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, Tailwind CSS, Shadcn UI |
| **Backend** | FastAPI, Python 3.10+ |
| **Database** | MongoDB 6.0 |
| **LLM Integration** | OpenAI GPT-4o, Groq, OpenRouter |
| **Styling** | CSS Variables, Dark/Light Themes |
| **Code Highlighting** | react-syntax-highlighter (Prism) |
| **PDF Export** | jsPDF |

---

## Roadmap

### Completed
- [x] Project CRUD with 7-stage workflow
- [x] Multi-provider LLM integration
- [x] ASCII wiring diagram generator
- [x] Hardware shopping list with links
- [x] Project templates (6 templates)
- [x] Debug assistant (4 error types)
- [x] Export (Markdown, PDF, JSON)
- [x] Code syntax highlighting
- [x] Dark/Light theme support

### Planned
- [ ] Arduino CLI compilation validation
- [ ] SVG wiring diagrams
- [ ] Mobile PWA with offline support
- [ ] Project sharing via URL
- [ ] Version history and rollback

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/esp32-copilot.git

# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes and test
yarn test  # Frontend
pytest     # Backend

# Submit a pull request
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Espressif Systems](https://www.espressif.com/) for the ESP32 platform
- [Arduino](https://www.arduino.cc/) for the framework
- [OpenAI](https://openai.com/) for GPT models
- [Shadcn](https://ui.shadcn.com/) for UI components

---

<div align="center">

**Built with ❤️ for the maker community**

[Report Bug](https://github.com/your-org/esp32-copilot/issues) • [Request Feature](https://github.com/your-org/esp32-copilot/issues) • [Documentation](https://docs.esp32-copilot.dev)

</div>
