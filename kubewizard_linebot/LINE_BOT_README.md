# LINE Bot Webhook 整合說明

## 概述

KubeWizard 現在支援 LINE Bot webhook 功能，可以直接通過 LINE 聊天來管理 Kubernetes 叢集。

## 功能特點

✅ 完整整合到現有 FastAPI 服務中
✅ 支援 LINE Bot webhook callback
✅ 自動儲存對話歷史到 Redis
✅ 使用 KubeAgent 處理 Kubernetes 相關查詢
✅ 錯誤處理和日誌記錄
❌ 不包含音訊功能（已移除）

## 配置步驟

### 1. 設定環境變數

在 `.env` 文件中添加你的 LINE Bot 憑證：

```bash
# LINE Bot Configuration
LINE_CHANNEL_SECRET=你的_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=你的_access_token
```

### 2. 啟動服務

```bash
# 使用 Python 直接啟動
python kubewizard_linebot/api.py

# 或使用 uvicorn
uvicorn kubewizard_linebot.api:app --host 0.0.0.0 --port 8000
```

### 3. 設定 LINE Webhook URL

在 LINE Developers Console 中，將 Webhook URL 設定為：

```
https://你的域名/linebot/callback
```

## API 端點

### Webhook Callback
- **URL**: `/linebot/callback`
- **方法**: `POST`
- **說明**: 接收來自 LINE 平台的 webhook 事件

### 測試端點
- **URL**: `/linebot/test`
- **方法**: `GET`
- **說明**: 測試 LINE Bot 配置是否正確

### 健康檢查
- **URL**: `/health`
- **方法**: `GET`
- **說明**: 檢查所有服務狀態（包括 LINE Bot）

## 使用方式

1. 將你的 LINE Bot 加入好友
2. 直接在 LINE 中發送訊息
3. Bot 會使用 KubeAgent 處理你的請求並回覆

## 支援的功能

LINE Bot 可以執行所有 KubeAgent 支援的功能：

- 查詢 Pod 狀態
- 查看 Deployment
- 檢查服務狀態
- 故障排除
- 部署管理
- 等等...

## 測試配置

使用以下命令測試 LINE Bot 配置：

```bash
curl http://localhost:8000/linebot/test
```

正確配置的回應範例：

```json
{
  "status": "ok",
  "bot_info": {
    "display_name": "KubeWizard Bot",
    "user_id": "U1234567890",
    "picture_url": "https://..."
  },
  "config": {
    "channel_secret": "configured",
    "channel_access_token": "configured"
  }
}
```

## 架構說明

```
FastAPI Application
├── /api/chat          - REST API 聊天端點
├── /api/memory        - 記憶體管理端點
└── /linebot/callback  - LINE Bot Webhook ✨ 新增
    └── 使用相同的 KubeAgent 和 MemoryService
```

## 日誌和除錯

應用程式會記錄所有 LINE webhook 事件和錯誤：

```python
# 檢查日誌
LOG_LEVEL=DEBUG python kubewizard_linebot/api.py
```

## 安全性考慮

- ✅ Webhook 簽名驗證
- ✅ 環境變數儲存敏感資訊
- ✅ 錯誤訊息不洩露系統資訊

## 故障排除

### 問題：收到 400 Invalid Signature 錯誤

**解決方案**：
- 確認 `LINE_CHANNEL_SECRET` 配置正確
- 檢查 LINE Developers Console 中的 Channel Secret

### 問題：Bot 沒有回應

**解決方案**：
1. 檢查服務是否正常運行：`curl http://localhost:8000/health`
2. 檢查日誌檔案
3. 確認 Webhook URL 可以從外部訪問
4. 使用 `/linebot/test` 端點測試配置

### 問題：Bot 回應錯誤訊息

**解決方案**：
- 檢查 `AI_GOOGLE_API_KEY` 是否配置正確
- 確認 KubeAgent 可以正常運作
- 檢查 Kubernetes 配置是否正確

## 與原始 Flask 版本的差異

| 功能 | Flask 版本 | FastAPI 版本 |
|------|-----------|-------------|
| 框架 | Flask | FastAPI |
| 音訊支援 | ✅ | ❌ (已移除) |
| 異步支援 | 部分 | 完整 |
| API 文檔 | ❌ | ✅ (Swagger UI) |
| 整合性 | 獨立服務 | 整合到主服務 |
| 記憶體管理 | ❌ | ✅ (Redis) |
| 健康檢查 | ❌ | ✅ |

## 開發和貢獻

如需添加新功能或修改，請編輯：
- `kubewizard_linebot/routers/linebot_webhook.py` - Webhook 處理邏輯
- `kubewizard_linebot/config.py` - 配置設定
- `kubewizard_linebot/api.py` - 主應用程式

## 相關資源

- [LINE Messaging API 文檔](https://developers.line.biz/en/docs/messaging-api/)
- [FastAPI 文檔](https://fastapi.tiangolo.com/)
- [KubeWizard 主要文檔](../README.md)
