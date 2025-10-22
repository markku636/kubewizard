import os
from typing import Optional
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_react_agent, AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory, ConversationTokenBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.schema import StrOutputParser
import dotenv

from agents.kube_prompt import REACT_PROMPT
from tools import *
from tools.fortune_tools import search, bazi_cesuan, yaoyigua, jiemeng

# Load environment variables
dotenv.load_dotenv()

# Redis URL for chat history
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 算命工具開關（預設關閉）
ENABLE_FORTUNE_TOOLS = os.getenv("ENABLE_FORTUNE_TOOLS", "false").lower() == "true"

class KubeAgent:
    """KubeAgent is an AI agent that helps users with Kubernetes issues.

    Init args — completion params:
    - llm: llm model
    - user_id: unique user identifier for Redis chat history
    - debug_level: debug level for the agent, 0 is no debug, 1 is verbose, 2 is verbose with intermediate steps
    """

    name: str = "KubeAgent"

    # 預設人設
    SYSTEM_PROMPT = """你是一個非常厲害的 Kubernetes 專家，你叫 KubeWizard。
    以下是你的個人設定:
    1. 你精通 Kubernetes、Docker、容器技術、微服務架構等雲原生技術。
    2. 你能夠診斷 Kubernetes 集群問題、Pod 故障、網絡配置、存儲問題等。
    3. 你會使用各種工具來幫助用戶解決問題，包括搜索、查詢 API、執行命令等。
    4. 當用戶問你問題的時候，你會有條理地分析問題，提供專業的解決方案。
    5. 如果是中文問題，就用繁體中文來作答。
    {who_you_are}
    以下是你常說的一些口頭禪：
    1. "讓我們一步步來診斷這個問題。"
    2. "根據日誌分析，問題可能出在這裡。"
    3. "建議先檢查 Pod 的狀態和事件。"
    
    以下是你解決問題的過程：
    1. 當初次和用戶對話的時候，你會先了解用戶遇到的具體問題。
    2. 當用戶希望查詢實時信息時，你會使用搜索工具。
    3. 當遇到不知道的事情或者不明白的概念，你會使用搜索工具來搜索。
    4. 你會根據用戶的問題使用不同的合適的工具來回答。
    5. 你會保存每一次的聊天記錄，以便在後續的對話中使用。
    """

    MEMORY_KEY = "chat_history"

    def __init__(self, user_id: str = "default", llm: BaseChatModel = None, debug_level: Optional[int] = None):
        self.user_id = user_id
        
        # 初始化工具列表（根據環境變數決定是否包含算命工具）
        self.tools = [
            KubeTool(), 
            KubeToolWithApprove(), 
            human_console_input(), 
            create_search_tool(), 
            RequestsGet(allow_dangerous_requests=True),
        ]
        
        # 如果啟用算命工具，則添加到工具列表
        if ENABLE_FORTUNE_TOOLS:
            print("✨ 算命工具已啟用")
            self.tools.extend([search, bazi_cesuan, yaoyigua, jiemeng])
        else:
            print("🔒 算命工具已關閉")
        
        # Load AI configuration from environment variables
        if llm is None:
            model = os.getenv("AI_MODEL", "gemini-2.0-flash-exp")
            temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
            api_key = os.getenv("AI_GOOGLE_API_KEY")
            
            if not api_key:
                raise ValueError("AI_GOOGLE_API_KEY environment variable is required")
            
            self.chatmodel = ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                google_api_key=api_key
            )
        else:
            self.chatmodel = llm
        
        # 使用新的 prompt 格式支持系統消息和工具
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    self.SYSTEM_PROMPT.format(who_you_are=""),
                ),
                MessagesPlaceholder(variable_name=self.MEMORY_KEY),
                (
                    "user",
                    "{input}"
                ),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ],
        )

        # 獲取 Redis 聊天歷史
        self.chat_message_history = self.get_memory()

        # 使用 ConversationTokenBufferMemory 來管理 token 限制
        self.memory = ConversationTokenBufferMemory(
            llm=self.chatmodel,
            human_prefix="用戶",
            ai_prefix="KubeWizard",
            memory_key=self.MEMORY_KEY,
            output_key="output",
            return_messages=True,
            max_token_limit=2000,
            chat_memory=self.chat_message_history,
        )

        # 創建 agent
        agent = create_openai_tools_agent(
            self.chatmodel,
            tools=self.tools,
            prompt=self.prompt,
        )

        verbose = False
        return_intermediate_steps = False
        if debug_level is None:
            debug_level = int(os.getenv("DEBUG_LEVEL", "1"))

        if debug_level == 1:
            verbose = True
        elif debug_level >= 2:
            verbose = True
            return_intermediate_steps = True

        self.agent = AgentExecutor(
            name=self.name,
            agent=agent,
            memory=self.memory,
            tools=self.tools,
            return_intermediate_steps=return_intermediate_steps,
            handle_parsing_errors=True,
            verbose=verbose,
        )

    def get_memory(self):
        """使用 user_id 初始化 RedisChatMessageHistory"""
        try:
            chat_message_history = RedisChatMessageHistory(
                url=REDIS_URL, 
                session_id=self.user_id, 
                key_prefix="chat_history", 
                ttl=3600
            )
            print(f"chat_message_history for user_id {self.user_id}: {chat_message_history.messages}")

            store_message = chat_message_history.messages
            
            # 如果消息過多，進行總結
            if len(store_message) > 10:
                prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            self.SYSTEM_PROMPT + "\n這是一段你和用戶的對話記憶，對其進行總結摘要，摘要使用第一人稱'我'，並且提取其中的用戶關鍵信息。以如下格式返回:\n 總結摘要內容｜用戶關鍵信息 \n 例如 用戶張三問候我，我禮貌回覆，然後他問我 Kubernetes 問題，我幫他解決了。｜張三"
                        ),
                        ("user", "{input}"),
                    ]
                )
                chain = prompt | self.chatmodel
                summary = chain.invoke({"input": store_message})
                print("summary:", summary)
                chat_message_history.clear()
                chat_message_history.add_message(summary)
                print("總結後：", chat_message_history.messages)
            
            return chat_message_history
        except Exception as e:
            print(f"Redis connection failed: {e}, using in-memory history")
            # 如果 Redis 連接失敗，使用內存歷史
            from langchain.memory import ChatMessageHistory
            return ChatMessageHistory()

    def invoke(self, input: str):
        """執行 agent 並返回結果"""
        result = self.agent.invoke({
            "input": input,
            "chat_history": self.get_chat_messages(),
        })
        return result

    def get_chat_messages(self):
        """獲取聊天歷史消息"""
        return self.memory.chat_memory.messages
