from fastapi import FastAPI, APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse, Response
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
import json
import httpx

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

class LLMProvider(str, Enum):
    OPENAI = "openai"
    GROQ = "groq"
    OPENROUTER = "openrouter"

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
    selected_components: List[str] = Field(default_factory=list)
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
    selected_components: Optional[List[str]] = None

class StageApproval(BaseModel):
    stage: ProjectStage
    approved: bool
    notes: Optional[str] = None

class LLMRequest(BaseModel):
    project_id: str
    stage: ProjectStage
    user_message: Optional[str] = None
    provider: LLMProvider = LLMProvider.OPENAI
    model: Optional[str] = None
    api_key: Optional[str] = None

class ShoppingListRequest(BaseModel):
    component_ids: List[str]

class WiringDiagramRequest(BaseModel):
    component_ids: List[str]

class DebugRequest(BaseModel):
    project_id: str
    error_type: str  # compilation, runtime, hardware, power
    log_content: str
    provider: LLMProvider = LLMProvider.OPENAI
    model: Optional[str] = None
    api_key: Optional[str] = None

# ================== ESP32 PIN MAPPING ==================

ESP32_PIN_MAP = {
    "i2c": {
        "SDA": "GPIO21",
        "SCL": "GPIO22"
    },
    "spi_vspi": {
        "MOSI": "GPIO23",
        "MISO": "GPIO19",
        "SCK": "GPIO18",
        "CS": "GPIO5"
    },
    "spi_hspi": {
        "MOSI": "GPIO13",
        "MISO": "GPIO12",
        "SCK": "GPIO14",
        "CS": "GPIO15"
    },
    "uart": {
        "TX": "GPIO1",
        "RX": "GPIO3"
    },
    "adc1": ["GPIO32", "GPIO33", "GPIO34", "GPIO35", "GPIO36", "GPIO39"],
    "adc2": ["GPIO0", "GPIO2", "GPIO4", "GPIO12", "GPIO13", "GPIO14", "GPIO15", "GPIO25", "GPIO26", "GPIO27"],
    "dac": ["GPIO25", "GPIO26"],
    "touch": ["GPIO0", "GPIO2", "GPIO4", "GPIO12", "GPIO13", "GPIO14", "GPIO15", "GPIO27", "GPIO32", "GPIO33"],
    "pwm": ["GPIO2", "GPIO4", "GPIO5", "GPIO12", "GPIO13", "GPIO14", "GPIO15", "GPIO16", "GPIO17", "GPIO18", "GPIO19", "GPIO21", "GPIO22", "GPIO23", "GPIO25", "GPIO26", "GPIO27", "GPIO32", "GPIO33"],
    "digital_recommended": ["GPIO4", "GPIO5", "GPIO16", "GPIO17", "GPIO18", "GPIO19", "GPIO23", "GPIO25", "GPIO26", "GPIO27", "GPIO32", "GPIO33"]
}

# ================== PROJECT TEMPLATES ==================

PROJECT_TEMPLATES = [
    {
        "id": "temperature_logger",
        "name": "Temperature Logger",
        "description": "Log temperature and humidity to Serial and optionally MQTT",
        "icon": "thermometer",
        "difficulty": "beginner",
        "components": ["esp32_devkit", "bme280", "breadboard", "jumper_wires"],
        "idea": "Build a temperature and humidity logger using BME280 sensor that outputs readings to Serial monitor every 5 seconds. Include WiFi connectivity for optional MQTT publishing to a home automation system.",
        "features": ["I2C sensor reading", "Serial output", "WiFi connectivity", "MQTT publishing"],
        "learning_topics": ["I2C protocol", "Sensor libraries", "WiFi configuration", "MQTT basics"]
    },
    {
        "id": "oled_sensor_display",
        "name": "OLED Sensor Display",
        "description": "Display real-time sensor data on an OLED screen",
        "icon": "monitor",
        "difficulty": "beginner",
        "components": ["esp32_devkit", "ssd1306", "dht22", "breadboard", "jumper_wires", "resistor_kit"],
        "idea": "Create a standalone sensor display unit using DHT22 temperature/humidity sensor and SSD1306 OLED display. Show current readings, min/max values, and a simple graph of recent measurements.",
        "features": ["I2C display", "DHT sensor reading", "Data visualization", "Min/max tracking"],
        "learning_topics": ["Multiple I2C devices", "Display graphics", "Data structures", "Non-blocking code"]
    },
    {
        "id": "relay_controller",
        "name": "Smart Relay Controller",
        "description": "Control a relay via button, timer, or web interface",
        "icon": "zap",
        "difficulty": "intermediate",
        "components": ["esp32_devkit", "relay", "breadboard", "jumper_wires"],
        "idea": "Build a smart relay controller with multiple control modes: physical button, timer-based scheduling, and web interface. Include safety features like maximum on-time and state persistence across reboots.",
        "features": ["GPIO control", "Web server", "Timer scheduling", "EEPROM persistence"],
        "learning_topics": ["Relay safety", "Web server basics", "State machines", "EEPROM/Preferences"]
    },
    {
        "id": "battery_sensor_node",
        "name": "Battery-Powered Sensor Node",
        "description": "Low-power sensor that wakes periodically to send data",
        "icon": "battery",
        "difficulty": "intermediate",
        "components": ["esp32_devkit", "ds18b20", "breadboard", "jumper_wires", "resistor_kit"],
        "idea": "Design a battery-optimized sensor node using DS18B20 temperature sensor. Implement deep sleep mode, wake every 15 minutes to read sensor and send data via WiFi, then return to sleep. Target battery life of 6+ months on 2xAA batteries.",
        "features": ["Deep sleep", "OneWire sensor", "WiFi transmission", "Power optimization"],
        "learning_topics": ["Power management", "Deep sleep modes", "Wake sources", "Current measurement"]
    },
    {
        "id": "motion_alarm",
        "name": "Motion Detection Alarm",
        "description": "PIR-based motion detector with buzzer alert and notifications",
        "icon": "alert-triangle",
        "difficulty": "beginner",
        "components": ["esp32_devkit", "pir_motion", "buzzer", "led_strip", "breadboard", "jumper_wires"],
        "idea": "Create a motion detection alarm system using HC-SR501 PIR sensor. When motion is detected, activate a buzzer, flash LED strip, and optionally send a notification via WiFi. Include arm/disarm functionality via button or web interface.",
        "features": ["PIR sensing", "Audio alert", "LED indication", "WiFi notifications"],
        "learning_topics": ["Interrupt handling", "Debouncing", "HTTP requests", "State management"]
    },
    {
        "id": "plant_monitor",
        "name": "Smart Plant Monitor",
        "description": "Monitor soil moisture, light, and environmental conditions",
        "icon": "leaf",
        "difficulty": "intermediate",
        "components": ["esp32_devkit", "soil_moisture", "dht22", "ssd1306", "relay", "water_pump", "breadboard", "jumper_wires", "resistor_kit"],
        "idea": "Build an automated plant care system that monitors soil moisture, temperature, and humidity. Display readings on OLED screen. Automatically water plants when soil is dry using a relay-controlled pump. Include configurable thresholds and manual override.",
        "features": ["Analog sensor reading", "Automatic watering", "Threshold configuration", "Manual override"],
        "learning_topics": ["ADC calibration", "Hysteresis", "Pump control safety", "Multi-sensor systems"]
    }
]

# ================== HARDWARE LIBRARY WITH SHOPPING LINKS ==================

HARDWARE_LIBRARY = {
    "sensors": [
        {
            "id": "dht22",
            "name": "DHT22",
            "type": "Temperature & Humidity",
            "interface": "Digital (OneWire-like)",
            "library": "DHT sensor library",
            "price_estimate": "$3-8",
            "wiring": {
                "VCC": "3.3V or 5V",
                "GND": "GND",
                "DATA": "GPIO (with 10K pull-up)"
            },
            "notes": "Use 10K pull-up resistor between DATA and VCC",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=DHT22+sensor+module",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=DHT22+sensor+module"
            }
        },
        {
            "id": "dht11",
            "name": "DHT11",
            "type": "Temperature & Humidity",
            "interface": "Digital",
            "library": "DHT sensor library",
            "price_estimate": "$1-3",
            "wiring": {
                "VCC": "3.3V or 5V",
                "GND": "GND",
                "DATA": "GPIO (with 10K pull-up)"
            },
            "notes": "Lower precision than DHT22, but cheaper",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=DHT11+sensor+module",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=DHT11+sensor+module"
            }
        },
        {
            "id": "bme280",
            "name": "BME280",
            "type": "Temperature, Humidity, Pressure",
            "interface": "I2C / SPI",
            "library": "Adafruit BME280 Library",
            "price_estimate": "$5-12",
            "wiring": {
                "VCC": "3.3V",
                "GND": "GND",
                "SDA": "GPIO21",
                "SCL": "GPIO22"
            },
            "notes": "Default I2C address: 0x76 or 0x77",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=BME280+sensor+module",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=BME280+sensor+module"
            }
        },
        {
            "id": "ds18b20",
            "name": "DS18B20",
            "type": "Temperature (Waterproof)",
            "interface": "OneWire",
            "library": "OneWire + DallasTemperature",
            "price_estimate": "$2-5",
            "wiring": {
                "VCC": "3.3V or 5V",
                "GND": "GND",
                "DATA": "GPIO (with 4.7K pull-up)"
            },
            "notes": "Can chain multiple sensors on same bus",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=DS18B20+waterproof+sensor",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=DS18B20+waterproof+temperature"
            }
        },
        {
            "id": "soil_moisture",
            "name": "Capacitive Soil Moisture Sensor",
            "type": "Soil Moisture",
            "interface": "Analog",
            "library": "None (analogRead)",
            "price_estimate": "$2-5",
            "wiring": {
                "VCC": "3.3V",
                "GND": "GND",
                "AOUT": "GPIO32-39 (ADC pins)"
            },
            "notes": "Capacitive type is more durable than resistive. Use ADC1 pins.",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=capacitive+soil+moisture+sensor",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=capacitive+soil+moisture+sensor"
            }
        },
        {
            "id": "pir_motion",
            "name": "HC-SR501 PIR Motion Sensor",
            "type": "Motion Detection",
            "interface": "Digital",
            "library": "None (digitalRead)",
            "price_estimate": "$1-3",
            "wiring": {
                "VCC": "5V",
                "GND": "GND",
                "OUT": "Any GPIO"
            },
            "notes": "Adjustable sensitivity and delay. Output is HIGH when motion detected.",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=HC-SR501+PIR+sensor",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=HC-SR501+PIR+motion"
            }
        },
        {
            "id": "ultrasonic",
            "name": "HC-SR04 Ultrasonic Sensor",
            "type": "Distance Measurement",
            "interface": "Digital (Trigger/Echo)",
            "library": "NewPing or built-in",
            "price_estimate": "$2-4",
            "wiring": {
                "VCC": "5V",
                "GND": "GND",
                "TRIG": "Any GPIO",
                "ECHO": "Any GPIO (use voltage divider for 3.3V)"
            },
            "notes": "Range: 2cm-400cm. Echo pin outputs 5V, use voltage divider.",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=HC-SR04+ultrasonic+sensor",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=HC-SR04+ultrasonic"
            }
        }
    ],
    "displays": [
        {
            "id": "ssd1306",
            "name": "SSD1306 OLED 0.96\"",
            "type": "OLED Display",
            "interface": "I2C",
            "library": "Adafruit SSD1306 + GFX",
            "price_estimate": "$3-8",
            "wiring": {
                "VCC": "3.3V",
                "GND": "GND",
                "SDA": "GPIO21",
                "SCL": "GPIO22"
            },
            "notes": "128x64 pixels, I2C address: 0x3C or 0x3D",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=SSD1306+OLED+0.96",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=SSD1306+OLED+0.96"
            }
        },
        {
            "id": "lcd1602_i2c",
            "name": "LCD 16x2 with I2C",
            "type": "LCD Display",
            "interface": "I2C",
            "library": "LiquidCrystal_I2C",
            "price_estimate": "$3-6",
            "wiring": {
                "VCC": "5V",
                "GND": "GND",
                "SDA": "GPIO21",
                "SCL": "GPIO22"
            },
            "notes": "I2C backpack simplifies wiring. Address usually 0x27 or 0x3F",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=LCD+1602+I2C+module",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=LCD+1602+I2C"
            }
        },
        {
            "id": "tft_st7789",
            "name": "TFT Display ST7789 1.3\"",
            "type": "Color TFT Display",
            "interface": "SPI",
            "library": "TFT_eSPI or Adafruit ST7789",
            "price_estimate": "$5-10",
            "wiring": {
                "VCC": "3.3V",
                "GND": "GND",
                "SCL": "GPIO18",
                "SDA": "GPIO23",
                "RES": "GPIO4",
                "DC": "GPIO2",
                "CS": "GPIO15"
            },
            "notes": "240x240 pixels, full color. Fast SPI interface.",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=ST7789+TFT+display+1.3",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=ST7789+TFT+1.3"
            }
        }
    ],
    "actuators": [
        {
            "id": "relay",
            "name": "Relay Module (1 Channel)",
            "type": "Switching",
            "interface": "Digital GPIO",
            "library": "None (digitalWrite)",
            "price_estimate": "$1-3",
            "wiring": {
                "VCC": "5V",
                "GND": "GND",
                "IN": "Any GPIO"
            },
            "notes": "Use optocoupled relay for safety. Active LOW common.",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=relay+module+5V+optocoupler",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=relay+module+5V+optocoupler"
            }
        },
        {
            "id": "relay_4ch",
            "name": "Relay Module (4 Channel)",
            "type": "Switching",
            "interface": "Digital GPIO",
            "library": "None (digitalWrite)",
            "price_estimate": "$4-8",
            "wiring": {
                "VCC": "5V",
                "GND": "GND",
                "IN1-IN4": "Any GPIO"
            },
            "notes": "4 independent relays. Optocoupled recommended.",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=4+channel+relay+module+5V",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=4+channel+relay+module"
            }
        },
        {
            "id": "servo_sg90",
            "name": "SG90 Micro Servo",
            "type": "Servo Motor",
            "interface": "PWM",
            "library": "ESP32Servo",
            "price_estimate": "$2-4",
            "wiring": {
                "VCC": "5V (external recommended)",
                "GND": "GND",
                "Signal": "Any PWM GPIO"
            },
            "notes": "180° rotation. Use external 5V supply for multiple servos.",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=SG90+micro+servo",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=SG90+micro+servo"
            }
        },
        {
            "id": "water_pump",
            "name": "Mini Water Pump DC 3-6V",
            "type": "Water Pump",
            "interface": "Via Relay/MOSFET",
            "library": "None",
            "price_estimate": "$2-5",
            "wiring": {
                "VCC": "3-6V (via relay)",
                "GND": "GND"
            },
            "notes": "Control via relay or MOSFET. Add flyback diode for protection.",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=mini+water+pump+DC+3V+6V",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=mini+water+pump+DC"
            }
        },
        {
            "id": "buzzer",
            "name": "Active Buzzer Module",
            "type": "Audio Output",
            "interface": "Digital GPIO",
            "library": "None (digitalWrite)",
            "price_estimate": "$0.50-2",
            "wiring": {
                "VCC": "3.3V or 5V",
                "GND": "GND",
                "I/O": "Any GPIO"
            },
            "notes": "Active buzzer - just apply voltage. Passive needs PWM for tone.",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=active+buzzer+module",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=active+buzzer+module"
            }
        },
        {
            "id": "led_strip",
            "name": "WS2812B LED Strip (NeoPixel)",
            "type": "RGB LED Strip",
            "interface": "Digital (Data)",
            "library": "FastLED or Adafruit NeoPixel",
            "price_estimate": "$5-15",
            "wiring": {
                "VCC": "5V (external supply for long strips)",
                "GND": "GND",
                "DIN": "Any GPIO (through 330Ω resistor)"
            },
            "notes": "Addressable RGB. Use capacitor (1000µF) for power supply.",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=WS2812B+LED+strip",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=WS2812B+LED+strip"
            }
        }
    ],
    "boards": [
        {
            "id": "esp32_devkit",
            "name": "ESP32 DevKit V1",
            "type": "Development Board",
            "interface": "USB",
            "library": "ESP32 Arduino Core",
            "price_estimate": "$5-10",
            "wiring": {},
            "notes": "Most common ESP32 board. 30 or 38 pin versions available.",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=ESP32+DevKit+V1",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=ESP32+DevKit+V1"
            }
        },
        {
            "id": "breadboard",
            "name": "Breadboard 830 Points",
            "type": "Prototyping",
            "interface": "N/A",
            "library": "N/A",
            "price_estimate": "$2-5",
            "wiring": {},
            "notes": "Standard solderless breadboard for prototyping.",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=breadboard+830+points",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=breadboard+830+points"
            }
        },
        {
            "id": "jumper_wires",
            "name": "Jumper Wires Kit (M-M, M-F, F-F)",
            "type": "Wiring",
            "interface": "N/A",
            "library": "N/A",
            "price_estimate": "$3-6",
            "wiring": {},
            "notes": "Essential for breadboard prototyping.",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=jumper+wires+kit+dupont",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=jumper+wires+kit+dupont"
            }
        },
        {
            "id": "resistor_kit",
            "name": "Resistor Kit (Various Values)",
            "type": "Components",
            "interface": "N/A",
            "library": "N/A",
            "price_estimate": "$3-8",
            "wiring": {},
            "notes": "Common values: 220Ω, 330Ω, 1K, 4.7K, 10K needed for pull-ups/LEDs.",
            "shopping_links": {
                "amazon": "https://www.amazon.com/s?k=resistor+assortment+kit",
                "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=resistor+assortment+kit"
            }
        }
    ]
}

# ================== LLM PROVIDERS ==================

async def call_groq_api(messages: List[dict], model: str, api_key: str) -> str:
    """Call Groq API directly"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.7
            },
            timeout=120.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Groq API error: {response.text}")
        data = response.json()
        return data["choices"][0]["message"]["content"]

async def call_openrouter_api(messages: List[dict], model: str, api_key: str) -> str:
    """Call OpenRouter API"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://esp32-copilot.app",
                "X-Title": "ESP32 IoT Copilot"
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.7
            },
            timeout=120.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"OpenRouter API error: {response.text}")
        data = response.json()
        return data["choices"][0]["message"]["content"]

async def call_emergent_api(messages: List[dict], model: str = "gpt-4o") -> str:
    """Call OpenAI via Emergent integration"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="Emergent LLM API key not configured")
    
    # Extract system message and user messages
    system_msg = next((m["content"] for m in messages if m["role"] == "system"), "You are a helpful assistant.")
    user_content = "\n\n".join(m["content"] for m in messages if m["role"] == "user")
    
    chat = LlmChat(
        api_key=api_key,
        session_id=f"esp32-{uuid.uuid4()}",
        system_message=system_msg
    ).with_model("openai", model)
    
    user_msg = UserMessage(text=user_content)
    response = await chat.send_message(user_msg)
    return response

# ================== LLM HELPER ==================

def get_system_prompt(stage: ProjectStage, hardware_library: dict) -> str:
    """Get system prompt for each stage"""
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
{json.dumps(hardware_library, indent=2)}

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
    
    return system_prompts.get(stage, "You are an ESP32 IoT expert assistant.")

async def generate_llm_response(
    project: dict, 
    stage: ProjectStage, 
    user_message: Optional[str] = None,
    provider: LLMProvider = LLMProvider.OPENAI,
    model: Optional[str] = None,
    api_key: Optional[str] = None
) -> str:
    """Generate LLM response for a specific stage"""
    
    system_message = get_system_prompt(stage, HARDWARE_LIBRARY)
    
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
    
    # Build user message
    if user_message:
        full_message = f"Project Context:\n{context}\n\nUser Request: {user_message}"
    else:
        full_message = f"Project Context:\n{context}\n\nPlease generate the {stage.value} for this project."
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": full_message}
    ]
    
    # Route to appropriate provider
    if provider == LLMProvider.GROQ:
        if not api_key:
            raise HTTPException(status_code=400, detail="Groq API key required")
        model = model or "llama-3.1-70b-versatile"
        return await call_groq_api(messages, model, api_key)
    
    elif provider == LLMProvider.OPENROUTER:
        if not api_key:
            raise HTTPException(status_code=400, detail="OpenRouter API key required")
        model = model or "anthropic/claude-3.5-sonnet"
        return await call_openrouter_api(messages, model, api_key)
    
    else:  # Default to OpenAI via Emergent
        model = model or "gpt-4o"
        return await call_emergent_api(messages, model)

# ================== ROUTES ==================

@api_router.get("/")
async def root():
    return {"message": "ESP32 IoT Copilot API", "version": "1.1.0"}

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
        content = await generate_llm_response(
            project, 
            request.stage, 
            request.user_message,
            request.provider,
            request.model,
            request.api_key
        )
        
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

# Shopping List Generator
@api_router.post("/shopping-list")
async def generate_shopping_list(request: ShoppingListRequest):
    """Generate a shopping list with links for selected components"""
    all_components = []
    for category in HARDWARE_LIBRARY.values():
        all_components.extend(category)
    
    selected = []
    total_min = 0
    total_max = 0
    
    for comp_id in request.component_ids:
        component = next((c for c in all_components if c["id"] == comp_id), None)
        if component:
            # Parse price estimate
            price_str = component.get("price_estimate", "$0")
            prices = price_str.replace("$", "").split("-")
            min_price = float(prices[0]) if prices[0] else 0
            max_price = float(prices[1]) if len(prices) > 1 else min_price
            
            selected.append({
                "id": component["id"],
                "name": component["name"],
                "type": component["type"],
                "price_estimate": component.get("price_estimate", "N/A"),
                "shopping_links": component.get("shopping_links", {}),
                "notes": component.get("notes", "")
            })
            total_min += min_price
            total_max += max_price
    
    return {
        "components": selected,
        "total_estimate": f"${total_min:.0f}-${total_max:.0f}",
        "component_count": len(selected)
    }

# Project Export
@api_router.get("/projects/{project_id}/export/markdown")
async def export_project_markdown(project_id: str):
    """Export project as markdown document"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    md_lines = [
        f"# {project['name']}",
        "",
        f"**Created:** {project.get('created_at', 'N/A')}",
        f"**Hardware:** {project.get('target_hardware', 'ESP32')}",
        f"**Status:** {project.get('status', 'active')}",
        "",
        "---",
        "",
        "## Project Idea",
        "",
        project.get('idea', ''),
        ""
    ]
    
    if project.get('description'):
        md_lines.extend([
            "## Description",
            "",
            project['description'],
            ""
        ])
    
    stage_titles = {
        "idea": "Idea",
        "requirements": "Requirements",
        "hardware": "Hardware Selection & Wiring",
        "architecture": "Firmware Architecture",
        "code": "Generated Code",
        "explanation": "Code Explanation",
        "iteration": "Iterations & Improvements"
    }
    
    stages = project.get('stages', {})
    for stage_key, title in stage_titles.items():
        stage_data = stages.get(stage_key, {})
        if stage_data.get('content') and stage_key != 'idea':
            md_lines.extend([
                "---",
                "",
                f"## {title}",
                "",
                stage_data['content'],
                ""
            ])
            if stage_data.get('notes'):
                md_lines.extend([
                    "**Notes:**",
                    stage_data['notes'],
                    ""
                ])
    
    markdown_content = "\n".join(md_lines)
    
    return Response(
        content=markdown_content,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{project["name"].replace(" ", "_")}_export.md"'
        }
    )

@api_router.get("/projects/{project_id}/export/json")
async def export_project_json(project_id: str):
    """Export project as JSON"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return Response(
        content=json.dumps(project, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{project["name"].replace(" ", "_")}_export.json"'
        }
    )

# ================== WIRING DIAGRAM GENERATOR ==================

def generate_ascii_wiring_diagram(component_ids: List[str]) -> dict:
    """Generate deterministic ASCII wiring diagram for selected components"""
    all_components = []
    for category in HARDWARE_LIBRARY.values():
        all_components.extend(category)
    
    selected = [c for c in all_components if c["id"] in component_ids]
    
    if not selected:
        return {"diagram": "No components selected", "warnings": [], "pin_assignments": {}}
    
    # Track used pins to detect conflicts
    used_pins = {}
    warnings = []
    pin_assignments = {}
    diagram_lines = []
    
    # Header
    diagram_lines.append("=" * 60)
    diagram_lines.append("ESP32 WIRING DIAGRAM")
    diagram_lines.append("=" * 60)
    diagram_lines.append("")
    
    # GPIO assignment counter for generic digital pins
    next_gpio_idx = 0
    gpio_pool = ESP32_PIN_MAP["digital_recommended"].copy()
    
    for component in selected:
        comp_id = component["id"]
        comp_name = component["name"]
        interface = component.get("interface", "")
        wiring = component.get("wiring", {})
        
        if not wiring:
            continue
        
        diagram_lines.append(f"ESP32                    {comp_name}")
        diagram_lines.append("-" * 50)
        
        comp_pins = {}
        
        for pin_name, pin_desc in wiring.items():
            assigned_pin = None
            
            # Power pins
            if pin_name.upper() in ["VCC", "VIN"]:
                if "3.3" in str(pin_desc):
                    assigned_pin = "3.3V"
                else:
                    assigned_pin = "5V (VIN)"
            elif pin_name.upper() == "GND":
                assigned_pin = "GND"
            
            # I2C pins
            elif pin_name.upper() in ["SDA", "SDL"]:
                assigned_pin = ESP32_PIN_MAP["i2c"]["SDA"]
            elif pin_name.upper() == "SCL":
                assigned_pin = ESP32_PIN_MAP["i2c"]["SCL"]
            
            # SPI pins
            elif pin_name.upper() in ["MOSI", "SDI", "DIN"]:
                assigned_pin = ESP32_PIN_MAP["spi_vspi"]["MOSI"]
            elif pin_name.upper() in ["MISO", "SDO", "DOUT"]:
                assigned_pin = ESP32_PIN_MAP["spi_vspi"]["MISO"]
            elif pin_name.upper() in ["SCK", "CLK", "SCLK"]:
                assigned_pin = ESP32_PIN_MAP["spi_vspi"]["SCK"]
            elif pin_name.upper() == "CS":
                assigned_pin = ESP32_PIN_MAP["spi_vspi"]["CS"]
            
            # ADC pins (analog sensors)
            elif pin_name.upper() in ["AOUT", "AO", "ANALOG"]:
                # Use ADC1 pins (safe with WiFi)
                for adc_pin in ESP32_PIN_MAP["adc1"]:
                    if adc_pin not in used_pins:
                        assigned_pin = adc_pin
                        break
                if not assigned_pin:
                    assigned_pin = "GPIO34 (ADC)"
                    warnings.append(f"{comp_name}: ADC pins limited, may conflict")
            
            # Generic digital pins (DATA, IN, OUT, SIGNAL, etc.)
            elif pin_name.upper() in ["DATA", "IN", "OUT", "SIGNAL", "DQ", "IO", "IN1", "IN2", "IN3", "IN4"]:
                # Get next available GPIO from pool
                while next_gpio_idx < len(gpio_pool):
                    candidate = gpio_pool[next_gpio_idx]
                    next_gpio_idx += 1
                    if candidate not in used_pins.values():
                        assigned_pin = candidate
                        break
                if not assigned_pin:
                    assigned_pin = f"GPIO{4 + next_gpio_idx}"
                    warnings.append(f"{comp_name}: Running low on recommended GPIOs")
            
            # Display/control pins
            elif pin_name.upper() in ["DC", "RS"]:
                assigned_pin = "GPIO2"
            elif pin_name.upper() in ["RES", "RST", "RESET"]:
                assigned_pin = "GPIO4"
            
            # Fallback
            else:
                assigned_pin = pin_desc
            
            if assigned_pin and assigned_pin not in ["GND", "3.3V", "5V (VIN)"]:
                # Check for conflicts
                if assigned_pin in used_pins and used_pins[assigned_pin] != comp_id:
                    warnings.append(f"PIN CONFLICT: {assigned_pin} used by both {used_pins[assigned_pin]} and {comp_name}")
                used_pins[assigned_pin] = comp_id
            
            comp_pins[pin_name] = assigned_pin
            
            # Format diagram line
            arrow = "-------->"
            note = ""
            if "pull-up" in str(pin_desc).lower():
                note = " [10K pull-up]"
            elif "pull-down" in str(pin_desc).lower():
                note = " [10K pull-down]"
            
            diagram_lines.append(f"{assigned_pin:20} {arrow} {pin_name}{note}")
        
        pin_assignments[comp_id] = comp_pins
        diagram_lines.append("")
    
    # Add notes section
    if any(c.get("notes") for c in selected):
        diagram_lines.append("=" * 60)
        diagram_lines.append("WIRING NOTES")
        diagram_lines.append("=" * 60)
        for component in selected:
            if component.get("notes"):
                diagram_lines.append(f"• {component['name']}: {component['notes']}")
        diagram_lines.append("")
    
    # Add warnings
    if warnings:
        diagram_lines.append("=" * 60)
        diagram_lines.append("⚠️  WARNINGS")
        diagram_lines.append("=" * 60)
        for warning in warnings:
            diagram_lines.append(f"• {warning}")
        diagram_lines.append("")
    
    # Add power notes
    diagram_lines.append("=" * 60)
    diagram_lines.append("POWER NOTES")
    diagram_lines.append("=" * 60)
    diagram_lines.append("• ESP32 3.3V pin can supply ~50mA max")
    diagram_lines.append("• For 5V components, use VIN or external supply")
    diagram_lines.append("• Relays/motors need external power supply")
    diagram_lines.append("• Add 100µF capacitor near sensor VCC for stability")
    
    return {
        "diagram": "\n".join(diagram_lines),
        "warnings": warnings,
        "pin_assignments": pin_assignments,
        "components": [{"id": c["id"], "name": c["name"]} for c in selected]
    }

@api_router.post("/wiring-diagram")
async def generate_wiring_diagram(request: WiringDiagramRequest):
    """Generate ASCII wiring diagram for selected components"""
    return generate_ascii_wiring_diagram(request.component_ids)

# ================== PROJECT TEMPLATES ==================

@api_router.get("/templates")
async def get_project_templates():
    """Get all available project templates"""
    return PROJECT_TEMPLATES

@api_router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template by ID"""
    template = next((t for t in PROJECT_TEMPLATES if t["id"] == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@api_router.post("/templates/{template_id}/instantiate")
async def instantiate_template(template_id: str):
    """Create a new project from a template"""
    template = next((t for t in PROJECT_TEMPLATES if t["id"] == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    project = Project(
        name=template["name"],
        idea=template["idea"],
        description=template["description"],
        target_hardware="ESP32 DevKit V1",
        selected_components=template.get("components", [])
    )
    project.stages["idea"] = StageData(
        content=template["idea"],
        generated_at=datetime.now(timezone.utc).isoformat(),
        user_approved=True
    )
    
    doc = project.model_dump()
    await db.projects.insert_one(doc)
    return project

# ================== DEBUG ASSISTANCE ==================

@api_router.post("/debug")
async def debug_assistance(request: DebugRequest):
    """Analyze error logs and provide debugging assistance"""
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    error_type_prompts = {
        "compilation": """You are an ESP32/Arduino compilation error expert. Analyze the following compiler error and provide:

## Error Classification
- Type of error (syntax, missing library, type mismatch, etc.)

## Root Cause
- Exact cause of the error
- Line/file if identifiable

## Solution
- Step-by-step fix instructions
- Corrected code snippet if applicable

## Prevention
- How to avoid this error in future

Be specific and actionable. Reference Arduino/ESP32 conventions.""",

        "runtime": """You are an ESP32 runtime debugging expert. Analyze the following runtime error/crash and provide:

## Error Classification  
- Type (crash, exception, watchdog, memory, etc.)

## Root Cause Analysis
- What caused this behavior
- Memory address analysis if applicable

## Solution
- Debugging steps
- Code fixes if identifiable

## Prevention
- Best practices to avoid this issue

Focus on ESP32-specific runtime behaviors.""",

        "hardware": """You are an ESP32 hardware debugging expert. Analyze the following hardware-related issue and provide:

## Problem Classification
- Type (wiring, power, signal, component failure)

## Diagnostic Steps
- How to verify the issue
- Measurements to take

## Solution
- Wiring corrections
- Component checks
- Code verification

## Common Causes
- Similar issues and their solutions

Focus on practical, hands-on debugging.""",

        "power": """You are an ESP32 power management expert. Analyze the following power-related issue and provide:

## Problem Classification
- Type (brownout, insufficient current, voltage drop, sleep issue)

## Root Cause
- Power budget analysis
- Supply adequacy

## Solution
- Power supply recommendations
- Circuit modifications
- Code changes for power optimization

## Best Practices
- Power management tips for this configuration"""
    }
    
    system_prompt = error_type_prompts.get(request.error_type, error_type_prompts["runtime"])
    
    # Build context
    context_parts = [
        f"Project: {project['name']}",
        f"Hardware: {project.get('target_hardware', 'ESP32')}",
        f"Idea: {project['idea']}"
    ]
    
    # Add code if available
    code_stage = project.get("stages", {}).get("code", {})
    if code_stage.get("content"):
        context_parts.append(f"\nGenerated Code:\n```\n{code_stage['content'][:2000]}...\n```")
    
    # Add hardware info
    hardware_stage = project.get("stages", {}).get("hardware", {})
    if hardware_stage.get("content"):
        context_parts.append(f"\nHardware Configuration:\n{hardware_stage['content'][:1000]}")
    
    context = "\n".join(context_parts)
    
    full_message = f"""Project Context:
{context}

Error Type: {request.error_type}

Log/Error Content:
```
{request.log_content}
```

Please analyze this {request.error_type} issue and provide debugging assistance."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": full_message}
    ]
    
    try:
        # Route to appropriate provider
        if request.provider == LLMProvider.GROQ:
            if not request.api_key:
                raise HTTPException(status_code=400, detail="Groq API key required")
            model = request.model or "llama-3.1-70b-versatile"
            response = await call_groq_api(messages, model, request.api_key)
        elif request.provider == LLMProvider.OPENROUTER:
            if not request.api_key:
                raise HTTPException(status_code=400, detail="OpenRouter API key required")
            model = request.model or "anthropic/claude-3.5-sonnet"
            response = await call_openrouter_api(messages, model, request.api_key)
        else:
            model = request.model or "gpt-4o"
            response = await call_emergent_api(messages, model)
        
        return {
            "analysis": response,
            "error_type": request.error_type,
            "project_id": request.project_id
        }
    
    except Exception as e:
        logger.error(f"Debug analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

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
