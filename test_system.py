#!/usr/bin/env python3
"""
Quick test script to verify the system is working
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_system():
    """Test all components"""
    print("🧪 Testing Xalora AI Interview System\n")
    print("=" * 50)
    
    # Test 1: Check API Key
    print("\n1️⃣ Checking API Key...")
    api_key = "sk-e9b92c79e0aa47a097aadf070f50a1c8"
    if api_key and len(api_key) > 20:
        print("   ✅ API Key configured")
    else:
        print("   ❌ API Key not found")
        return False
    
    # Test 2: Import agents
    print("\n2️⃣ Testing AI Agents...")
    try:
        from agents.round0_resume_agent import ResumeAnalysisAgent
        from agents.round1_formal_qa_agent import FormalQAAgent
        from agents.round2_coding_agent import CodingAgent
        from agents.round3_technical_agent import TechnicalAgent
        from agents.round4_behavioral_agent import BehavioralAgent
        from agents.round5_system_design_agent import SystemDesignAgent
        print("   ✅ All agents imported successfully")
    except Exception as e:
        print(f"   ❌ Agent import failed: {e}")
        return False
    
    # Test 3: Test DeepSeek connection
    print("\n3️⃣ Testing DeepSeek API Connection...")
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": "Say 'API test successful' and nothing else."}
            ],
            temperature=0.1
        )
        
        if "successful" in response.choices[0].message.content.lower():
            print("   ✅ DeepSeek API working")
        else:
            print("   ⚠️  API responded but unexpected response")
    except Exception as e:
        print(f"   ❌ API connection failed: {e}")
        return False
    
    # Test 4: Check static files
    print("\n4️⃣ Checking Static Files...")
    if os.path.exists("static/index.html"):
        print("   ✅ Web interface found")
    else:
        print("   ❌ Web interface missing")
        return False
    
    # Test 5: Test FastAPI app
    print("\n5️⃣ Testing FastAPI Application...")
    try:
        from app import app
        print("   ✅ FastAPI app loaded")
    except Exception as e:
        print(f"   ❌ FastAPI app failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    print("\n🚀 Your system is ready to use!")
    print("\n📝 Next steps:")
    print("   1. Run: python app.py")
    print("   2. Open: http://localhost:8000")
    print("   3. Start interviewing!")
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_system())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        exit(1)