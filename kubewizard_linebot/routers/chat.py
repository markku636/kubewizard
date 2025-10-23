"""
Chat API Router
"""
import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

from kubewizard_linebot.models import ChatRequest, ChatResponse
from kubewizard_linebot.config import get_settings
from kubewizard_linebot.memory import MemoryService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
settings = get_settings()
memory_service = MemoryService(redis_url=settings.redis_url)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    處理聊天請求
    
    - **message**: 用戶消息
    - **user_id**: 用戶 ID（可選，默認為 default_user）
    """
    session_id = str(uuid.uuid4())
    
    try:
        # Import KubeAgent
        from agents import KubeAgent
        
        # Create agent instance with user_id to maintain conversation context
        # 重要：必須傳入 user_id，這樣每個用戶都有獨立的對話記憶
        agent = KubeAgent(user_id=request.user_id)
        
        # Get response from agent
        # agent 內部已經會處理記憶，所以這裡不需要再額外保存
        result = agent.invoke(request.message)
        reply = result.get("output", "抱歉，我無法處理您的請求。")
        
        return ChatResponse(
            reply=reply,
            session_id=session_id,
            user_id=request.user_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"處理聊天請求時發生錯誤：{str(e)}"
        )
