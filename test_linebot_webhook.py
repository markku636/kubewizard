"""
LINE Bot Webhook 測試腳本

此腳本可用於測試 LINE Bot webhook 功能
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8000"

def test_health_check():
    """測試健康檢查端點"""
    print("🔍 測試健康檢查...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_linebot_config():
    """測試 LINE Bot 配置"""
    print("🔍 測試 LINE Bot 配置...")
    response = requests.get(f"{BASE_URL}/linebot/test")
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_chat_api(message: str, user_id: str = "test_user"):
    """測試聊天 API"""
    print(f"💬 測試聊天 API - 訊息: {message}")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": message, "user_id": user_id}
    )
    print(f"狀態碼: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"回應: {result.get('reply', 'No reply')}")
    else:
        print(f"錯誤: {response.text}")
    print()

def simulate_linebot_webhook(message: str, user_id: str = "U1234567890"):
    """
    模擬 LINE Bot webhook 請求
    注意：這個測試需要正確的 LINE 簽名，實際上會失敗
    這裡只是展示如何構造請求
    """
    print(f"📱 模擬 LINE Bot Webhook - 訊息: {message}")
    
    # 構造 LINE webhook payload
    webhook_payload = {
        "destination": "U1234567890",
        "events": [
            {
                "type": "message",
                "message": {
                    "type": "text",
                    "id": "123456789",
                    "text": message
                },
                "timestamp": 1234567890123,
                "source": {
                    "type": "user",
                    "userId": user_id
                },
                "replyToken": "test_reply_token"
            }
        ]
    }
    
    print("⚠️  注意：這個請求會失敗，因為缺少有效的 LINE 簽名")
    print(f"Payload: {json.dumps(webhook_payload, indent=2, ensure_ascii=False)}")
    print()

def main():
    """主測試函數"""
    print("=" * 60)
    print("KubeWizard LINE Bot Webhook 測試")
    print("=" * 60)
    print()
    
    try:
        # 1. 測試健康檢查
        test_health_check()
        
        # 2. 測試 LINE Bot 配置
        test_linebot_config()
        
        # 3. 測試聊天 API（這個會正常工作）
        test_chat_api("list pods in default namespace")
        
        # 4. 展示如何構造 LINE webhook 請求（僅供參考）
        simulate_linebot_webhook("show me all deployments")
        
        print("✅ 測試完成！")
        print()
        print("📝 說明：")
        print("- 健康檢查和聊天 API 應該正常工作")
        print("- LINE Bot webhook 需要從 LINE 平台發送才能正常工作")
        print("- 請在 LINE Developers Console 中設定 webhook URL")
        
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到服務器")
        print(f"請確保服務正在運行: {BASE_URL}")
        print("啟動命令: python kubewizard_linebot/api.py")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    main()
