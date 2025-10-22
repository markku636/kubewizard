"""
LINE Bot Webhook Router
處理 LINE Bot 的 callback 請求
"""
import logging
import urllib.parse
from fastapi import APIRouter, Request, HTTPException, Header
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from kubewizard_linebot.config import get_settings
from kubewizard_linebot.memory import MemoryService
from agents import KubeAgent

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize settings and services
settings = get_settings()
memory_service = MemoryService(redis_url=settings.redis_url)

# Initialize LINE Bot API
line_bot_api = LineBotApi(settings.line_channel_access_token)
handler = WebhookHandler(settings.line_channel_secret)


@router.post("/linebot/callback")
async def callback(
    request: Request,
    x_line_signature: str = Header(None, alias="X-Line-Signature")
):
    """
    LINE Bot Webhook Callback 端點
    
    處理來自 LINE 平台的 webhook 事件
    """
    # Get request body
    body = await request.body()
    body_str = body.decode('utf-8')
    
    # Log the request
    logger.info(f"LINE webhook received. Signature: {x_line_signature}")
    logger.debug(f"Request body: {body_str}")
    
    # Handle webhook body
    try:
        handler.handle(body_str, x_line_signature)
    except InvalidSignatureError:
        logger.error("Invalid signature. Please check your channel access token/channel secret.")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Error handling webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"status": "ok"}


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """
    處理 LINE 文字訊息事件
    """
    try:
        # Get user input and user ID
        input_text = event.message.text
        user_id = event.source.user_id
        
        logger.info(f"Received message from user {user_id}: {input_text}")
        
        # Create KubeAgent instance
        agent = KubeAgent()
        
        # Get response from agent
        result = agent.invoke(input_text)
        reply_text = result.get("output", "抱歉，我無法理解您的問題。")
        
        # Save conversation to memory
        memory_service.add_message(user_id, "user", input_text)
        memory_service.add_message(user_id, "assistant", reply_text)
        
        # Reply to user
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        
        logger.info(f"Replied to user {user_id}: {reply_text[:50]}...")
        
    except Exception as e:
        logger.error(f"Error handling text message: {e}", exc_info=True)
        
        # Send error message to user
        try:
            error_message = "抱歉，處理您的訊息時發生錯誤。請稍後再試。"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=error_message)
            )
        except Exception as reply_error:
            logger.error(f"Failed to send error message: {reply_error}")


@router.get("/linebot/test")
async def test_linebot_config():
    """
    測試 LINE Bot 配置
    """
    try:
        # Test LINE Bot API connection
        bot_info = line_bot_api.get_bot_info()
        
        return {
            "status": "ok",
            "bot_info": {
                "display_name": bot_info.display_name,
                "user_id": bot_info.user_id,
                "picture_url": bot_info.picture_url if hasattr(bot_info, 'picture_url') else None
            },
            "config": {
                "channel_secret": "configured" if settings.line_channel_secret else "missing",
                "channel_access_token": "configured" if settings.line_channel_access_token else "missing"
            }
        }
    except Exception as e:
        logger.error(f"LINE Bot configuration test failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "config": {
                "channel_secret": "configured" if settings.line_channel_secret else "missing",
                "channel_access_token": "configured" if settings.line_channel_access_token else "missing"
            }
        }
