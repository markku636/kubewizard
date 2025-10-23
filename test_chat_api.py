"""
測試 Chat API

正確的請求格式：
{
  "message": "你的問題",     ← 這是你想問的問題
  "user_id": "用戶ID"        ← 這是用戶的識別碼
}

錯誤的格式（不要這樣做）：
{
  "message": "用戶ID",       ← 錯！
  "user_id": "你的問題"      ← 錯！
}
"""

import requests
import json

API_URL = "http://localhost:8000/api/chat"

def test_chat_api():
    """測試聊天 API"""
    
    print("=" * 70)
    print("⚠️  重要：請確認在 Swagger UI 中使用正確的格式")
    print("=" * 70)
    print("正確格式：")
    print(json.dumps({
        "message": "我想查目前k8s有幾個節點",
        "user_id": "mark"
    }, indent=2, ensure_ascii=False))
    print("\n" + "=" * 70)
    
    test_cases = [
        {
            "message": "請列出所有 nodes",
            "user_id": "test_user_1"
        },
        {
            "message": "有哪些 namespace?",
            "user_id": "test_user_1"
        },
        {
            "message": "default namespace 有哪些 pods?",
            "user_id": "test_user_1"
        },
    ]
    
    print("=" * 70)
    print("測試 Chat API")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n測試 {i}: {test_case['message']}")
        print("-" * 70)
        
        try:
            response = requests.post(
                API_URL,
                json=test_case,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功")
                print(f"User ID: {result['user_id']}")
                print(f"Session ID: {result['session_id']}")
                print(f"回應: {result['reply'][:200]}...")
            else:
                print(f"❌ 失敗: HTTP {response.status_code}")
                print(f"錯誤: {response.text}")
                
        except Exception as e:
            print(f"❌ 錯誤: {e}")
    
    print("\n" + "=" * 70)
    print("測試完成")
    print("=" * 70)

if __name__ == "__main__":
    test_chat_api()
