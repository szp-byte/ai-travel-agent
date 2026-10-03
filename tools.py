# -*- coding: utf-8 -*-
"""
tools.py - Agent 的工具模块

每个工具是一个普通 Python 函数, 接收 JSON 可序列化参数, 返回 JSON 可序列化结果。
agent.py 会通过 Function Calling 让大模型决定调用哪个工具、传什么参数。
"""

import json
import urllib.request
import urllib.parse


# ---------- 城市坐标表 (小型内置知识: 城市 -> 经纬度) ----------
# 用免费天气API(Open-Meteo)需要经纬度。这里内置常见城市, 未知城市返回提示。
CITY_COORDS = {
    "北京": (39.90, 116.40),
    "上海": (31.23, 121.47),
    "广州": (23.13, 113.26),
    "深圳": (22.54, 114.06),
    "杭州": (30.27, 120.16),
    "南京": (32.06, 118.80),
    "成都": (30.57, 104.07),
    "武汉": (30.59, 114.31),
    "西安": (34.34, 108.94),
    "重庆": (29.56, 106.55),
    "长沙": (28.23, 112.94),
    "苏州": (31.30, 120.62),
    "天津": (39.13, 117.20),
    "唐山": (39.63, 118.18),
    "青岛": (36.07, 120.38),
    "大连": (38.91, 121.61),
    "沈阳": (41.80, 123.43),
    "哈尔滨": (45.80, 126.53),
    "郑州": (34.75, 113.63),
    "济南": (36.65, 117.12),
    "昆明": (25.04, 102.71),
    "三亚": (18.25, 109.51),
    "海口": (20.04, 110.20),
    "厦门": (24.48, 118.09),
}


def get_weather(city: str, days: int = 3):
    """查询某城市未来几天的天气预报。

    参数:
        city: 城市名(中文, 如"北京")
        days: 预报天数, 1~7, 默认3
    返回:
        JSON 字符串: {city, days, forecast: [{date, weather, temp_max, temp_min, wind}]}
    """
    city = str(city).strip()
    days = max(1, min(7, int(days)))

    if city not in CITY_COORDS:
        return json.dumps({
            "city": city,
            "error": f"暂不支持城市「{city}」。可选城市: {'、'.join(list(CITY_COORDS.keys())[:20])} 等",
            "forecast": []
        }, ensure_ascii=False)

    lat, lon = CITY_COORDS[city]
    params = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,wind_speed_10m_max",
        "timezone": "Asia/Shanghai",
        "forecast_days": days,
    })
    url = f"https://api.open-meteo.com/v1/forecast?{params}"

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return json.dumps({"city": city, "error": f"天气服务请求失败: {e}", "forecast": []},
                          ensure_ascii=False)

    # 把 WMO 天气码翻译成中文描述
    wmo = {
        0: "晴", 1: "大致晴朗", 2: "多云", 3: "阴",
        45: "雾", 48: "冻雾", 51: "小毛毛雨", 53: "毛毛雨", 55: "大毛毛雨",
        61: "小雨", 63: "中雨", 65: "大雨", 66: "冻雨", 67: "强冻雨",
        71: "小雪", 73: "中雪", 75: "大雪", 77: "雪粒", 80: "小阵雨",
        81: "阵雨", 82: "强阵雨", 85: "小阵雪", 86: "大阵雪", 95: "雷暴",
        96: "雷暴伴小冰雹", 99: "雷暴伴大冰雹",
    }

    dates = data.get("daily", {}).get("time", [])
    codes = data.get("daily", {}).get("weather_code", [])
    tmax = data.get("daily", {}).get("temperature_2m_max", [])
    tmin = data.get("daily", {}).get("temperature_2m_min", [])
    wind = data.get("daily", {}).get("wind_speed_10m_max", [])

    forecast = []
    for i in range(len(dates)):
        forecast.append({
            "date": dates[i],
            "weather": wmo.get(codes[i], f"代码{codes[i]}"),
            "temp_max": tmax[i] if i < len(tmax) else None,
            "temp_min": tmin[i] if i < len(tmin) else None,
            "wind_max_kmh": wind[i] if i < len(wind) else None,
        })

    return json.dumps({"city": city, "days": days, "forecast": forecast}, ensure_ascii=False)


# ---------- 工具注册表: 给 agent 用的工具描述(对应 Function Calling 的 schema) ----------
# 每个工具: {type, function: {name, description, parameters}}
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市未来几天的天气预报。当用户询问某地天气、或规划行程需要知道天气时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名, 如'北京'、'唐山'"},
                    "days": {"type": "integer", "description": "预报天数, 1~7, 默认3"}
                },
                "required": ["city"],
                "additionalProperties": False,
            },
        },
    },
]


# 工具调用分发表: 名字 -> 实际函数
TOOL_FUNCTIONS = {
    "get_weather": get_weather,
}


# 简单自测
if __name__ == "__main__":
    print(get_weather("北京", 3))
    print(get_weather("火星", 3))
