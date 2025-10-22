# KubeAgent 新功能說明

## 概述

KubeAgent 已經升級，新增以下功能：

1. **Redis 聊天歷史記錄** - 使用 Redis 持久化聊天記錄
2. **預設人設** - AI 具有專業的 Kubernetes 專家人設
3. **多個工具集成** - 整合了多種實用工具

---

## 主要新功能

### 1. Redis 聊天歷史

KubeAgent 現在支持使用 Redis 來持久化聊天記錄，讓對話可以跨會話保存。

**特性：**
- 使用 `user_id` 區分不同用戶的聊天記錄
- 自動管理 token 限制（最多 2000 tokens）
- 當消息超過 10 條時，自動總結歷史記錄
- TTL 設置為 3600 秒（1 小時）
- 如果 Redis 連接失敗，自動降級到內存歷史

**使用方法：**

```python
from agents import KubeAgent

# 創建帶有 user_id 的 agent
agent = KubeAgent(user_id="user_123")

# 第一次對話
response = agent.invoke("你好")

# 後續對話會記住之前的內容
response = agent.invoke("你還記得我剛才說什麼嗎？")
```

**環境變量配置：**

```bash
# .env 文件
REDIS_URL=redis://localhost:6379/0
# 或帶密碼的連接
REDIS_URL=redis://:password@hostname:port/0
```

---

### 2. 預設人設

KubeAgent 現在具有專業的 Kubernetes 專家人設：

**人設特點：**
- 名字：KubeWizard
- 專長：Kubernetes、Docker、容器技術、微服務架構
- 能力：診斷集群問題、Pod 故障、網絡配置、存儲問題
- 語言：支持繁體中文
- 風格：有條理、專業、提供實用的解決方案

**口頭禪：**
- "讓我們一步步來診斷這個問題。"
- "根據日誌分析，問題可能出在這裡。"
- "建議先檢查 Pod 的狀態和事件。"

---

### 3. 多工具集成

KubeAgent 整合了以下工具：

#### Kubernetes 工具
1. **KubeTool** - 執行 kubectl 命令
2. **KubeToolWithApprove** - 需要批准的 kubectl 命令

#### 通用工具
3. **human_console_input** - 向用戶詢問輸入
4. **create_search_tool** - 網頁搜索工具
5. **RequestsGet** - HTTP GET 請求工具
6. **search** - SerpAPI 實時搜索（需要 SERPAPI_API_KEY）

#### 算命工具（示例）
7. **bazi_cesuan** - 八字排盤
8. **yaoyigua** - 占卜抽簽
9. **jiemeng** - 解夢

---

## 安裝和配置

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

新增的主要依賴：
- `google-search-results>=2.4.2` - SerpAPI 支持
- Redis 客戶端已包含在之前的依賴中

### 2. 環境變量配置

複製 `.env.example` 到 `.env` 並配置：

```bash
# 必需
AI_GOOGLE_API_KEY=your-google-api-key-here

# 可選 - Redis 聊天歷史
REDIS_URL=redis://localhost:6379/0

# 可選 - 算命 API
YUANFENJU_API_KEY=your-yuanfenju-api-key-here
SERPAPI_API_KEY=your-serpapi-api-key-here
```

### 3. 啟動 Redis（可選）

如果要使用 Redis 聊天歷史：

**使用 Docker：**
```bash
docker run -d -p 6379:6379 redis:latest
```

**使用 Docker Compose：**
```bash
docker-compose up -d redis
```

---

## 使用示例

### 基本使用（不使用 Redis）

```python
from agents import KubeAgent

# 創建 agent（使用內存歷史）
agent = KubeAgent()

# 對話
response = agent.invoke("我的 Pod 一直重啟，怎麼辦？")
print(response['output'])
```

### 使用 Redis 聊天歷史

```python
from agents import KubeAgent

# 為特定用戶創建 agent
agent = KubeAgent(user_id="alice@example.com")

# 第一輪對話
response = agent.invoke("你好，我是 Alice")
print(response['output'])

# 第二輪對話（agent 會記住 Alice）
response = agent.invoke("我有一個 Deployment 的問題")
print(response['output'])

# 之後重新創建 agent，聊天歷史會被保留（1小時內）
agent2 = KubeAgent(user_id="alice@example.com")
response = agent2.invoke("你還記得我之前問的問題嗎？")
print(response['output'])
```

### 使用搜索工具

```python
from agents import KubeAgent

agent = KubeAgent(user_id="user_001")

# Agent 會自動使用搜索工具來獲取實時信息
response = agent.invoke("Kubernetes 1.28 有什麼新功能？")
print(response['output'])
```

---

## 測試

運行測試腳本：

```bash
python test_agent_features.py
```

測試內容包括：
1. 工具列表檢查
2. Redis 聊天歷史功能
3. 算命工具功能

---

## 架構說明

### Memory 管理流程

1. **初始化**：根據 `user_id` 創建 `RedisChatMessageHistory`
2. **載入歷史**：從 Redis 載入該用戶的聊天記錄
3. **Token 管理**：使用 `ConversationTokenBufferMemory` 限制最多 2000 tokens
4. **自動總結**：當消息超過 10 條時，自動總結並清理舊消息
5. **持久化**：每次對話後自動保存到 Redis（TTL 1小時）

### Agent 創建流程

```
KubeAgent.__init__()
    ↓
載入 LLM (Google Gemini)
    ↓
創建 ChatPromptTemplate (系統消息 + 歷史 + 用戶輸入)
    ↓
get_memory() - 從 Redis 載入聊天歷史
    ↓
創建 ConversationTokenBufferMemory
    ↓
create_openai_tools_agent() - 創建工具代理
    ↓
AgentExecutor - 執行代理
```

---

## 工具開發指南

### 添加新工具

1. 在 `tools/` 目錄下創建新的工具文件
2. 使用 `@tool` 裝飾器定義工具函數
3. 在 `tools/__init__.py` 中導出工具
4. 在 `KubeAgent.tools` 列表中添加工具

**示例：**

```python
# tools/my_tool.py
from langchain.agents import tool

@tool
def my_custom_tool(query: str):
    """這是我的自定義工具的描述"""
    # 工具邏輯
    return "結果"
```

```python
# tools/__init__.py
from .my_tool import my_custom_tool

__all__ = [..., 'my_custom_tool']
```

```python
# agents/kube_agent.py
from tools.my_tool import my_custom_tool

class KubeAgent:
    tools = [
        ...,
        my_custom_tool,
    ]
```

---

## 常見問題

### Q: Redis 連接失敗怎麼辦？
A: Agent 會自動降級到使用內存歷史記錄，功能仍可正常使用，只是重啟後會話不會保留。

### Q: 如何修改 Token 限制？
A: 在 `KubeAgent.__init__()` 中修改 `max_token_limit` 參數：
```python
self.memory = ConversationTokenBufferMemory(
    ...
    max_token_limit=2000,  # 修改這個值
    ...
)
```

### Q: 如何修改聊天歷史的 TTL？
A: 在 `get_memory()` 方法中修改 `ttl` 參數：
```python
chat_message_history = RedisChatMessageHistory(
    url=REDIS_URL, 
    session_id=self.user_id, 
    key_prefix="chat_history", 
    ttl=3600  # 修改這個值（秒）
)
```

### Q: 如何自定義人設？
A: 修改 `KubeAgent.SYSTEM_PROMPT` 變量中的系統提示詞。

---

## 技術細節

### 使用的 LangChain 組件

- **ChatGoogleGenerativeAI** - Google Gemini LLM
- **RedisChatMessageHistory** - Redis 聊天歷史
- **ConversationTokenBufferMemory** - Token 緩衝記憶
- **create_openai_tools_agent** - 工具代理創建器
- **AgentExecutor** - 代理執行器

### Redis 數據結構

```
Key: chat_history:{user_id}
Type: List
Value: [
    {"type": "human", "content": "用戶消息"},
    {"type": "ai", "content": "AI 回復"},
    ...
]
TTL: 3600 秒
```

---

## 後續計劃

- [ ] 添加更多 Kubernetes 診斷工具
- [ ] 支持更多存儲後端（PostgreSQL, MongoDB）
- [ ] 添加對話總結和分析功能
- [ ] 支持多輪對話的上下文優化
- [ ] 添加工具使用統計和監控

---

## 參考資料

- [LangChain 文檔](https://python.langchain.com/)
- [Redis 文檔](https://redis.io/docs/)
- [Google Gemini API](https://ai.google.dev/)
- [SerpAPI 文檔](https://serpapi.com/docs)
