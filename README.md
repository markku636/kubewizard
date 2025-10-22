# KubeWizard

> AI-powered Kubernetes management assistant with Google Gemini integration

KubeWizard 是一個智能的 Kubernetes 管理助手，使用 Google Gemini AI 模型提供自然語言交互界面，幫助您診斷、管理和部署 Kubernetes 資源。

## 📑 目錄

- [✨ 特性](#-特性)
- [📁 專案結構](#-專案結構)
- [🚀 快速開始](#-快速開始)
  - [1. 環境準備](#1-環境準備)
  - [2. 安裝依賴](#2-安裝依賴)
  - [3. 配置環境變數](#3-配置環境變數)
  - [4. 運行方式](#4-運行方式)
- [📡 API 端點](#-api-端點)
- [🧪 測試](#-測試)
- [🔧 配置說明](#-配置說明)
- [🛠️ 開發指南](#️-開發指南)
- [📝 常見問題](#-常見問題)
- [📄 授權](#-授權)
- [🤝 貢獻](#-貢獻)
- [📚 相關資源](#-相關資源)

---

## ✨ 特性

- 🤖 **AI 驅動**: 使用 Google Gemini 2.0 Flash 模型進行智能對話
- 🔧 **Kubernetes 整合**: 直接執行 kubectl 和 helm 命令
- 💬 **對話記憶**: 使用 Redis 持久化保存對話歷史（支援內存備用）
- 🌐 **REST API**: 提供完整的 FastAPI REST 接口
- 📱 **LINE Bot 支援**: 可選的 LINE Bot 整合（需配置）
- 🐳 **Docker 部署**: 完整的 Docker 和 Docker Compose 支援
- 🔍 **網路搜尋**: 集成 DuckDuckGo 搜尋功能
- 🧪 **完整測試**: 包含單元測試和 API 測試
- 🎨 **Rich UI**: 使用 Rich 庫提供美觀的控制台界面
- ⚡ **模組化架構**: 清晰的代碼結構，易於維護和擴展

## 📁 專案結構

```
kubewizard/
├── agent/                      # KubeAgent 核心代理
│   ├── __init__.py
│   ├── agent.py               # 主要 Agent 邏輯（LangChain Agent）
│   └── prompt.py              # AI 提示詞模板
├── tools/                      # LangChain 工具集
│   ├── __init__.py
│   ├── kubetool.py            # Kubernetes 工具（kubectl、helm）
│   ├── search.py              # DuckDuckGo 搜尋工具
│   ├── request.py             # HTTP 請求工具
│   └── human.py               # 人工協助工具
├── kubewizard_linebot/        # LINE Bot API 模組
│   ├── __init__.py
│   ├── api.py                 # FastAPI 主應用
│   ├── config.py              # 配置管理（pydantic-settings）
│   ├── models.py              # Pydantic 數據模型
│   ├── memory.py              # Redis 記憶服務
│   └── routers/               # API 路由模組
│       ├── __init__.py
│       ├── chat.py            # 聊天端點
│       └── memory.py          # 記憶管理端點
├── utils/                      # 工具函數
│   ├── __init__.py
│   └── console.py             # Rich 控制台工具
├── app/                        # CLI 控制台應用
│   ├── __init__.py
│   └── app.py                 # 交互式 CLI 應用
├── main.py                     # CLI 啟動入口
├── test_units.py              # 單元測試腳本
├── test_api.py                # API 測試腳本
├── requirements.txt           # Python 依賴列表
├── Dockerfile                 # Docker 映像定義
├── docker-compose.yml         # Docker Compose 配置
├── .env.example               # 環境變數範例
├── .gitignore                 # Git 忽略規則
├── LICENSE                    # MIT 授權
├── README.md                  # 本文件
├── QUICKSTART.md              # 快速入門指南
└── REFACTORING_SUMMARY.md     # 重構總結文檔
```

## 🚀 快速開始

### 1. 環境準備

**必需**:
- Python 3.11+
- Google Gemini API Key

**可選**:
- Docker & Docker Compose（用於容器化部署）
- Redis（用於持久化記憶，否則使用內存存儲）
- LINE Bot 帳號（用於 LINE Bot 功能）

### 2. 安裝依賴

```bash
# Clone 專案
git clone https://github.com/markku636/kubewizard.git
cd kubewizard

# 安裝 Python 依賴
pip install -r requirements.txt
```

### 3. 配置環境變數

複製 `.env.example` 到 `.env` 並填入您的配置：

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

編輯 `.env` 文件（最少只需配置 API Key）：

```env
# AI Configuration（必填）
AI_GOOGLE_API_KEY=your_gemini_api_key_here
AI_MODEL=gemini-2.0-flash-exp
AI_TEMPERATURE=0.7

# Kubernetes Configuration（可選）
KUBECONFIG=~/.kube/config
DEBUG_LEVEL=1

# Redis Configuration（可選，未配置時使用內存存儲）
REDIS_URL=redis://localhost:6379/0

# LINE Bot Configuration（可選，僅需要 LINE Bot 功能時配置）
LINE_CHANNEL_SECRET=your_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_access_token

# Application Configuration
LOG_LEVEL=INFO
```

> 💡 **提示**: 如果沒有安裝 Redis，系統會自動使用內存存儲作為備用方案，重啟後對話歷史會清空。

### 4. 運行方式

#### 方式 A: CLI 控制台模式（推薦新手）

```bash
python main.py
```

這將啟動一個交互式控制台，您可以直接與 KubeAgent 對話。

**CLI 命令**:
- 直接輸入問題與 AI 對話
- `clear` - 清除對話歷史
- `exit` 或 `quit` - 退出程式

**使用範例**:
```
> 請列出所有 namespace
> 檢查 default namespace 的 pod 狀態
> 為什麼我的 pod 一直在 pending？
> 如何配置 Kubernetes Ingress？
```

#### 方式 B: API 服務器模式（推薦開發）

```bash
# 開發模式（支援熱重載）
python -m kubewizard_linebot.api

# 或使用 uvicorn（更多選項）
uvicorn kubewizard_linebot.api:app --host 0.0.0.0 --port 8000 --reload
```

API 將在 `http://localhost:8000` 啟動：
- 🏠 根端點: `http://localhost:8000/`
- 📖 API 文檔（Swagger UI）: `http://localhost:8000/docs`
- 📘 替代文檔（ReDoc）: `http://localhost:8000/redoc`
- 💚 健康檢查: `http://localhost:8000/health`

**測試 API**:
```bash
# Windows PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/api/chat" -Method POST -ContentType "application/json" -Body '{"message":"hello","user_id":"test"}'

# Linux/Mac (使用 curl)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"hello","user_id":"test"}'
```

#### 方式 C: Docker 部署（推薦生產）

```bash
# 啟動所有服務（包含 Redis）
docker-compose up -d

# 查看日誌
docker-compose logs -f kubewizard-api

# 查看所有服務狀態
docker-compose ps

# 停止服務
docker-compose down

# 停止並刪除所有數據
docker-compose down -v
```

**Docker 服務**:
- `kubewizard-api`: 主 API 服務（端口 8000）
- `redis`: Redis 數據庫（端口 6379）
- `redis-commander`: Redis 管理界面（端口 8081，使用 `--profile admin` 啟動）

## 📡 API 端點

### 根端點

```http
GET /
```

返回 API 基本信息和可用端點。

### 健康檢查

```http
GET /health
```

**回應範例**:
```json
{
  "status": "healthy",
  "services": {
    "gemini_ai": "configured",
    "ai_model": "gemini-2.0-flash-exp",
    "redis": "connected",
    "kube_agent": "available"
  },
  "timestamp": "2025-10-22T10:30:00"
}
```

### 聊天端點

```http
POST /api/chat
Content-Type: application/json

{
  "message": "請列出所有 pod",
  "user_id": "user123"
}
```

**回應**:
```json
{
  "reply": "以下是所有 namespace 中的 pod...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "timestamp": "2025-10-22T10:30:00"
}
```

### 記憶管理端點

#### 獲取對話歷史

```http
GET /api/memory/{user_id}?limit=10
```

**回應**:
```json
{
  "user_id": "user123",
  "message_count": 4,
  "history": [
    {
      "role": "user",
      "content": "你好",
      "timestamp": "2025-10-22T10:30:00"
    },
    {
      "role": "assistant",
      "content": "你好！我可以幫助你管理 Kubernetes。",
      "timestamp": "2025-10-22T10:30:01"
    }
  ]
}
```

#### 清除對話歷史

```http
DELETE /api/memory/{user_id}
```

**回應**:
```json
{
  "message": "已清除用戶 user123 的對話歷史",
  "user_id": "user123"
}
```

## 🧪 測試

### 運行單元測試

測試配置、KubeAgent、記憶服務和 API 模型：

```bash
python test_units.py
```

**預期輸出**:
```
============================================================
🧪 KubeWizard API 功能測試
============================================================

1. 測試配置...
   ✅ 配置正常
   - AI Model: gemini-2.0-flash-exp
   - Redis URL: redis://localhost:6379/0

2. 測試 KubeAgent...
   ✅ KubeAgent 創建成功
   - 測試回應: 你好！How can I help you...

3. 測試記憶服務...
   ✅ 記憶服務正常
   - 儲存的消息數: 2

4. 測試 API 模型...
   ✅ ChatRequest 正常
   ✅ ChatResponse 正常
   ✅ HealthResponse 正常

============================================================
📊 測試結果
============================================================
配置              ✅ 通過
KubeAgent       ✅ 通過
記憶服務            ✅ 通過
API 模型          ✅ 通過

總計: 4/4 測試通過

🎉 所有測試通過！
```

### 運行 API 測試

測試 API 端點（需先啟動 API 服務器）：

```bash
# 終端 1: 啟動 API 服務器
python -m kubewizard_linebot.api

# 終端 2: 運行 API 測試
python test_api.py
```

## 🔧 配置說明

### AI 配置

| 變數 | 說明 | 默認值 | 必填 |
|------|------|--------|------|
| `AI_GOOGLE_API_KEY` | Google Gemini API 密鑰 | - | ✅ 是 |
| `AI_MODEL` | 使用的 AI 模型 | `gemini-2.0-flash-exp` | ❌ 否 |
| `AI_TEMPERATURE` | 溫度參數（0-1，控制創造性） | `0.7` | ❌ 否 |

**獲取 API Key**: 訪問 [Google AI Studio](https://makersuite.google.com/app/apikey)

**可用模型**:
- `gemini-2.0-flash-exp` - 最新實驗版本（推薦）
- `gemini-1.5-pro` - 穩定版本
- `gemini-1.5-flash` - 快速版本

### Kubernetes 配置

| 變數 | 說明 | 默認值 | 必填 |
|------|------|--------|------|
| `KUBECONFIG` | Kubernetes 配置文件路徑 | `~/.kube/config` | ❌ 否 |
| `DEBUG_LEVEL` | 調試級別（0-2） | `1` | ❌ 否 |

### Redis 配置

| 變數 | 說明 | 默認值 | 必填 |
|------|------|--------|------|
| `REDIS_URL` | Redis 連接 URL | `redis://localhost:6379/0` | ❌ 否 |

**注意**: 
- 如果 Redis 不可用，系統會自動使用內存存儲作為備用方案
- 內存存儲的對話歷史在程序重啟後會丟失
- 使用 Docker Compose 部署時會自動啟動 Redis

### LINE Bot 配置（可選）

| 變數 | 說明 | 必填 |
|------|------|------|
| `LINE_CHANNEL_SECRET` | LINE Bot Channel Secret | 僅需要 LINE Bot 功能時 |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot Access Token | 僅需要 LINE Bot 功能時 |

**設置 LINE Bot**:
1. 訪問 [LINE Developers Console](https://developers.line.biz/)
2. 創建 Messaging API 頻道
3. 獲取 Channel Secret 和 Channel Access Token
4. 配置 Webhook URL 為 `https://your-domain.com/webhook`

### 應用配置

| 變數 | 說明 | 默認值 |
|------|------|--------|
| `LOG_LEVEL` | 日誌級別（DEBUG/INFO/WARNING/ERROR） | `INFO` |

## 🛠️ 開發指南

### 專案架構

KubeWizard 採用模組化架構：

```
核心層 (agent/)
  └─> KubeAgent: LangChain Agent 主邏輯
       └─> 工具層 (tools/): Kubernetes、搜尋、HTTP 等工具
       
API 層 (kubewizard_linebot/)
  ├─> FastAPI 應用
  ├─> Pydantic 模型
  ├─> Redis 記憶服務
  └─> API 路由

應用層 (app/, main.py)
  └─> CLI 交互式界面
```

### 添加新工具

1. 在 `tools/` 目錄下創建新工具文件：

```python
# tools/my_tool.py
from langchain.tools import tool

@tool
def my_kubernetes_tool(query: str) -> str:
    """
    我的自定義 Kubernetes 工具
    
    Args:
        query: 查詢參數
        
    Returns:
        str: 工具執行結果
    """
    # 實現工具邏輯
    result = execute_command(query)
    return result
```

2. 在 `agent/agent.py` 中註冊工具：

```python
from tools.my_tool import my_kubernetes_tool

# 在 KubeAgent 類的 __init__ 方法中
self.tools = [
    kubetool,
    my_kubernetes_tool,  # 添加新工具
    # ... 其他工具
]
```

### 添加新 API 端點

1. 在 `kubewizard_linebot/routers/` 創建新路由文件：

```python
# kubewizard_linebot/routers/my_router.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/my-endpoint")
async def my_endpoint():
    return {"message": "Hello from my endpoint"}
```

2. 在 `kubewizard_linebot/api.py` 中註冊路由：

```python
from kubewizard_linebot.routers import my_router

app.include_router(
    my_router.router, 
    prefix="/api", 
    tags=["MyFeature"]
)
```

### 添加新數據模型

在 `kubewizard_linebot/models.py` 中添加 Pydantic 模型：

```python
from pydantic import BaseModel, Field

class MyRequest(BaseModel):
    """我的請求模型"""
    field1: str = Field(..., description="欄位 1")
    field2: int = Field(default=0, description="欄位 2")

class MyResponse(BaseModel):
    """我的響應模型"""
    result: str
    timestamp: str
```

### 修改配置

1. 在 `kubewizard_linebot/config.py` 添加新配置：

```python
class Settings(BaseSettings):
    # 現有配置...
    
    my_new_setting: str = Field(
        default="default_value",
        description="我的新配置"
    )
```

2. 更新 `.env.example`：

```env
# My New Feature
MY_NEW_SETTING=some_value
```

3. 更新文檔說明配置用途

### 代碼風格

- 使用 Python 3.11+ 語法
- 遵循 PEP 8 規範
- 使用類型提示（Type Hints）
- 編寫清晰的 Docstrings
- 保持函數簡潔（單一職責）

### 測試指南

在 `test_units.py` 中添加測試：

```python
def test_my_feature():
    """測試我的功能"""
    print("\n5. 測試我的功能...")
    try:
        # 測試邏輯
        result = my_function()
        assert result is not None
        print(f"   ✅ 測試通過")
        return True
    except Exception as e:
        print(f"   ❌ 測試失敗: {e}")
        return False
```

## 📝 常見問題

### Q: 為什麼我的對話記憶沒有保存？

**A**: 檢查以下幾點：

1. **Redis 是否運行**？
   ```bash
   # 檢查 Redis 連接
   redis-cli ping
   # 應該返回 PONG
   ```

2. **環境變數是否正確**？
   ```env
   REDIS_URL=redis://localhost:6379/0
   ```

3. **使用 Docker 部署**？
   ```bash
   # 檢查 Redis 容器狀態
   docker-compose ps redis
   ```

如果沒有 Redis，系統會使用內存存儲，重啟後對話歷史會清空。

### Q: 如何更換 AI 模型？

**A**: 修改 `.env` 文件中的 `AI_MODEL` 變數：

```env
# 使用穩定版本
AI_MODEL=gemini-1.5-pro

# 使用快速版本
AI_MODEL=gemini-1.5-flash

# 使用最新實驗版本（默認）
AI_MODEL=gemini-2.0-flash-exp
```

不同模型的特點：
- **gemini-2.0-flash-exp**: 最新功能，可能不穩定
- **gemini-1.5-pro**: 功能最強，速度較慢
- **gemini-1.5-flash**: 速度最快，適合簡單任務

### Q: Docker 部署失敗怎麼辦？

**A**: 檢查以下項目：

1. **Docker 是否正確安裝**？
   ```bash
   docker --version
   docker-compose --version
   ```

2. **`.env` 文件是否存在且配置正確**？
   ```bash
   # Windows
   type .env
   
   # Linux/Mac
   cat .env
   ```

3. **端口是否被占用**？
   ```bash
   # Windows
   netstat -ano | findstr :8000
   netstat -ano | findstr :6379
   
   # Linux/Mac
   lsof -i :8000
   lsof -i :6379
   ```

4. **查看 Docker 日誌**：
   ```bash
   docker-compose logs kubewizard-api
   docker-compose logs redis
   ```

### Q: API 請求返回 500 錯誤？

**A**: 

1. **檢查 API Key 是否有效**：
   - 訪問 [Google AI Studio](https://makersuite.google.com/app/apikey)
   - 驗證 API Key 是否正確且未過期

2. **查看詳細錯誤信息**：
   ```bash
   # 查看服務器日誌
   docker-compose logs -f kubewizard-api
   ```

3. **檢查配置**：
   ```bash
   # 測試配置是否正確
   python test_units.py
   ```

### Q: kubectl 命令無法執行？

**A**: 

1. **確保 kubectl 已安裝**：
   ```bash
   kubectl version --client
   ```

2. **檢查 KUBECONFIG 環境變數**：
   ```env
   KUBECONFIG=~/.kube/config
   ```

3. **驗證 Kubernetes 連接**：
   ```bash
   kubectl cluster-info
   ```

4. **如果使用 Docker**，需要將 kubeconfig 掛載到容器：
   ```yaml
   # docker-compose.yml
   volumes:
     - ~/.kube:/root/.kube:ro
   ```

### Q: 如何啟用 DEBUG 模式？

**A**: 修改 `.env` 文件：

```env
LOG_LEVEL=DEBUG
DEBUG_LEVEL=2
```

重啟服務後會看到詳細的調試信息。

### Q: LINE Bot 如何配置？

**A**: 

1. **創建 LINE Bot**：
   - 訪問 [LINE Developers Console](https://developers.line.biz/)
   - 創建 Messaging API 頻道

2. **配置環境變數**：
   ```env
   LINE_CHANNEL_SECRET=your_channel_secret
   LINE_CHANNEL_ACCESS_TOKEN=your_access_token
   ```

3. **設置 Webhook**：
   - Webhook URL: `https://your-domain.com/webhook`
   - 需要 HTTPS（可使用 ngrok 測試）

4. **實現 Webhook 處理**（目前需要自行實現）

### Q: 如何貢獻代碼？

**A**: 

1. Fork 本專案
2. 創建功能分支：`git checkout -b feature/my-feature`
3. 提交更改：`git commit -am 'Add some feature'`
4. 推送到分支：`git push origin feature/my-feature`
5. 提交 Pull Request

請確保：
- 代碼通過所有測試
- 遵循項目的代碼風格
- 更新相關文檔

### Q: 在哪裡獲取更多幫助？

**A**: 

- 📖 閱讀 [QUICKSTART.md](QUICKSTART.md) 快速入門指南
- 📋 查看 [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) 了解專案結構
- 🐛 在 [GitHub Issues](https://github.com/markku636/kubewizard/issues) 提交問題
- 💬 查看現有的 Issue 和 Discussion

## 📄 授權

本專案採用 MIT License - 查看 [LICENSE](LICENSE) 文件了解詳情

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

### 貢獻指南

1. Fork 本專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 貢獻者

感謝所有為本專案做出貢獻的開發者！

## 📚 相關資源

### 文檔
- [快速入門指南](QUICKSTART.md) - 5 分鐘快速上手
- [重構總結](REFACTORING_SUMMARY.md) - 專案結構詳解
- [API 文檔](http://localhost:8000/docs) - Swagger UI（需先啟動服務）

### 技術棧
- [FastAPI](https://fastapi.tiangolo.com/) - 現代化的 Python Web 框架
- [LangChain](https://python.langchain.com/) - LLM 應用開發框架
- [Google Gemini](https://ai.google.dev/) - Google 的生成式 AI
- [Redis](https://redis.io/) - 內存數據庫
- [Pydantic](https://docs.pydantic.dev/) - 數據驗證
- [Rich](https://rich.readthedocs.io/) - 終端美化庫

### 社群
- [GitHub Issues](https://github.com/markku636/kubewizard/issues) - 問題回報和功能建議
- [GitHub Discussions](https://github.com/markku636/kubewizard/discussions) - 討論和問答

## 📧 聯繫方式

- 📧 Email: 透過 GitHub Issues 聯繫
- 🐛 Bug 回報: [提交 Issue](https://github.com/markku636/kubewizard/issues/new)
- 💡 功能建議: [提交 Feature Request](https://github.com/markku636/kubewizard/issues/new)

## 🌟 Star History

如果這個專案對你有幫助，請給它一個 ⭐️！

## 📈 版本歷史

### v1.0.0 (2025-10-22)
- ✅ 完整的 KubeAgent 功能
- ✅ FastAPI REST API
- ✅ Redis 記憶管理
- ✅ Docker 部署支援
- ✅ 模組化架構重構
- ✅ 完整的測試覆蓋
- ✅ 詳細的文檔

## 🙏 致謝

- Google Gemini AI 團隊提供強大的 AI 模型
- LangChain 社群提供優秀的框架
- 所有開源貢獻者

---

**Made with ❤️ using Google Gemini AI**

*讓 Kubernetes 管理變得更簡單！*
