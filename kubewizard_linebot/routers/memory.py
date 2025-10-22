"""
Memory API Router
"""
from fastapi import APIRouter

from kubewizard_linebot.config import get_settings
from kubewizard_linebot.memory import MemoryService

router = APIRouter()

# Initialize services
settings = get_settings()
memory_service = MemoryService(redis_url=settings.redis_url)


@router.get("/memory/{user_id}")
async def get_memory(user_id: str, limit: int = 10):
    """
    獲取用戶的對話歷史
    
    - **user_id**: 用戶 ID
    - **limit**: 返回的最大消息數量（默認 10）
    """
    history = memory_service.get_history(user_id, limit=limit)
    
    return {
        "user_id": user_id,
        "message_count": len(history),
        "history": history
    }


@router.delete("/memory/{user_id}")
async def clear_memory(user_id: str):
    """
    清除用戶的對話歷史
    
    - **user_id**: 用戶 ID
    """
    memory_service.clear_history(user_id)
    
    return {
        "message": f"已清除用戶 {user_id} 的對話歷史",
        "user_id": user_id
    }
