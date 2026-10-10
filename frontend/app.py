"""
AgriDialectAgent —— Streamlit 前端
- 聊天页面
- 知识来源展示
- Agent 执行流程展示
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests
import json

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="AgriDialectAgent",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== API 基础地址 ====================
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")


# ==================== 侧边栏 ====================
with st.sidebar:
    st.title("🌾 AgriDialectAgent")
    st.markdown("农业方言智能语义转换系统")
    st.divider()

    # 状态查询
    if st.button("查询Agent状态", use_container_width=True):
        try:
            resp = requests.get(f"{API_BASE}/api/status", timeout=5)
            if resp.status_code == 200:
                status = resp.json()
                st.success(f"服务运行中")
                st.json(status)
            else:
                st.error("服务异常")
        except Exception:
            st.error("无法连接后端服务")

    st.divider()

    # 知识库上传
    st.subheader("上传知识库")
    uploaded_file = st.file_uploader(
        "选择CSV知识库文件",
        type=["csv"],
        help="上传后将自动重建向量库",
    )
    if uploaded_file is not None:
        if st.button("开始上传并重建", use_container_width=True):
            with st.spinner("正在处理..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    resp = requests.post(f"{API_BASE}/api/upload", files=files, timeout=120)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(f"重建完成！{data.get('chunk_count', 0)} 个文本块，{data.get('vector_count', 0)} 条向量")
                    else:
                        st.error(f"上传失败: {resp.text}")
                except Exception as e:
                    st.error(f"请求异常: {e}")

    st.divider()
    st.caption("v1.0.0 | FastAPI + LangGraph + RAG")


# ==================== 主页面 ====================
st.title("🌾 农业方言翻译助手")
st.markdown("输入农业方言，获取标准农业术语翻译 —— 基于 LangGraph + RAG 的智能语义转换系统")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示聊天历史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入框
user_input = st.chat_input("请输入农业方言（如：打坷垃、耪地、耠地）...")

if user_input:
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 调用后端 API
    with st.chat_message("assistant"):
        with st.spinner("Agent 思考中..."):
            try:
                resp = requests.post(
                    f"{API_BASE}/api/chat",
                    json={"query": user_input},
                    timeout=60,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    translation = data.get("translation") or data.get("direct_reply") or "无结果"

                    # 显示翻译结果
                    st.markdown(f"### 翻译结果\n{translation}")

                    # 显示意图
                    if data.get("intent"):
                        st.caption(f"意图: {data['intent']}")

                    # 显示知识来源
                    sources = data.get("sources", [])
                    if sources:
                        with st.expander("知识来源"):
                            for i, src in enumerate(sources):
                                st.text(f"[{i+1}] {src}")

                    # 显示执行日志
                    logs = data.get("execution_logs", [])
                    if logs:
                        with st.expander("Agent 执行流程"):
                            for log in logs:
                                st.text(log)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": str(translation),
                    })
                else:
                    st.error(f"API 错误: {resp.status_code}")
            except Exception as e:
                st.error(f"请求失败: {e}\n\n请确保后端服务已启动: `python -m app.main`")
