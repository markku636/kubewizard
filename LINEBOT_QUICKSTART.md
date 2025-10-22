# LINE Bot 快速啟動指南

## 🚀 5 分鐘快速設定

### 步驟 1: 獲取 LINE Bot 憑證

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 建立新的 Provider（如果還沒有）
3. 建立 Messaging API channel
4. 在 "Basic settings" 頁面複製 **Channel secret**
5. 在 "Messaging API" 頁面複製 **Channel access token**

### 步驟 2: 配置環境變數

編輯 `.env` 文件（或複製 `.env.example` 並重命名）：

```bash
# 必需 - Google AI
AI_GOOGLE_API_KEY=你的_google_api_key

# 必需 - LINE Bot
LINE_CHANNEL_SECRET=你的_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=你的_access_token

# 可選 - Redis（預設使用 localhost）
REDIS_URL=redis://localhost:6379/0
```

### 步驟 3: 安裝依賴

```bash
pip install -r requirements.txt
```

### 步驟 4: 啟動服務

```bash
# 方式 A: 直接啟動
python kubewizard_linebot/api.py

# 方式 B: 使用 uvicorn
uvicorn kubewizard_linebot.api:app --host 0.0.0.0 --port 8000

# 方式 C: 使用 Docker
docker-compose up -d
```

服務啟動後會顯示：
```
🚀 Starting KubeWizard LINE Bot API...
📍 API will be available at: http://localhost:8000
📖 API documentation: http://localhost:8000/docs
💚 Health check: http://localhost:8000/health
```

### 步驟 5: 測試配置

開啟新的終端視窗，執行：

```bash
# 測試健康檢查
curl http://localhost:8000/health

# 測試 LINE Bot 配置
curl http://localhost:8000/linebot/test
```

預期看到：
```json
{
  "status": "ok",
  "bot_info": {
    "display_name": "你的 Bot 名稱",
    "user_id": "U...",
    ...
  }
}
```

### 步驟 6: 設定 Webhook URL

#### 本地開發（使用 ngrok）

```bash
# 安裝 ngrok（如果還沒有）
# Windows: choco install ngrok
# Mac: brew install ngrok

# 啟動 ngrok
ngrok http 8000
```

ngrok 會顯示一個 HTTPS URL，例如：
```
Forwarding: https://abc123.ngrok.io -> http://localhost:8000
```

#### 設定 LINE Webhook

1. 回到 LINE Developers Console
2. 進入你的 channel 的 "Messaging API" 頁面
3. 找到 "Webhook settings"
4. 設定 Webhook URL：
   ```
   https://abc123.ngrok.io/linebot/callback
   ```
   （生產環境使用你的實際域名）
5. 點擊 "Verify" 測試連接
6. 啟用 "Use webhook"
7. **重要**: 關閉 "Auto-reply messages"（自動回覆訊息）

### 步驟 7: 測試 Bot

1. 在 LINE Developers Console 找到你的 Bot 的 QR Code
2. 使用 LINE App 掃描 QR Code 加為好友
3. 發送訊息測試：
   - "hello"
   - "list pods"
   - "show deployments"

## 🎯 快速測試腳本

使用提供的測試腳本：

```bash
python test_linebot_webhook.py
```

這會測試：
- ✅ 健康檢查端點
- ✅ LINE Bot 配置
- ✅ 聊天 API

## 📊 監控和除錯

### 查看日誌

```bash
# 如果使用 Python 直接運行
# 日誌會直接輸出到控制台

# 如果使用 Docker
docker-compose logs -f kubewizard-api
```

### 設定除錯模式

在 `.env` 中：
```bash
LOG_LEVEL=DEBUG
DEBUG_LEVEL=2
```

### 測試端點

瀏覽器開啟：
- API 文檔: http://localhost:8000/docs
- 健康檢查: http://localhost:8000/health
- LINE Bot 測試: http://localhost:8000/linebot/test

## ⚠️ 常見問題

### Q1: "Invalid signature" 錯誤
**A**: 檢查 `LINE_CHANNEL_SECRET` 是否正確配置

### Q2: Bot 不回應
**A**: 
1. 檢查服務是否運行：`curl http://localhost:8000/health`
2. 檢查 webhook URL 是否可訪問
3. 確認已啟用 webhook 並關閉自動回覆

### Q3: "Configuration warning" 訊息
**A**: 確保 `AI_GOOGLE_API_KEY` 已正確設定

### Q4: 連不到 Redis
**A**: 
- 使用 Docker: `docker-compose up -d redis`
- 本地 Redis: 確保 Redis 服務正在運行
- 或不設定 REDIS_URL，系統會使用內存儲存

## 🔗 有用的連結

- [完整文檔](kubewizard_linebot/LINE_BOT_README.md)
- [整合摘要](LINEBOT_INTEGRATION_SUMMARY.md)
- [主 README](README.md)
- [LINE Messaging API 文檔](https://developers.line.biz/en/docs/messaging-api/)

## 🎉 成功！

如果一切正常，你應該能夠：
1. ✅ 在 LINE 中與 Bot 對話
2. ✅ Bot 使用 KubeAgent 回答 Kubernetes 相關問題
3. ✅ 對話歷史被保存在 Redis 中
4. ✅ 通過 REST API 訪問相同的功能

## 📝 下一步

- 查看 [API 文檔](http://localhost:8000/docs) 了解所有可用端點
- 閱讀 [Agent 功能文檔](agents/AGENT_FEATURES.md) 了解 KubeAgent 的能力
- 自訂 Bot 的回應和功能

---

**需要幫助？** 查看詳細文檔或檢查日誌文件。
