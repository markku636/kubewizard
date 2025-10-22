# KubeWizard 快速入門指南

## 🚀 5 分鐘快速開始

### 步驟 1: 獲取 API Key

前往 [Google AI Studio](https://makersuite.google.com/app/apikey) 獲取免費的 Gemini API Key。

### 步驟 2: 克隆專案

```bash
git clone https://github.com/markku636/kubewizard.git
cd kubewizard
```

### 步驟 3: 設置環境

```bash
# 複製配置範例
cp .env.example .env

# 編輯 .env 文件，填入你的 API Key
# 在 Windows 上使用 notepad .env
# 在 Linux/Mac 上使用 nano .env 或 vim .env
```

最少只需設置：
```env
AI_GOOGLE_API_KEY=你的_API_KEY
```

### 步驟 4: 安裝依賴

```bash
pip install -r requirements.txt
```

### 步驟 5: 開始使用

#### 選項 A: CLI 模式（最簡單）

```bash
python main.py
```

然後你可以直接輸入問題：
```
> 請列出所有 namespace
> 檢查 pod 狀態
> 幫我診斷為什麼 pod 啟動失敗
```

#### 選項 B: API 模式

```bash
python -m kubewizard_linebot.api
```

然後訪問：
- API 文檔: http://localhost:8000/docs
- 健康檢查: http://localhost:8000/health

測試 API：
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "user_id": "test"}'
```

#### 選項 C: Docker 模式（推薦生產環境）

```bash
docker-compose up -d
```

## 💡 使用技巧

### CLI 模式命令

- `clear` - 清除對話歷史
- `exit` / `quit` - 退出程式
- 直接輸入問題與 AI 對話

### 問題範例

```
# Kubernetes 診斷
> 為什麼我的 pod 一直 pending？
> 檢查 deployment 的狀態
> 幫我看看有沒有資源不足的問題

# Kubernetes 操作
> 列出所有運行中的 pod
> 顯示 kube-system namespace 的資源
> 查看最近的事件

# 網路搜尋
> 如何配置 Kubernetes Ingress？
> ServiceMesh 是什麼？
```

## 🔧 可選配置

### Redis（用於持久化記憶）

```bash
# 使用 Docker 啟動 Redis
docker run -d -p 6379:6379 redis:7-alpine

# 或使用 docker-compose（已包含 Redis）
docker-compose up -d
```

### LINE Bot 整合

1. 在 [LINE Developers](https://developers.line.biz/) 創建 Messaging API 頻道
2. 獲取 Channel Secret 和 Channel Access Token
3. 在 `.env` 中設置：
```env
LINE_CHANNEL_SECRET=你的_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=你的_access_token
```

## 🧪 驗證安裝

```bash
# 運行測試
python test_units.py

# 應該看到：
# ✅ 配置正常
# ✅ KubeAgent 創建成功
# ✅ 記憶服務正常
# ✅ API 模型正常
```

## ❓ 常見問題

### Q: 無法連接到 Kubernetes？

確保 `KUBECONFIG` 環境變數正確設置：
```env
KUBECONFIG=~/.kube/config
```

### Q: API 啟動失敗？

檢查：
1. 是否已安裝所有依賴？`pip install -r requirements.txt`
2. API Key 是否正確？檢查 `.env` 文件
3. 端口 8000 是否被占用？

### Q: Redis 連接失敗？

不用擔心！系統會自動使用內存存儲作為備用方案。如需持久化，請啟動 Redis。

## 📚 下一步

- 閱讀完整的 [README.md](README.md)
- 查看 [API 文檔](http://localhost:8000/docs)（啟動 API 後）
- 瀏覽 [重構總結](REFACTORING_SUMMARY.md) 了解專案結構

## 🆘 獲取幫助

遇到問題？
1. 查看 [README.md](README.md) 的常見問題部分
2. 在 GitHub 上提交 [Issue](https://github.com/markku636/kubewizard/issues)
3. 檢查日誌輸出找到錯誤信息

---

**祝使用愉快！** 🎉
