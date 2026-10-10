"""
聊天 API —— POST /api/chat
支持普通请求和 Streaming（SSE）
"""
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest, ChatResponse
from app.service.chat_service import process_chat
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse, summary="农业方言翻译聊天接口")
async def chat(request: ChatRequest):
    """
    聊天接口 —— 输入农业方言，返回标准术语翻译

    - **query**: 用户输入的农业方言（如"打坷垃"、"耪地"）
    - **thread_id**: 可选，会话ID（用于多轮对话上下文）
    """
    logger.info(f"[Chat] query='{request.query[:50]}', thread_id={request.thread_id}")

    result = await process_chat(
        query=request.query,
        thread_id=request.thread_id,
    )

    return ChatResponse(**result)


@router.post("/chat/stream", summary="农业方言翻译聊天接口（Streaming SSE）")
async def chat_stream(request: ChatRequest):
    """
    聊天接口（Streaming 版本） —— Server-Sent Events 流式输出

    - 事件类型: node_start / node_end / token / done
    """
    async def event_generator():
        result = await process_chat(
            query=request.query,
            thread_id=request.thread_id,
        )

        # 发送执行日志（模拟节点进度）
        for log_entry in result.get("execution_logs", []):
            yield f"data: {json.dumps({'event': 'node_log', 'data': log_entry}, ensure_ascii=False)}\n\n"

        # 发送最终结果
        final = {
            "event": "done",
            "data": {
                "thread_id": result["thread_id"],
                "translation": result.get("translation") or result.get("direct_reply"),
                "intent": result.get("intent"),
                "sources": result.get("sources"),
                "reflection": result.get("reflection"),
            },
        }
        yield f"data: {json.dumps(final, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
