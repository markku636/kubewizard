"""
API 數據模型
"""
from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天請求模型"""
    message: str = Field(..., description="用戶消息")
    user_id: str = Field(default="default_user", description="用戶 ID")


class ChatResponse(BaseModel):
    """聊天響應模型"""
    reply: str = Field(..., description="AI 回覆")
    session_id: str = Field(..., description="會話 ID")
    user_id: str = Field(..., description="用戶 ID")
    timestamp: str = Field(..., description="時間戳")


class HealthResponse(BaseModel):
    """健康檢查響應模型"""
    status: str = Field(..., description="服務狀態")
    timestamp: str = Field(..., description="時間戳")
    services: dict = Field(default_factory=dict, description="各項服務狀態")
