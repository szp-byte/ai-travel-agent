# -*- coding: utf-8 -*-
"""
agent.py - 基于 Function Calling 的出行规划 Agent

流程:
  用户问题
    -> 带工具清单发给大模型
    -> 若大模型要求调用工具, 则执行工具, 把结果回传
    -> 大模型基于工具结果生成最终回答
"""

import os
import json

from openai import OpenAI

from tools import TOOLS, TOOL_FUNCTIONS
from env_loader import load_dotenv

load_dotenv()  # 自动读取 .env

# 从环境变量读取 API Key (安全, 不硬编码)
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

SYSTEM_PROMPT = (
    "你是一位专业的旅行规划助手。你可以调用工具获取实时信息（如天气）来帮助用户。\n"
    "规则：\n"
    "1. 当问题需要实时数据（如天气、温度）时，必须先调用工具获取，不要凭记忆编造。\n"
    "2. 根据工具返回的真实结果，结合你的知识，给用户一个完整、实用的回答。\n"
    "3. 回答用中文，条理清晰，可给出可执行的行程安排或建议。\n"
)


class TravelAgent:
    def __init__(self):
        if not API_KEY:
            raise RuntimeError("未检测到 DEEPSEEK_API_KEY 环境变量，请先设置后再运行。")
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        # 记录本轮工具调用过程, 便于展示
        self.tool_trace = []

    def _call_tool(self, name: str, args: dict):
        """执行工具, 返回工具结果字符串"""
        if name not in TOOL_FUNCTIONS:
            return json.dumps({"error": f"未知工具: {name}"}, ensure_ascii=False)
        try:
            result = TOOL_FUNCTIONS[name](**args)
            self.tool_trace.append({"tool": name, "args": args})
            return result
        except TypeError as e:
            return json.dumps({"error": f"工具参数错误: {e}", "args": args}, ensure_ascii=False)

    def chat(self, user_input, history=None) -> str:
        """对话入口。history: 可选, 之前的消息列表(OpenAI格式), 用于多轮对话"""
        self.tool_trace = []
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        # 支持传入历史(列表)或单条字符串
        if isinstance(user_input, list):
            messages.extend(user_input)
        else:
            messages.append({"role": "user", "content": user_input})

        # ---- 循环: 允许大模型多次调用工具 ----
        for _ in range(5):  # 最多5轮工具调用, 防止死循环
            resp = self.client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
            msg = resp.choices[0].message

            # 没有工具调用 -> 大模型已给出最终回答
            if not msg.tool_calls:
                return msg.content or ""

            # 有工具调用 -> 逐个执行
            messages.append(msg)  # 把带tool_calls的assistant消息加入
            for tc in msg.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                tool_result = self._call_tool(name, args)
                # 把工具结果以 role=tool 回传
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_result,
                })

        return "工具调用次数过多，请重试或换一种问法。"


def main():
    """命令行入口, 用于测试 Agent 逻辑"""
    try:
        agent = TravelAgent()
    except RuntimeError as e:
        print(f"[错误] {e}")
        print("请先设置环境变量: set DEEPSEEK_API_KEY=你的key")
        return

    print("=" * 50)
    print("出行规划 Agent 已启动 (输入 exit 退出)")
    print("=" * 50)
    while True:
        try:
            q = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见!")
            break
        if not q:
            continue
        if q.lower() in ("exit", "quit"):
            print("再见!")
            break
        print("\n[Agent思考中...]")
        answer = agent.chat(q)
        print("\nAgent:", answer)


if __name__ == "__main__":
    main()
