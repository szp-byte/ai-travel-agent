# -*- coding: utf-8 -*-
"""
app.py - 出行规划 Agent 的 Streamlit 网页界面

运行: streamlit run app.py
"""

import streamlit as st
from agent import TravelAgent

# ---------- 页面配置 ----------
st.set_page_config(page_title="AI 出行规划助手", page_icon="🧭", layout="wide")

# ---------- 初始化 ----------
if "agent" not in st.session_state:
    try:
        st.session_state.agent = TravelAgent()
    except RuntimeError as e:
        st.error(f"⚠️ {e} 请先在项目目录的 .env 中配置 DEEPSEEK_API_KEY")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []  # OpenAI 格式历史

# ---------- 侧边栏 ----------
with st.sidebar:
    st.title("🧭 AI 出行规划助手")
    st.markdown("一个基于 **Function Calling** 的 Agent，能调用天气工具帮你规划行程。")
    st.divider()
    st.markdown("### 支持的技能")
    st.markdown("- 🌤️ 实时天气查询")
    st.markdown("- 🗺️ 行程规划建议")
    st.markdown("### 试试这样问")
    st.markdown("""
    - 北京周末适合旅游吗？
    - 唐山这几天天气怎么样？
    - 帮我规划一个去杭州的三日游
    """)
    if st.button("清空对话"):
        st.session_state.messages = []
        st.rerun()

# ---------- 主区标题 ----------
st.title("AI 出行规划助手")
st.caption("Agent 会自动判断是否需要调用工具获取实时天气，再为你生成回答。")

# ---------- 展示历史消息 ----------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# ---------- 输入 ----------
prompt = st.chat_input("问问天气、规划行程……")

if prompt:
    # 追加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    agent = st.session_state.agent
    # 把历史(不含system)传给agent, agent内部会加system
    history = [m for m in st.session_state.messages[:-1] if m["role"] in ("user", "assistant")]

    with st.chat_message("assistant"):
        with st.spinner("Agent 思考中……"):
            answer = agent.chat(prompt, history=history)
            trace = agent.tool_trace

        # 展示工具调用过程 (亮点!)
        if trace:
            with st.expander("🔧 本次调用了这些工具", expanded=True):
                for t in trace:
                    args_str = "、".join(f"{k}={v}" for k, v in t["args"].items())
                    st.markdown(f"- **{t['tool']}**( {args_str} ) ✅")
            st.caption("Agent 先获取了实时数据，再基于数据回答。")
        else:
            st.caption("ℹ️ 本次无需调用工具，直接回答。")

        st.markdown(answer)

    # 保存助手回复
    st.session_state.messages.append({"role": "assistant", "content": answer})
