import requests
import sys
import json
from datetime import datetime

class ESP32CopilotAPITester:
    def __init__(self, base_url="https://esp-builder-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.project_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if method == 'POST' and 'id' in response_data:
                        print(f"   Response ID: {response_data['id']}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text[:200]}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_endpoints(self):
        """Test basic health endpoints"""
        print("\n=== TESTING HEALTH ENDPOINTS ===")
        
        # Test root endpoint
        self.run_test("Root API", "GET", "api/", 200)
        
        # Test health endpoint
        self.run_test("Health Check", "GET", "api/health", 200)

    def test_project_crud(self):
        """Test project CRUD operations"""
        print("\n=== TESTING PROJECT CRUD ===")
        
        # Test list projects (empty initially)
        success, projects = self.run_test("List Projects", "GET", "api/projects", 200)
        if success:
            print(f"   Found {len(projects)} existing projects")
        
        # Test create project
        project_data = {
            "name": f"Test Project {datetime.now().strftime('%H%M%S')}",
            "idea": "Smart plant watering system with soil moisture sensor and WiFi notifications",
            "description": "Automated watering system for indoor plants",
            "target_hardware": "ESP32 DevKit V1"
        }
        
        success, response = self.run_test("Create Project", "POST", "api/projects", 200, project_data)
        if success and 'id' in response:
            self.project_id = response['id']
            print(f"   Created project with ID: {self.project_id}")
        else:
            print("❌ Failed to create project - stopping CRUD tests")
            return False
        
        # Test get specific project
        success, project = self.run_test("Get Project", "GET", f"api/projects/{self.project_id}", 200)
        if success:
            print(f"   Project name: {project.get('name', 'Unknown')}")
            print(f"   Current stage: {project.get('current_stage', 'Unknown')}")
        
        # Test update project
        update_data = {"description": "Updated description for automated plant care"}
        self.run_test("Update Project", "PATCH", f"api/projects/{self.project_id}", 200, update_data)
        
        # Test list projects with filter
        self.run_test("List Active Projects", "GET", "api/projects?status=active", 200)
        
        return True

    def test_stage_management(self):
        """Test stage generation and approval"""
        print("\n=== TESTING STAGE MANAGEMENT ===")
        
        if not self.project_id:
            print("❌ No project ID available - skipping stage tests")
            return False
        
        # Test stage generation (requirements stage)
        generation_data = {
            "project_id": self.project_id,
            "stage": "requirements",
            "user_message": "Focus on low power consumption and easy maintenance"
        }
        
        print("⏳ Generating requirements stage (this may take 10-15 seconds)...")
        success, response = self.run_test("Generate Requirements", "POST", f"api/projects/{self.project_id}/generate", 200, generation_data)
        
        if success and 'content' in response:
            print(f"   Generated content length: {len(response['content'])} characters")
            print(f"   Content preview: {response['content'][:100]}...")
        
        # Test stage approval
        approval_data = {
            "stage": "requirements",
            "approved": True,
            "notes": "Looks good, proceeding to next stage"
        }
        
        success, response = self.run_test("Approve Stage", "POST", f"api/projects/{self.project_id}/stages/requirements/approve", 200, approval_data)
        if success and 'next_stage' in response:
            print(f"   Next stage: {response['next_stage']}")
        
        return True

    def test_hardware_library(self):
        """Test hardware library endpoint"""
        print("\n=== TESTING HARDWARE LIBRARY ===")
        
        success, hardware = self.run_test("Get Hardware Library", "GET", "api/hardware", 200)
        if success:
            categories = list(hardware.keys()) if hardware else []
            print(f"   Hardware categories: {categories}")
            if 'sensors' in hardware:
                print(f"   Available sensors: {len(hardware['sensors'])}")

    def test_shopping_list(self):
        """Test shopping list generation endpoint"""
        print("\n=== TESTING SHOPPING LIST GENERATION ===")
        
        # Test shopping list with valid component IDs
        shopping_data = {
            "component_ids": ["dht22", "ssd1306", "relay", "esp32_devkit"]
        }
        
        success, response = self.run_test("Generate Shopping List", "POST", "api/shopping-list", 200, shopping_data)
        if success:
            print(f"   Components in list: {response.get('component_count', 0)}")
            print(f"   Total estimate: {response.get('total_estimate', 'N/A')}")
            
            # Check if components have shopping links
            components = response.get('components', [])
            if components:
                first_component = components[0]
                has_amazon = 'amazon' in first_component.get('shopping_links', {})
                has_aliexpress = 'aliexpress' in first_component.get('shopping_links', {})
                print(f"   Shopping links available - Amazon: {has_amazon}, AliExpress: {has_aliexpress}")
        
        # Test with empty component list
        empty_data = {"component_ids": []}
        self.run_test("Empty Shopping List", "POST", "api/shopping-list", 200, empty_data)

    def test_project_export(self):
        """Test project export endpoints"""
        print("\n=== TESTING PROJECT EXPORT ===")
        
        if not self.project_id:
            print("❌ No project ID available - skipping export tests")
            return False
        
        # Test markdown export
        success, _ = self.run_test("Export Markdown", "GET", f"api/projects/{self.project_id}/export/markdown", 200)
        if success:
            print("   Markdown export successful")
        
        # Test JSON export
        success, _ = self.run_test("Export JSON", "GET", f"api/projects/{self.project_id}/export/json", 200)
        if success:
            print("   JSON export successful")
        
        return True

    def test_llm_providers(self):
        """Test LLM generation with different providers"""
        print("\n=== TESTING LLM PROVIDERS ===")
        
        if not self.project_id:
            print("❌ No project ID available - skipping LLM provider tests")
            return False
        
        # Test with OpenAI (default/Emergent)
        openai_data = {
            "project_id": self.project_id,
            "stage": "hardware",
            "provider": "openai",
            "model": "gpt-4o"
        }
        
        print("⏳ Testing OpenAI provider (this may take 10-15 seconds)...")
        success, response = self.run_test("OpenAI Provider", "POST", f"api/projects/{self.project_id}/generate", 200, openai_data)
        if success and 'content' in response:
            print(f"   OpenAI generation successful - {len(response['content'])} characters")
        
        # Test with Groq (should fail without API key)
        groq_data = {
            "project_id": self.project_id,
            "stage": "architecture",
            "provider": "groq",
            "model": "llama-3.1-70b-versatile"
        }
        
        success, response = self.run_test("Groq Provider (no key)", "POST", f"api/projects/{self.project_id}/generate", 400, groq_data)
        if not success:
            print("   Groq correctly requires API key")
        
        # Test with OpenRouter (should fail without API key)
        openrouter_data = {
            "project_id": self.project_id,
            "stage": "architecture",
            "provider": "openrouter",
            "model": "anthropic/claude-3.5-sonnet"
        }
        
        success, response = self.run_test("OpenRouter Provider (no key)", "POST", f"api/projects/{self.project_id}/generate", 400, openrouter_data)
        if not success:
            print("   OpenRouter correctly requires API key")
        
        return True

    def test_wiring_diagram(self):
        """Test ASCII wiring diagram generation"""
        print("\n=== TESTING WIRING DIAGRAM GENERATION ===")
        
        # Test wiring diagram with valid components
        wiring_data = {
            "component_ids": ["dht22", "ssd1306", "relay", "esp32_devkit"]
        }
        
        success, response = self.run_test("Generate Wiring Diagram", "POST", "api/wiring-diagram", 200, wiring_data)
        if success:
            diagram = response.get('diagram', '')
            warnings = response.get('warnings', [])
            pin_assignments = response.get('pin_assignments', {})
            components = response.get('components', [])
            
            print(f"   Diagram length: {len(diagram)} characters")
            print(f"   Components: {len(components)}")
            print(f"   Pin assignments: {len(pin_assignments)} components")
            print(f"   Warnings: {len(warnings)}")
            
            # Check for deterministic pin mappings
            if 'GPIO21' in diagram and 'GPIO22' in diagram:
                print("   ✅ I2C pins (GPIO21/22) correctly assigned")
            
            if 'ESP32 WIRING DIAGRAM' in diagram:
                print("   ✅ ASCII diagram header present")
        
        # Test with empty component list
        empty_data = {"component_ids": []}
        success, response = self.run_test("Empty Wiring Diagram", "POST", "api/wiring-diagram", 200, empty_data)
        if success and 'No components selected' in response.get('diagram', ''):
            print("   ✅ Empty component list handled correctly")
        
        # Test with conflicting components (multiple I2C devices)
        conflict_data = {
            "component_ids": ["bme280", "ssd1306", "lcd1602_i2c"]
        }
        success, response = self.run_test("Conflicting Components", "POST", "api/wiring-diagram", 200, conflict_data)
        if success:
            warnings = response.get('warnings', [])
            if any('conflict' in w.lower() for w in warnings):
                print("   ✅ Pin conflicts detected and warned")

    def test_project_templates(self):
        """Test project templates functionality"""
        print("\n=== TESTING PROJECT TEMPLATES ===")
        
        # Test get all templates
        success, templates = self.run_test("Get All Templates", "GET", "api/templates", 200)
        if success:
            print(f"   Available templates: {len(templates)}")
            
            # Check for expected templates
            template_ids = [t.get('id') for t in templates]
            expected_templates = ["temperature_logger", "oled_sensor_display", "relay_controller", 
                                "battery_sensor_node", "motion_alarm", "plant_monitor"]
            
            found_templates = [tid for tid in expected_templates if tid in template_ids]
            print(f"   Expected templates found: {len(found_templates)}/6")
            
            # Check template structure
            if templates:
                first_template = templates[0]
                required_fields = ['id', 'name', 'description', 'difficulty', 'components', 'idea']
                has_all_fields = all(field in first_template for field in required_fields)
                print(f"   Template structure complete: {has_all_fields}")
                
                # Check difficulty levels
                difficulties = set(t.get('difficulty') for t in templates)
                print(f"   Difficulty levels: {sorted(difficulties)}")
        
        # Test get specific template
        if templates:
            template_id = templates[0]['id']
            success, template = self.run_test("Get Specific Template", "GET", f"api/templates/{template_id}", 200)
            if success:
                print(f"   Template '{template.get('name')}' retrieved successfully")
        
        # Test template instantiation
        if templates:
            template_id = templates[0]['id']
            success, project = self.run_test("Instantiate Template", "POST", f"api/templates/{template_id}/instantiate", 200)
            if success and 'id' in project:
                print(f"   Template instantiated as project: {project['id']}")
                # Store for cleanup
                self.template_project_id = project['id']
                
                # Verify project has template data
                if project.get('name') == templates[0].get('name'):
                    print("   ✅ Project created with template name")
                if project.get('idea') == templates[0].get('idea'):
                    print("   ✅ Project created with template idea")
        
        # Test non-existent template
        self.run_test("Non-existent Template", "GET", "api/templates/nonexistent", 404)

    def test_debug_assistant(self):
        """Test debug assistance functionality"""
        print("\n=== TESTING DEBUG ASSISTANT ===")
        
        if not self.project_id:
            print("❌ No project ID available - skipping debug tests")
            return False
        
        # Test compilation error analysis
        compilation_data = {
            "project_id": self.project_id,
            "error_type": "compilation",
            "log_content": """
Arduino: 1.8.19 (Windows 10), Board: "ESP32 Dev Module, Disabled, Default 4MB with spiffs, 240MHz (WiFi/BT), QIO, 80MHz, 4MB (32Kb SPIFFS), None, Core 1, Core 1"

sketch_jan01a:5:1: error: 'WiFi' was not declared in this scope
 WiFi.begin(ssid, password);
 ^~~~
sketch_jan01a:5:1: note: suggested alternative: 'wifi'
 WiFi.begin(ssid, password);
 ^~~~
 wifi

exit status 1
'WiFi' was not declared in this scope
            """,
            "provider": "openai",
            "model": "gpt-4o"
        }
        
        print("⏳ Analyzing compilation error (this may take 10-15 seconds)...")
        success, response = self.run_test("Debug Compilation Error", "POST", "api/debug", 200, compilation_data)
        if success:
            analysis = response.get('analysis', '')
            error_type = response.get('error_type', '')
            print(f"   Analysis length: {len(analysis)} characters")
            print(f"   Error type: {error_type}")
            
            # Check for key debugging elements
            if 'WiFi.h' in analysis or '#include' in analysis:
                print("   ✅ Analysis mentions missing include")
            if 'library' in analysis.lower():
                print("   ✅ Analysis mentions library issue")
        
        # Test runtime error analysis
        runtime_data = {
            "project_id": self.project_id,
            "error_type": "runtime",
            "log_content": """
Guru Meditation Error: Core  1 panic'ed (LoadProhibited). Exception was unhandled.

Core  1 register dump:
PC      : 0x400d1b1c  PS      : 0x00060030  A0      : 0x800d1b3c  A1      : 0x3ffb1f50  
A2      : 0x00000000  A3      : 0x3ffb1f7c  A4      : 0x00000001  A5      : 0x3ffb1f7c  

Backtrace:0x400d1b19:0x3ffb1f50 0x400d1b39:0x3ffb1f70 0x400d62ed:0x3ffb1f90

ELF file SHA256: 0000000000000000

Rebooting...
            """,
            "provider": "openai"
        }
        
        print("⏳ Analyzing runtime error (this may take 10-15 seconds)...")
        success, response = self.run_test("Debug Runtime Error", "POST", "api/debug", 200, runtime_data)
        if success:
            analysis = response.get('analysis', '')
            if 'null pointer' in analysis.lower() or 'memory' in analysis.lower():
                print("   ✅ Analysis identifies memory/pointer issue")
        
        # Test hardware issue analysis
        hardware_data = {
            "project_id": self.project_id,
            "error_type": "hardware",
            "log_content": "DHT22 sensor always returns NaN values. Wiring: VCC to 3.3V, GND to GND, DATA to GPIO4 with 10K pullup resistor. Serial output shows: Temperature: nan°C, Humidity: nan%",
            "provider": "openai"
        }
        
        print("⏳ Analyzing hardware issue (this may take 10-15 seconds)...")
        success, response = self.run_test("Debug Hardware Issue", "POST", "api/debug", 200, hardware_data)
        if success:
            analysis = response.get('analysis', '')
            if 'wiring' in analysis.lower() or 'power' in analysis.lower():
                print("   ✅ Analysis addresses hardware/wiring")
        
        # Test power issue analysis
        power_data = {
            "project_id": self.project_id,
            "error_type": "power",
            "log_content": "ESP32 keeps rebooting when relay activates. Serial shows: Brownout detector was triggered. Using USB power supply.",
            "provider": "openai"
        }
        
        print("⏳ Analyzing power issue (this may take 10-15 seconds)...")
        success, response = self.run_test("Debug Power Issue", "POST", "api/debug", 200, power_data)
        if success:
            analysis = response.get('analysis', '')
            if 'power supply' in analysis.lower() or 'current' in analysis.lower():
                print("   ✅ Analysis addresses power supply")
        
        return True

    def test_cleanup(self):
        """Clean up test data"""
        print("\n=== CLEANUP ===")
        
        if self.project_id:
            success, _ = self.run_test("Delete Test Project", "DELETE", f"api/projects/{self.project_id}", 200)
            if success:
                print(f"   Cleaned up project {self.project_id}")
        
        # Clean up template project if created
        if hasattr(self, 'template_project_id') and self.template_project_id:
            success, _ = self.run_test("Delete Template Project", "DELETE", f"api/projects/{self.template_project_id}", 200)
            if success:
                print(f"   Cleaned up template project {self.template_project_id}")

def main():
    print("🚀 Starting ESP32 IoT Copilot API Tests - Phase 3")
    print("=" * 50)
    
    tester = ESP32CopilotAPITester()
    
    # Run all tests
    tester.test_health_endpoints()
    
    if tester.test_project_crud():
        tester.test_stage_management()
        tester.test_llm_providers()
        tester.test_project_export()
        tester.test_debug_assistant()
    
    tester.test_hardware_library()
    tester.test_shopping_list()
    tester.test_wiring_diagram()
    tester.test_project_templates()
    tester.test_cleanup()
    
    # Print results
    print(f"\n📊 TEST RESULTS")
    print("=" * 50)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())