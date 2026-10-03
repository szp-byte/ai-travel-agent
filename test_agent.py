# -*- coding: utf-8 -*-
"""test_agent.py - 测试 Agent 的 Function Calling 是否跑通"""
from agent import TravelAgent

def main():
    print("=" * 50)
    print("测试1: 需要调用工具的问题")
    print("=" * 50)
    agent = TravelAgent()
    q = "北京明天天气怎么样？适合去户外玩吗？"
    print(f"问题: {q}")
    print("\n[Agent 思考中...]")
    ans = agent.chat(q)
    print("\n工具调用轨迹:", agent.tool_trace)
    print("\nAgent回答:")
    print(ans)

    print("\n" + "=" * 50)
    print("测试2: 不需要工具的问题")
    print("=" * 50)
    q2 = "什么是RAG？"
    print(f"问题: {q2}")
    ans2 = agent.chat(q2)
    print("\n工具调用轨迹:", agent.tool_trace)
    print("\nAgent回答:")
    print(ans2)

if __name__ == "__main__":
    main()
