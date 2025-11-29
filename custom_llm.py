# custom_llm.py
# Custom LLM Engine - Gemini Only

import os
import requests
import json
import time
from typing import Dict, Any, Optional
import google.generativeai as genai
from datetime import datetime

class CustomLLMEngine:
    def __init__(self):
        """Initialize Custom LLM Engine with Gemini only"""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_model = "gemini-1.5-flash"  # Using the latest Gemini model
        
        # Configure Gemini
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model_instance = genai.GenerativeModel(self.gemini_model)
            print("✅ Gemini API configured successfully")
        else:
            print("⚠️ Warning: GEMINI_API_KEY not found in environment variables")
            self.gemini_model_instance = None
        
        # Performance tracking
        self.request_count = 0
        self.total_response_time = 0
        self.error_count = 0

    def _call_gemini_api(self, prompt: str, max_tokens: int = 2048) -> Optional[str]:
        """Call Gemini API directly"""
        if not self.gemini_model_instance:
            print("❌ Gemini API not configured")
            return None
        
        try:
            start_time = time.time()
            
            # Generate content using Gemini
            response = self.gemini_model_instance.generate_content(prompt)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Update performance metrics
            self.request_count += 1
            self.total_response_time += response_time
            
            if response.text:
                print(f"✅ Gemini API response generated in {response_time:.2f}s")
                return response.text
            else:
                print("❌ Empty response from Gemini API")
                return None
                
        except Exception as e:
            self.error_count += 1
            print(f"❌ Error calling Gemini API: {e}")
            return None

    def generate_response(self, prompt: str, max_tokens: int = 2048) -> str:
        """Generate response using Gemini only"""
        print(f"🤖 Using Gemini API for response generation")
        
        response = self._call_gemini_api(prompt, max_tokens)
        if response:
            return response
        else:
            return "Error: Unable to generate response. Gemini API is unavailable."

    def test_model(self) -> Dict[str, Any]:
        """Test the Gemini model with a simple prompt"""
        test_prompt = "Hello, how are you? Please respond briefly."
        
        start_time = time.time()
        response = self.generate_response(test_prompt, max_tokens=100)
        end_time = time.time()
        
        success = "Error:" not in response
        
        return {
            "success": success,
            "response": response,
            "response_time": end_time - start_time,
            "model_used": "gemini",
            "gemini_available": self.gemini_model_instance is not None,
            "api_key_configured": self.gemini_api_key is not None
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        avg_response_time = self.total_response_time / self.request_count if self.request_count > 0 else 0
        error_rate = self.error_count / self.request_count if self.request_count > 0 else 0
        
        return {
            "total_requests": self.request_count,
            "average_response_time": avg_response_time,
            "error_count": self.error_count,
            "error_rate": error_rate,
            "model": "gemini",
            "model_name": self.gemini_model
        }

    def reset_stats(self):
        """Reset performance statistics"""
        self.request_count = 0
        self.total_response_time = 0
        self.error_count = 0
        print("✅ Performance statistics reset")

# Test the Gemini-only setup
if __name__ == "__main__":
    print("🧪 Testing Gemini-Only LLM Setup...")
    
    llm_engine = CustomLLMEngine()
    
    # Test basic functionality
    test_result = llm_engine.test_model()
    print(f"\n✅ Test Results:")
    print(f"   Success: {test_result['success']}")
    print(f"   Model Used: {test_result['model_used']}")
    print(f"   Response Time: {test_result['response_time']:.2f}s")
    print(f"   Gemini Available: {test_result['gemini_available']}")
    print(f"   API Key Configured: {test_result['api_key_configured']}")
    
    if test_result['success']:
        print(f"   Response: {test_result['response'][:100]}...")
    
    # Test performance stats
    stats = llm_engine.get_performance_stats()
    print(f"\n📊 Performance Stats:")
    print(f"   Total Requests: {stats['total_requests']}")
    print(f"   Average Response Time: {stats['average_response_time']:.2f}s")
    print(f"   Error Rate: {stats['error_rate']:.2%}")
    
    print(f"\n✅ Gemini-Only Setup: COMPLETE")
    print(f"🚀 Using Gemini as the primary and only LLM!")
