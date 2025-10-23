"""
測試 KubeAgent 是否能真正查詢 K8s
"""

import os
import dotenv
import logging

# 載入環境變數
dotenv.load_dotenv()

# 設定日誌
logging.basicConfig(level=logging.INFO)

def test_kube_agent():
    """測試 KubeAgent 查詢功能"""
    from agents import KubeAgent
    
    # 檢查 API Key
    if not os.getenv("AI_GOOGLE_API_KEY"):
        print("❌ 請設定 AI_GOOGLE_API_KEY 環境變數")
        return False
    
    print("=" * 70)
    print("測試 KubeAgent 查詢 Kubernetes")
    print("=" * 70)
    
    # 創建 agent
    print("\n1. 創建 KubeAgent...")
    agent = KubeAgent(user_id="test_query_user", debug_level=2)
    print(f"✅ Agent 創建成功，工具數量: {len(agent.tools)}")
    
    # 測試查詢命令
    test_queries = [
        "請使用 kubectl 列出所有 nodes",
        "請告訴我有哪些 namespace",
        "檢查 default namespace 有哪些 pods",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. 測試查詢: {query}")
        print("-" * 70)
        try:
            result = agent.invoke(query)
            print(f"✅ 查詢成功")
            print(f"回應: {result.get('output', result)[:200]}...")
        except Exception as e:
            print(f"❌ 查詢失敗: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("測試完成")
    print("=" * 70)

if __name__ == "__main__":
    test_kube_agent()
