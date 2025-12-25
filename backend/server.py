from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from enum import Enum
import asyncio
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================== ENUMS ==================

class ProjectStage(str, Enum):
    IDEA = "idea"
    REQUIREMENTS = "requirements"
    HARDWARE = "hardware"
    ARCHITECTURE = "architecture"
    CODE = "code"
    EXPLANATION = "explanation"
    ITERATION = "iteration"

class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"

# ================== MODELS ==================

class StageData(BaseModel):
    content: Optional[str] = None
    generated_at: Optional[str] = None
    user_approved: bool = False
    notes: Optional[str] = None

class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    idea: str
    description: Optional[str] = None
    target_hardware: str = "ESP32 DevKit V1"
    status: ProjectStatus = ProjectStatus.ACTIVE
    current_stage: ProjectStage = ProjectStage.IDEA
    stages: Dict[str, StageData] = Field(default_factory=lambda: {
        "idea": StageData(user_approved=True),
        "requirements": StageData(),
        "hardware": StageData(),
        "architecture": StageData(),
        "code": StageData(),
        "explanation": StageData(),
        "iteration": StageData()
    })
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ProjectCreate(BaseModel):
    name: str
    idea: str
    description: Optional[str] = None
    target_hardware: str = "ESP32 DevKit V1"

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_hardware: Optional[str] = None
    status: Optional[ProjectStatus] = None

class StageApproval(BaseModel):
    stage: ProjectStage
    approved: bool
    notes: Optional[str] = None

class LLMRequest(BaseModel):
    project_id: str
    stage: ProjectStage
    user_message: Optional[str] = None

class LLMProvider(str, Enum):
    OPENAI = "openai"
    GROQ = "groq"
    OPENROUTER = "openrouter"

class SettingsModel(BaseModel):
    provider: LLMProvider = LLMProvider.OPENAI
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    theme: str = "system"

# ================== HARDWARE LIBRARY ==================

HARDWARE_LIBRARY = {
    "sensors": [
        {
            "id": "dht22",
            "name": "DHT22",
            "type": "Temperature & Humidity",
            "interface": "Digital (OneWire-like)",
            "library": "DHT sensor library",
            "wiring": {
                "VCC": "3.3V or 5V",
                "GND": "GND",
                "DATA": "GPIO (with 10K pull-up)"
            },
            "notes": "Use 10K pull-up resistor between DATA and VCC"
        },
        {
            "id": "dht11",
            "name": "DHT11",
            "type": "Temperature & Humidity",
            "interface": "Digital",
            "library": "DHT sensor library",
            "wiring": {
                "VCC": "3.3V or 5V",
                "GND": "GND",
                "DATA": "GPIO (with 10K pull-up)"
            },
            "notes": "Lower precision than DHT22, but cheaper"
        },
        {
            "id": "bme280",
            "name": "BME280",
            "type": "Temperature, Humidity, Pressure",
            "interface": "I2C / SPI",
            "library": "Adafruit BME280 Library",
            "wiring": {
                "VCC": "3.3V",
                "GND": "GND",
                "SDA": "GPIO21",
                "SCL": "GPIO22"
            },
            "notes": "Default I2C address: 0x76 or 0x77"
        },
        {
            "id": "ds18b20",
            "name": "DS18B20",
            "type": "Temperature (Waterproof)",
            "interface": "OneWire",
            "library": "OneWire + DallasTemperature",
            "wiring": {
                "VCC": "3.3V or 5V",
                "GND": "GND",
                "DATA": "GPIO (with 4.7K pull-up)"
            },
            "notes": "Can chain multiple sensors on same bus"
        }
    ],
    "displays": [
        {
            "id": "ssd1306",
            "name": "SSD1306 OLED",
            "type": "OLED Display 0.96\"",
            "interface": "I2C",
            "library": "Adafruit SSD1306 + GFX",
            "wiring": {
                "VCC": "3.3V",
                "GND": "GND",
                "SDA": "GPIO21",
                "SCL": "GPIO22"
            },
            "notes": "128x64 pixels, I2C address: 0x3C or 0x3D"
        }
    ],
    "actuators": [
        {
            "id": "relay",
            "name": "Relay Module",
            "type": "Switching",
            "interface": "Digital GPIO",
            "library": "None (digitalWrite)",
            "wiring": {
                "VCC": "5V",
                "GND": "GND",
                "IN": "GPIO"
            },
            "notes": "Use optocoupled relay for safety. Active LOW common."
        }
    ],
    "analog": [
        {
            "id": "analog_sensor",
            "name": "Generic Analog Sensor",
            "type": "Analog Input",
            "interface": "ADC",
            "library": "None (analogRead)",
            "wiring": {
                "VCC": "3.3V",
                "GND": "GND",
                "OUT": "GPIO32-39 (ADC pins)"
            },
            "notes": "ESP32 ADC is 12-bit (0-4095). Use ADC1 pins for WiFi compatibility."
        }
    ]
}

# ================== LLM HELPER ==================

async def generate_llm_response(project: dict, stage: ProjectStage, user_message: Optional[str] = None) -> str:
    """Generate LLM response for a specific stage"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API key not configured")
    
    # Build system message based on stage
    system_prompts = {
        ProjectStage.REQUIREMENTS: """You are an ESP32 IoT project expert. Analyze the user's project idea and extract clear, structured requirements.
Output format:
## Functional Requirements
- List each functional requirement

## Hardware Requirements
- List sensors, actuators, displays needed

## Communication Requirements
- WiFi, MQTT, HTTP, Serial, etc.

## Power Requirements
- Battery, USB, mains considerations

## Constraints
- Any limitations or special considerations

Be specific to ESP32 capabilities. Keep it practical and achievable.""",

        ProjectStage.HARDWARE: f"""You are an ESP32 hardware expert. Based on the project requirements, recommend specific hardware components and provide wiring guidance.

Available hardware library:
{json.dumps(HARDWARE_LIBRARY, indent=2)}

Output format:
## Recommended Components
List each component with:
- Name and model
- Purpose in this project
- Quantity needed

## Wiring Diagram (Text)
Provide clear pin connections:
Component -> ESP32
- Pin: GPIO

## Wiring Notes
- Pull-up/down resistors needed
- Power considerations
- Common mistakes to avoid

## Shopping List
Simple list of what to buy.""",

        ProjectStage.ARCHITECTURE: """You are an ESP32 firmware architect. Design the software architecture for this IoT project.

Output format:
## Architecture Overview
Brief description of the system design

## Module Structure
- Main loop responsibilities
- Sensor reading module
- Communication module
- Display module (if applicable)
- Configuration/Settings

## State Machine
If applicable, describe states and transitions

## Data Flow
How data moves through the system

## Libraries Required
List Arduino libraries needed with install instructions

## Memory Considerations
RAM and Flash usage estimates""",

        ProjectStage.CODE: """You are an ESP32 Arduino developer. Generate complete, compilable firmware code.

Requirements:
- Use Arduino framework for ESP32
- Include all necessary #include statements
- Define all pins at the top
- Add clear comments
- Handle errors gracefully
- Include Serial debug output
- Use non-blocking code where possible

Output complete, ready-to-compile code with:
1. Header with project description
2. Pin definitions
3. Library includes
4. Global variables
5. Setup function
6. Loop function
7. Helper functions

Make the code production-ready and educational.""",

        ProjectStage.EXPLANATION: """You are an ESP32 educator. Explain the generated code and architecture in a way that helps the user learn.

Output format:
## How It Works
High-level explanation

## Code Walkthrough
Explain each major section:
- Setup phase
- Main loop logic
- Key functions

## Key Concepts
Explain important concepts used:
- Timers, interrupts, protocols, etc.

## Common Modifications
How to customize or extend this code

## Debugging Tips
How to troubleshoot common issues

## Learning Resources
Links and references for deeper learning""",

        ProjectStage.ITERATION: """You are an ESP32 expert helping iterate on an existing project. Based on user feedback, suggest improvements, fix bugs, or add features.

Be specific and provide code snippets where helpful. Consider:
- Performance improvements
- Power optimization
- Code cleanliness
- Feature additions
- Bug fixes"""
    }
    
    system_message = system_prompts.get(stage, "You are an ESP32 IoT expert assistant.")
    
    # Build context from project
    context_parts = [f"Project: {project['name']}", f"Idea: {project['idea']}"]
    
    if project.get('description'):
        context_parts.append(f"Description: {project['description']}")
    
    context_parts.append(f"Target Hardware: {project['target_hardware']}")
    
    # Add previous stage outputs
    stages_order = ["idea", "requirements", "hardware", "architecture", "code", "explanation"]
    stage_idx = stages_order.index(stage.value) if stage.value in stages_order else 0
    
    for prev_stage in stages_order[:stage_idx]:
        stage_data = project.get('stages', {}).get(prev_stage, {})
        if stage_data.get('content'):
            context_parts.append(f"\n=== {prev_stage.upper()} ===\n{stage_data['content']}")
    
    context = "\n".join(context_parts)
    
    # Create chat instance
    chat = LlmChat(
        api_key=api_key,
        session_id=f"esp32-{project['id']}-{stage.value}",
        system_message=system_message
    ).with_model("openai", "gpt-4o")
    
    # Build user message
    if user_message:
        full_message = f"Project Context:\n{context}\n\nUser Request: {user_message}"
    else:
        full_message = f"Project Context:\n{context}\n\nPlease generate the {stage.value} for this project."
    
    user_msg = UserMessage(text=full_message)
    response = await chat.send_message(user_msg)
    
    return response

# ================== ROUTES ==================

@api_router.get("/")
async def root():
    return {"message": "ESP32 IoT Copilot API", "version": "1.0.0"}

@api_router.get("/health")
async def health():
    return {"status": "healthy"}

# Project CRUD
@api_router.post("/projects", response_model=Project)
async def create_project(input: ProjectCreate):
    project = Project(
        name=input.name,
        idea=input.idea,
        description=input.description,
        target_hardware=input.target_hardware
    )
    project.stages["idea"] = StageData(
        content=input.idea,
        generated_at=datetime.now(timezone.utc).isoformat(),
        user_approved=True
    )
    
    doc = project.model_dump()
    await db.projects.insert_one(doc)
    return project

@api_router.get("/projects", response_model=List[Project])
async def list_projects(status: Optional[ProjectStatus] = None):
    query = {}
    if status:
        query["status"] = status.value
    
    projects = await db.projects.find(query, {"_id": 0}).sort("updated_at", -1).to_list(100)
    return projects

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@api_router.patch("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, update: ProjectUpdate):
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.projects.update_one({"id": project_id}, {"$set": update_data})
    
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}

# Stage Management
@api_router.post("/projects/{project_id}/stages/{stage}/approve")
async def approve_stage(project_id: str, stage: ProjectStage, approval: StageApproval):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    stages = project.get("stages", {})
    stage_data = stages.get(stage.value, {})
    stage_data["user_approved"] = approval.approved
    if approval.notes:
        stage_data["notes"] = approval.notes
    
    stages[stage.value] = stage_data
    
    # Move to next stage if approved
    next_stage = None
    if approval.approved:
        stage_order = ["idea", "requirements", "hardware", "architecture", "code", "explanation", "iteration"]
        current_idx = stage_order.index(stage.value)
        if current_idx < len(stage_order) - 1:
            next_stage = stage_order[current_idx + 1]
    
    update_data = {
        "stages": stages,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    if next_stage:
        update_data["current_stage"] = next_stage
    
    await db.projects.update_one({"id": project_id}, {"$set": update_data})
    
    return {"message": "Stage approval updated", "next_stage": next_stage}

# LLM Generation
@api_router.post("/projects/{project_id}/generate")
async def generate_stage_content(project_id: str, request: LLMRequest):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        content = await generate_llm_response(project, request.stage, request.user_message)
        
        # Update project with generated content
        stages = project.get("stages", {})
        stages[request.stage.value] = {
            "content": content,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "user_approved": False,
            "notes": None
        }
        
        # Add to conversation history
        conversation = project.get("conversation_history", [])
        if request.user_message:
            conversation.append({"role": "user", "content": request.user_message, "stage": request.stage.value})
        conversation.append({"role": "assistant", "content": content, "stage": request.stage.value})
        
        await db.projects.update_one(
            {"id": project_id},
            {"$set": {
                "stages": stages,
                "conversation_history": conversation,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {"content": content, "stage": request.stage.value}
    
    except Exception as e:
        logger.error(f"LLM generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

# Hardware Library
@api_router.get("/hardware")
async def get_hardware_library():
    return HARDWARE_LIBRARY

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
