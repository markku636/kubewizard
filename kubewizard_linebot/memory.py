"""
Redis 記憶服務
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryService:
    """
    管理對話記憶的服務
    支援 Redis 持久化和內存回退
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        初始化記憶服務
        
        Args:
            redis_url: Redis 連接 URL，如果為 None 則使用內存存儲
        """
        self.redis_client = None
        self.memory_store: Dict[str, List[Dict[str, Any]]] = {}
        
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                self.redis_client.ping()
                logger.info(f"✅ Connected to Redis: {redis_url}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to connect to Redis: {e}")
                logger.info("📝 Using in-memory storage as fallback")
    
    def add_message(self, user_id: str, role: str, content: str) -> None:
        """
        添加消息到對話歷史
        
        Args:
            user_id: 用戶 ID
            role: 角色 (user/assistant)
            content: 消息內容
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.redis_client:
            try:
                import json
                key = f"chat:{user_id}"
                self.redis_client.rpush(key, json.dumps(message))
                self.redis_client.expire(key, 3600)  # 1 hour TTL
                return
            except Exception as e:
                logger.error(f"Redis error: {e}")
        
        # Fallback to in-memory
        if user_id not in self.memory_store:
            self.memory_store[user_id] = []
        self.memory_store[user_id].append(message)
    
    def get_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        獲取對話歷史
        
        Args:
            user_id: 用戶 ID
            limit: 返回的最大消息數量
            
        Returns:
            消息歷史列表
        """
        if self.redis_client:
            try:
                import json
                key = f"chat:{user_id}"
                messages = self.redis_client.lrange(key, -limit, -1)
                return [json.loads(msg) for msg in messages]
            except Exception as e:
                logger.error(f"Redis error: {e}")
        
        # Fallback to in-memory
        history = self.memory_store.get(user_id, [])
        return history[-limit:] if len(history) > limit else history
    
    def clear_history(self, user_id: str) -> None:
        """
        清除用戶的對話歷史
        
        Args:
            user_id: 用戶 ID
        """
        if self.redis_client:
            try:
                key = f"chat:{user_id}"
                self.redis_client.delete(key)
                return
            except Exception as e:
                logger.error(f"Redis error: {e}")
        
        # Fallback to in-memory
        if user_id in self.memory_store:
            del self.memory_store[user_id]
