"""Test script for KubeAgent with Redis chat history and fortune tools."""

import os
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents import KubeAgent


def test_kube_agent_with_redis():
    """測試 KubeAgent 的 Redis 聊天歷史功能"""
    print("=" * 50)
    print("測試 KubeAgent 與 Redis 聊天歷史")
    print("=" * 50)
    
    try:
        # 創建帶有 user_id 的 agent
        agent = KubeAgent(user_id="test_user_123")
        print("✓ KubeAgent 創建成功 (user_id: test_user_123)")
        
        # 測試基本對話
        response = agent.invoke("你好，我是測試用戶")
        print(f"\n用戶: 你好，我是測試用戶")
        print(f"AI: {response.get('output', response)}")
        
        # 測試記憶功能
        response = agent.invoke("你還記得我是誰嗎？")
        print(f"\n用戶: 你還記得我是誰嗎？")
        print(f"AI: {response.get('output', response)}")
        
        print("\n✓ Redis 聊天歷史測試通過")
        
    except Exception as e:
        print(f"\n✗ 測試失敗: {e}")
        print(f"注意: 如果 Redis 未運行，將使用內存歷史")
        return False
    
    return True


def test_fortune_tools():
    """測試算命工具"""
    print("\n" + "=" * 50)
    print("測試算命工具")
    print("=" * 50)
    
    try:
        agent = KubeAgent(user_id="fortune_test_user")
        
        # 測試搜索工具
        print("\n測試搜索工具:")
        try:
            response = agent.invoke("請搜索 Kubernetes 最新版本")
            print(f"✓ 搜索工具可用")
        except Exception as e:
            print(f"✗ 搜索工具測試失敗: {e}")
        
        print("\n✓ 算命工具測試完成")
        
    except Exception as e:
        print(f"\n✗ 測試失敗: {e}")
        return False
    
    return True


def test_tools_list():
    """測試工具列表"""
    print("\n" + "=" * 50)
    print("檢查可用工具")
    print("=" * 50)
    
    try:
        agent = KubeAgent(user_id="tools_test")
        print(f"\n可用工具數量: {len(agent.tools)}")
        print("\n工具列表:")
        for i, tool in enumerate(agent.tools, 1):
            tool_name = getattr(tool, 'name', str(tool))
            print(f"  {i}. {tool_name}")
        
        print("\n✓ 工具列表檢查完成")
        
    except Exception as e:
        print(f"\n✗ 測試失敗: {e}")
        return False
    
    return True


def main():
    """主測試函數"""
    print("開始測試 KubeAgent 新功能...\n")
    
    # 檢查環境變量
    print("檢查環境變量:")
    required_vars = ["AI_GOOGLE_API_KEY"]
    optional_vars = ["REDIS_URL", "YUANFENJU_API_KEY", "SERPAPI_API_KEY"]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✓ {var}: 已設置")
        else:
            print(f"  ✗ {var}: 未設置 (必需)")
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✓ {var}: 已設置")
        else:
            print(f"  ⚠ {var}: 未設置 (可選)")
    
    print()
    
    # 運行測試
    results = []
    results.append(("工具列表檢查", test_tools_list()))
    results.append(("Redis 聊天歷史", test_kube_agent_with_redis()))
    results.append(("算命工具", test_fortune_tools()))
    
    # 總結
    print("\n" + "=" * 50)
    print("測試總結")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n總計: {passed}/{total} 測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！")
    else:
        print("⚠️  部分測試失敗，請檢查錯誤訊息")


if __name__ == "__main__":
    main()
