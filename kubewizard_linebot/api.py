#!/usr/bin/env python3
"""
KubeWizard LINE Bot API 主應用
"""
import sys
import os
import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kubewizard_linebot.config import get_settings, validate_required_settings
from kubewizard_linebot.models import HealthResponse
from kubewizard_linebot.routers import chat, memory, linebot_webhook
from utils.k8s_config import get_k8s_config_manager

# 設定日誌
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KubeWizard LINE Bot API",
    description="AI-powered LINE Bot for Kubernetes management with Google Gemini",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(memory.router, prefix="/api", tags=["Memory"])
app.include_router(linebot_webhook.router, tags=["LINE Bot"])

# Get settings
settings = get_settings()


@app.get("/")
async def root():
    """根端點 - API 資訊"""
    return {
        "name": "KubeWizard LINE Bot API",
        "version": "1.0.0",
        "description": "AI-powered LINE Bot for Kubernetes management",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康檢查端點"""
    services = {}
    
    # Check AI configuration
    services["gemini_ai"] = "configured" if settings.ai_google_api_key else "missing"
    services["ai_model"] = settings.ai_model
    
    # Check LINE Bot configuration
    services["line_bot"] = "configured" if (settings.line_channel_secret and settings.line_channel_access_token) else "not configured"
    
    # Check Redis
    try:
        import redis
        redis_client = redis.from_url(settings.redis_url, socket_connect_timeout=2)
        redis_client.ping()
        services["redis"] = "connected"
    except Exception as e:
        services["redis"] = f"disconnected ({str(e)[:50]})"
    
    # Check KubeAgent
    try:
        from agents import KubeAgent
        services["kube_agent"] = "available"
    except Exception as e:
        services["kube_agent"] = f"error: {str(e)[:50]}"
    
    # Determine overall status
    status = "healthy" if services["gemini_ai"] == "configured" else "degraded"
    
    return HealthResponse(
        status=status,
        services=services,
        timestamp=datetime.now().isoformat()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全域例外處理器"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting KubeWizard LINE Bot API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API documentation: http://localhost:8000/docs")
    print("💚 Health check: http://localhost:8000/health")
    
    # 初始化 Kubernetes 配置（自動判斷環境）
    try:
        print("\n🔧 初始化 Kubernetes 配置...")
        k8s_manager = get_k8s_config_manager()
        if k8s_manager.load_config():
            if k8s_manager.is_in_cluster:
                print("✅ Kubernetes 配置已載入 (集群內環境)")
            else:
                print("✅ Kubernetes 配置已載入 (本地環境)")
        else:
            print("⚠️  無法載入 Kubernetes 配置 (某些功能可能受限)")
    except Exception as e:
        print(f"⚠️  初始化 K8s 配置時發生錯誤: {e}")
    
    try:
        validate_required_settings()
        print("✅ Configuration validated")
    except Exception as e:
        print(f"⚠️  Configuration warning: {e}")
    
    print("\n按 Ctrl+C 停止服務\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
