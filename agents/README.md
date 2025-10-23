# Agents 目錄

這個目錄包含所有 AI Agent 的實現。

## 📁 結構

```
agents/
├── __init__.py           # 模組初始化，導出所有 Agent
├── kube_agent.py         # Kubernetes 管理專用 Agent
└── kube_prompt.py        # KubeAgent 的提示詞模板
```

## 🤖 可用的 Agents

### KubeAgent
**文件**: `kube_agent.py`

Kubernetes 管理專用的 AI Agent，能夠：
- 執行 kubectl 和 helm 命令
- 診斷 Kubernetes 問題
- 提供 Kubernetes 相關建議
- 搜尋相關文檔和資訊

**使用範例**:
```python
from agents import KubeAgent

agent = KubeAgent()
result = agent.invoke("請列出所有 pod")
print(result['output'])
```

## 🔧 如何添加新的 Agent

1. **創建 Agent 文件**:
```bash
# 例如：database_agent.py
touch agents/database_agent.py
touch agents/database_prompt.py
```

2. **實現 Agent 類**:
```python
# agents/database_agent.py
from langchain.agents import create_react_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.database_prompt import DATABASE_PROMPT
from tools import *

class DatabaseAgent:
    """Database 管理專用 Agent"""
    
    def __init__(self, llm=None):
        if llm is None:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash-latest",
                temperature=0.7
            )
        
        self.llm = llm
        self.tools = [
            # 添加相關工具
        ]
        
        # 創建 agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=DATABASE_PROMPT
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )
    
    def invoke(self, input_text: str):
        """執行 Agent"""
        return self.agent_executor.invoke({"input": input_text})
```

3. **創建提示詞模板**:
```python
# agents/database_prompt.py
from langchain_core.prompts import PromptTemplate

DATABASE_PROMPT = PromptTemplate.from_template("""
你是一個 Database 管理專家...

{agent_scratchpad}
""")
```

4. **在 __init__.py 中導出**:
```python
# agents/__init__.py
from agents.kube_agent import KubeAgent
from agents.database_agent import DatabaseAgent

__all__ = ['KubeAgent', 'DatabaseAgent']
```

5. **使用新的 Agent**:
```python
from agents import DatabaseAgent

db_agent = DatabaseAgent()
result = db_agent.invoke("查詢資料庫狀態")
```

## 📝 Agent 設計原則

1. **單一職責**: 每個 Agent 專注於特定領域
2. **工具整合**: 使用 LangChain 工具擴展能力
3. **提示詞分離**: 將提示詞放在獨立文件中
4. **可配置**: 允許自定義 LLM 和參數
5. **統一接口**: 使用 `invoke()` 方法作為主要入口

## 🔄 Agent 生命週期

```
初始化 → 配置工具 → 創建 Agent → 執行任務 → 返回結果
```

## 📚 相關文檔

- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [Google Gemini API](https://ai.google.dev/)
- [項目主 README](../README.md)
