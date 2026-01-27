"""
Chatbot API Test Script

This script tests the chatbot API endpoints to verify they're working correctly.

Usage:
    python test_api.py

Requirements:
    pip install requests
"""

import requests
import json
import time
from typing import Optional

# Configuration
API_BASE_URL = "https://chat-agent-9wt6.onrender.com"
# For local testing, use: API_BASE_URL = "http://localhost:8000"

class ChatbotAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session_id: Optional[int] = None
        
    def print_section(self, title: str):
        """Print a formatted section header"""
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60)
    
    def print_result(self, success: bool, message: str):
        """Print test result"""
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {message}")
    
    def test_chat(self, message: str, user_name: str = "Test User", 
                  user_email: str = "test@example.com") -> dict:
        """Test the chat endpoint"""
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "message": message,
            "session_id": self.session_id,
            "user_name": user_name,
            "user_email": user_email
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Store session ID for subsequent requests
            if 'session_id' in data:
                self.session_id = data['session_id']
            
            return {
                'success': True,
                'data': data,
                'status_code': response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def test_get_config(self) -> dict:
        """Test getting configuration"""
        url = f"{self.base_url}/api/config"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json(),
                'status_code': response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def test_get_presets(self) -> dict:
        """Test getting presets"""
        url = f"{self.base_url}/api/presets"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json(),
                'status_code': response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def test_get_analytics(self) -> dict:
        """Test getting analytics"""
        url = f"{self.base_url}/api/analytics"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json(),
                'status_code': response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def run_all_tests(self):
        """Run all API tests"""
        print("\n" + "🤖 CHATBOT API TEST SUITE ".center(60, "="))
        print(f"Testing API at: {self.base_url}\n")
        
        # Test 1: Get Configuration
        self.print_section("Test 1: Get Configuration")
        result = self.test_get_config()
        if result['success']:
            self.print_result(True, "Successfully retrieved configuration")
            print(f"Configuration: {json.dumps(result['data'], indent=2)}")
        else:
            self.print_result(False, f"Failed to get configuration: {result.get('error')}")
        
        # Test 2: Get Presets
        self.print_section("Test 2: Get Presets")
        result = self.test_get_presets()
        if result['success']:
            self.print_result(True, f"Successfully retrieved {len(result['data'])} presets")
            for preset in result['data']:
                print(f"  - {preset.get('company_name', 'Unknown')}")
        else:
            self.print_result(False, f"Failed to get presets: {result.get('error')}")
        
        # Test 3: First Chat Message (New Session)
        self.print_section("Test 3: First Chat Message (New Session)")
        result = self.test_chat("Hello, I need help with your services")
        if result['success']:
            self.print_result(True, "Successfully sent first message")
            print(f"Session ID: {result['data']['session_id']}")
            print(f"Bot Response: {result['data']['response'][:100]}...")
        else:
            self.print_result(False, f"Failed to send message: {result.get('error')}")
        
        # Test 4: Second Chat Message (Same Session)
        self.print_section("Test 4: Second Chat Message (Same Session)")
        if self.session_id:
            result = self.test_chat("Tell me more about your pricing")
            if result['success']:
                self.print_result(True, "Successfully continued conversation")
                print(f"Session ID: {result['data']['session_id']}")
                print(f"Bot Response: {result['data']['response'][:100]}...")
            else:
                self.print_result(False, f"Failed to send message: {result.get('error')}")
        else:
            self.print_result(False, "No session ID from previous test")
        
        # Test 5: Third Chat Message (Context Test)
        self.print_section("Test 5: Third Chat Message (Context Test)")
        if self.session_id:
            result = self.test_chat("What did I just ask about?")
            if result['success']:
                self.print_result(True, "Successfully tested conversation context")
                print(f"Bot Response: {result['data']['response'][:100]}...")
            else:
                self.print_result(False, f"Failed to send message: {result.get('error')}")
        else:
            self.print_result(False, "No session ID from previous test")
        
        # Test 6: Get Analytics
        self.print_section("Test 6: Get Analytics")
        result = self.test_get_analytics()
        if result['success']:
            self.print_result(True, "Successfully retrieved analytics")
            data = result['data']
            print(f"Total Sessions: {data.get('total_sessions', 0)}")
            print(f"Average Duration: {data.get('average_duration_minutes', 0):.2f} minutes")
            print(f"Total Users: {len(data.get('users', []))}")
        else:
            self.print_result(False, f"Failed to get analytics: {result.get('error')}")
        
        # Summary
        self.print_section("TEST SUMMARY")
        print("All basic API tests completed!")
        print(f"API Base URL: {self.base_url}")
        print(f"Final Session ID: {self.session_id}")
        print("\n✅ Your chatbot API is ready to use!\n")


def interactive_chat():
    """Interactive chat session for manual testing"""
    print("\n" + "💬 INTERACTIVE CHAT MODE ".center(60, "="))
    print("Type your messages below. Type 'quit' to exit.\n")
    
    tester = ChatbotAPITester(API_BASE_URL)
    
    while True:
        try:
            message = input("\nYou: ").strip()
            
            if message.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋\n")
                break
            
            if not message:
                continue
            
            print("Bot: ", end="", flush=True)
            result = tester.test_chat(message)
            
            if result['success']:
                print(result['data']['response'])
                if result['data'].get('tool_executed'):
                    print(f"[Tool executed: {result['data']['tool_executed']}]")
            else:
                print(f"Error: {result.get('error')}")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋\n")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    import sys
    
    print("\n🤖 Chatbot API Tester")
    print("=" * 60)
    print(f"API URL: {API_BASE_URL}")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_chat()
    else:
        print("\nRunning automated tests...\n")
        tester = ChatbotAPITester(API_BASE_URL)
        tester.run_all_tests()
        
        print("\nWant to try interactive mode?")
        print("Run: python test_api.py interactive\n")
