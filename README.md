# AI 出行规划助手 🧭

一个基于 **Function Calling（函数调用）** 的出行规划 **Agent**，能自动判断是否需要调用工具（如实时天气）获取真实数据，再结合大模型知识为用户生成实用的旅行建议。

> 技术亮点：不只是一个"对话机器人"，而是一个**会调用工具、能获取实时信息的 Agent**——体现大模型应用中的工具编排能力。

## ✨ 核心能力

- 🌤️ **实时天气查询**：Agent 识别到需要天气数据时，自动调用 `get_weather` 工具获取真实天气，绝不编造
- 🗺️ **行程规划**：基于真实天气数据 + 模型知识，给出可执行的旅行建议和行程安排
- 🔧 **工具编排**：通过 Function Calling 让大模型自主决定"何时调用工具、传什么参数、如何综合结果"
- 💬 **多轮对话**：支持连续对话，可追问（如"那后几天呢？"）
- 🔍 **过程可视化**：网页界面实时展示"本次调用了哪些工具、传了什么参数"——Agent 的思考过程透明可见

## 🛠 技术栈

- **Python 3**
- **DeepSeek 大模型 API**（OpenAI SDK 调用）
- **Function Calling**（工具调用，本项目的核心）
- **Open-Meteo 免费天气 API**（无需注册 Key）
- **Streamlit**（网页界面）

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install openai streamlit
```

### 2. 配置 API Key

在项目目录创建 `.env` 文件，写入：

```bash
DEEPSEEK_API_KEY=sk-你的key
```

> `.env` 已被 `.gitignore` 忽略，不会提交到 GitHub，请勿把 Key 写进代码。

### 3. 运行

网页版：

```bash
streamlit run app.py
```

浏览器自动打开对话页面。

命令行测试版（可选）：

```bash
python agent.py
```

## 📂 项目结构

```
ai_travel_agent/
├── app.py            # Streamlit 网页界面（含工具调用过程展示）
├── agent.py          # Agent 核心逻辑（Function Calling 循环）
├── tools.py          # 工具模块（天气查询 + 工具注册表）
├── env_loader.py     # 安全读取 .env
├── test_agent.py     # 命令行功能测试
└── .gitignore        # 忽略 .env、缓存等
```

## 🧠 工作原理（核心逻辑）

```
用户提问 "杭州这几天的天气适合旅游吗？"
        │
        ▼
① 带工具清单发给大模型 (get_weather 的说明)
        │
        ▼
② 大模型判断: 需要天气 → 返回 "调用 get_weather(city=杭州, days=5)"
        │
        ▼
③ 程序执行真实天气API → 得到杭州真实天气
        │
        ▼
④ 把真实天气 + 问题 再发给大模型
        │
        ▼
⑤ 大模型基于真实数据 → 生成旅行建议
```

这个"**判断需要什么 → 调用工具 → 综合推理**"的循环，就是 Agent 的核心，也是大模型应用开发的重要能力。

## 📌 说明

- 天气数据来自 Open-Meteo 免费 API，支持国内主要城市
- 本项目为个人学习/求职作品，展示大模型应用中的 Agent 与工具调用能力
- API Key 通过 `.env` 环境变量配置，安全不泄露
