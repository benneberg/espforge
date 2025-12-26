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

    def test_cleanup(self):
        """Clean up test data"""
        print("\n=== CLEANUP ===")
        
        if self.project_id:
            success, _ = self.run_test("Delete Test Project", "DELETE", f"api/projects/{self.project_id}", 200)
            if success:
                print(f"   Cleaned up project {self.project_id}")

def main():
    print("🚀 Starting ESP32 IoT Copilot API Tests")
    print("=" * 50)
    
    tester = ESP32CopilotAPITester()
    
    # Run all tests
    tester.test_health_endpoints()
    
    if tester.test_project_crud():
        tester.test_stage_management()
    
    tester.test_hardware_library()
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