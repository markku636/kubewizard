#!/usr/bin/env python3
"""
測試 KubeWizard LINE Bot API

這個腳本會測試主要的 API 端點功能
"""

import asyncio
import aiohttp
import json


async def test_api():
    """測試 API 端點"""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("🧪 Testing KubeWizard LINE Bot API...")
        print("=" * 50)
        
        # Test root endpoint
        print("\n1. Testing root endpoint...")
        try:
            async with session.get(f"{base_url}/") as response:
                data = await response.json()
                print(f"✅ Status: {response.status}")
                print(f"📝 Service: {data.get('name')}")
                print(f"🔢 Version: {data.get('version')}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test health check
        print("\n2. Testing health check...")
        try:
            async with session.get(f"{base_url}/health") as response:
                data = await response.json()
                print(f"✅ Status: {response.status}")
                print(f"🏥 Health: {data.get('status')}")
                print("🔧 Services:")
                for service, status in data.get('services', {}).items():
                    emoji = "✅" if status in ["healthy", "configured"] else "⚠️" if status in ["degraded", "unavailable"] else "❌"
                    print(f"   {emoji} {service}: {status}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test chat endpoint
        print("\n3. Testing chat endpoint...")
        try:
            chat_data = {
                "message": "你好，請問你可以幫我什麼？",
                "user_id": "test_user_123"
            }
            async with session.post(
                f"{base_url}/api/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                data = await response.json()
                print(f"✅ Status: {response.status}")
                print(f"💬 Reply: {data.get('reply')[:100]}...")
                print(f"🆔 Session ID: {data.get('session_id')}")
                print(f"🔊 Audio URL: {data.get('audio_url', 'None')}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test memory endpoint
        print("\n4. Testing memory endpoint...")
        try:
            async with session.get(f"{base_url}/api/memory/test_user_123") as response:
                data = await response.json()
                print(f"✅ Status: {response.status}")
                print(f"💾 Message count: {data.get('message_count')}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 API testing completed!")
        print("\n📖 To explore all endpoints, visit: http://localhost:8000/docs")


if __name__ == "__main__":
    print("請確保 API 服務正在運行 (python linebot_server.py)")
    print("按 Enter 開始測試...")
    input()
    
    asyncio.run(test_api())