"""
聊天历史查询服务
"""
from app.database.session import SyncSessionLocal
from app.models.conversation import Conversation


def get_history(thread_id: str) -> dict:
    """
    查询指定会话的聊天记录

    参数:
        thread_id: 会话线程ID

    返回:
        包含对话列表的字典
    """
    db = SyncSessionLocal()
    try:
        records = (
            db.query(Conversation)
            .filter(Conversation.thread_id == thread_id)
            .order_by(Conversation.created_at.asc())
            .all()
        )

        conversations = []
        for r in records:
            conversations.append({
                "id": r.id,
                "thread_id": r.thread_id,
                "role": r.role,
                "user_query": r.user_query,
                "translation": r.translation,
                "intent": r.intent,
                "created_at": r.created_at,
            })

        return {
            "thread_id": thread_id,
            "total": len(conversations),
            "conversations": conversations,
        }
    finally:
        db.close()
