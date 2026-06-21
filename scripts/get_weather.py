"""
天气查询模块
使用 wttr.in（免费，无需 API Key）获取天气信息
"""
import json
import urllib.request
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from feishu_push import send_card


# 城市中英文映射
CITY_MAP = {
    "上海": "Shanghai",
    "武汉": "Wuhan",
    "北京": "Beijing",
    "深圳": "Shenzhen",
    "杭州": "Hangzhou",
    "广州": "Guangzhou",
}


def get_weather(city_cn="上海"):
    """从 wttr.in 获取天气数据"""
    city_en = CITY_MAP.get(city_cn, city_cn)
    url = f"https://wttr.in/{city_en}?format=j1"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/7.88"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data


def format_weather(data, city_cn="上海"):
    """将 wttr.in 数据格式化为飞书 Markdown"""
    current = data["current_condition"][0]
    today = data["weather"][0]
    tomorrow = data["weather"][1] if len(data["weather"]) > 1 else None

    temp = current["temp_C"]
    feels = current["FeelsLikeC"]
    humidity = current["humidity"]
    desc = current["lang_zh"][0]["value"] if current.get("lang_zh") else current["weatherDesc"][0]["value"]
    wind_speed = current["windspeedKmph"]
    wind_dir = current["winddir16Point"]

    lines = [
        f"**{city_cn}今日天气**",
        f"当前：{desc}，{temp}°C（体感 {feels}°C）",
        f"温度范围：{today['mintempC']}°C ~ {today['maxtempC']}°C",
        f"湿度：{humidity}% 风力：{wind_dir} {wind_speed}km/h",
        "",
    ]

    # 日出日落
    astro = today.get("astronomy", [{}])[0]
    if astro:
        lines.append(f"日出 {astro.get('sunrise', '?')} 日落 {astro.get('sunset', '?')}")
        lines.append("")

    # 明天预报
    if tomorrow:
        tmr_desc = ""
        for h in tomorrow.get("hourly", []):
            if h.get("lang_zh"):
                tmr_desc = h["lang_zh"][0]["value"]
                break
        lines.append(f"**明日预报**")
        if tmr_desc:
            lines.append(f"{tmr_desc}，{tomorrow['mintempC']}°C ~ {tomorrow['maxtempC']}°C")
        else:
            lines.append(f"{tomorrow['mintempC']}°C ~ {tomorrow['maxtempC']}°C")

    # 穿衣/带伞建议
    max_temp = int(today["maxtempC"])
    min_temp = int(today["mintempC"])
    lines.append("")
    if max_temp < 10:
        lines.append("[!] 天气较冷，注意保暖")
    elif max_temp > 35:
        lines.append("[!] 高温天气，注意防暑")

    # 检查是否有雨
    has_rain = False
    for h in today.get("hourly", []):
        chance = int(h.get("chanceofrain", "0"))
        if chance > 50:
            has_rain = True
            break
    if has_rain:
        lines.append("[!] 今天有雨，记得带伞")

    return "\n".join(lines)


if __name__ == "__main__":
    city = "上海"
    dry_run = False
    for arg in sys.argv[1:]:
        if arg == "--dry-run":
            dry_run = True
        else:
            city = arg

    print(f"查询 {city} 天气...")
    data = get_weather(city)
    msg = format_weather(data, city)
    print(msg)

    if not dry_run:
        print("\n推送到飞书...")
        result = send_card(f"☀️ {city}今日天气", msg)
        print(json.dumps(result, ensure_ascii=False))
    else:
        print("\n(--dry-run 模式，未推送)")
