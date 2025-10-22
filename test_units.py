#!/usr/bin/env python3
"""
測試 KubeWizard API 功能
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_configuration():
    """測試配置"""
    print("\n1. 測試配置...")
    try:
        from kubewizard_linebot.config import get_settings, validate_required_settings
        settings = get_settings()
        validate_required_settings()
        print(f"   ✅ 配置正常")
        print(f"   - AI Model: {settings.ai_model}")
        print(f"   - Redis URL: {settings.redis_url}")
        return True
    except Exception as e:
        print(f"   ❌ 配置錯誤: {e}")
        return False


def test_kube_agent():
    """測試 KubeAgent"""
    print("\n2. 測試 KubeAgent...")
    try:
        from agent import KubeAgent
        agent = KubeAgent()
        print(f"   ✅ KubeAgent 創建成功")
        
        # 簡單測試
        result = agent.invoke("你好")
        response = result.get("output", "")
        print(f"   - 測試回應: {response[:100]}...")
        return True
    except Exception as e:
        print(f"   ❌ KubeAgent 錯誤: {e}")
        return False


def test_memory_service():
    """測試記憶服務"""
    print("\n3. 測試記憶服務...")
    try:
        from kubewizard_linebot.memory import MemoryService
        from kubewizard_linebot.config import get_settings
        
        settings = get_settings()
        memory = MemoryService(redis_url=settings.redis_url)
        
        # 測試添加和讀取
        test_user = "test_user_123"
        memory.add_message(test_user, "user", "測試消息")
        memory.add_message(test_user, "assistant", "測試回覆")
        
        history = memory.get_history(test_user)
        print(f"   ✅ 記憶服務正常")
        print(f"   - 儲存的消息數: {len(history)}")
        
        # 清理
        memory.clear_history(test_user)
        return True
    except Exception as e:
        print(f"   ❌ 記憶服務錯誤: {e}")
        return False


def test_api_models():
    """測試 API 模型"""
    print("\n4. 測試 API 模型...")
    try:
        from kubewizard_linebot.models import ChatRequest, ChatResponse, HealthResponse
        from datetime import datetime
        
        # 測試 ChatRequest
        req = ChatRequest(message="test", user_id="user123")
        print(f"   ✅ ChatRequest 正常")
        
        # 測試 ChatResponse
        resp = ChatResponse(
            reply="test reply",
            session_id="session123",
            user_id="user123",
            timestamp=datetime.now().isoformat()
        )
        print(f"   ✅ ChatResponse 正常")
        
        # 測試 HealthResponse
        health = HealthResponse(
            status="healthy",
            services={"test": "ok"},
            timestamp=datetime.now().isoformat()
        )
        print(f"   ✅ HealthResponse 正常")
        return True
    except Exception as e:
        print(f"   ❌ API 模型錯誤: {e}")
        return False


def main():
    """主測試函數"""
    print("=" * 60)
    print("🧪 KubeWizard API 功能測試")
    print("=" * 60)
    
    results = []
    results.append(("配置", test_configuration()))
    results.append(("KubeAgent", test_kube_agent()))
    results.append(("記憶服務", test_memory_service()))
    results.append(("API 模型", test_api_models()))
    
    print("\n" + "=" * 60)
    print("📊 測試結果")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{name:15} {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n總計: {passed}/{total} 測試通過")
    
    if passed == total:
        print("\n🎉 所有測試通過！")
        return 0
    else:
        print("\n⚠️  部分測試失敗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
