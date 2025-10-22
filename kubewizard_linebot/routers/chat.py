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
        from agent import KubeAgent
        
        # Create agent instance
        agent = KubeAgent()
        
        # Get response from agent
        result = agent.invoke(request.message)
        reply = result.get("output", "抱歉，我無法處理您的請求。")
        
        # Save conversation to memory
        memory_service.add_message(request.user_id, "user", request.message)
        memory_service.add_message(request.user_id, "assistant", reply)
        
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
