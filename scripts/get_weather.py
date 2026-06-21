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
    """从 wttr.in 获取天气数据（中文）"""
    city_en = CITY_MAP.get(city_cn, city_cn)
    url = f"https://wttr.in/{city_en}?format=j1&lang=zh"
    req = urllib.request.Request(url, headers={
        "User-Agent": "curl/7.88",
        "Accept-Language": "zh-CN,zh;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data


# 风向英文→中文映射
WIND_DIR_CN = {
    "N": "北风", "NNE": "北东北风", "NE": "东北风", "ENE": "东东北风",
    "E": "东风", "ESE": "东东南风", "SE": "东南风", "SSE": "南东南风",
    "S": "南风", "SSW": "南西南风", "SW": "西南风", "WSW": "西西南风",
    "W": "西风", "WNW": "西西北风", "NW": "西北风", "NNW": "北西北风",
}

# wttr.in 天气描述英文→中文映射
WEATHER_DESC_CN = {
    "sunny": "晴", "clear": "晴",
    "partly cloudy": "多云", "partlycloudy": "多云",
    "cloudy": "多云",
    "overcast": "阴",
    "mist": "薄雾", "fog": "雾", "freezing fog": "冻雾",
    "patchy rain possible": "局部可能有雨", "patchy rain nearby": "局部有雨",
    "patchy snow possible": "局部可能有雪", "patchy sleet possible": "局部可能有雨夹雪",
    "thundery outbreaks possible": "可能有雷阵雨",
    "blowing snow": "风吹雪", "blizzard": "暴风雪",
    "light drizzle": "小毛毛雨", "patchy light drizzle": "局部小毛毛雨",
    "freezing drizzle": "冻毛毛雨", "heavy freezing drizzle": "强冻毛毛雨",
    "patchy light rain": "局部小雨", "light rain": "小雨", "light rain shower": "小阵雨",
    "moderate rain at times": "时有中雨", "moderate rain": "中雨",
    "heavy rain at times": "时有大雨", "heavy rain": "大雨",
    "light freezing rain": "小冻雨", "moderate or heavy freezing rain": "中到大冻雨",
    "light sleet": "小雨夹雪", "moderate or heavy sleet": "中到大雨夹雪",
    "patchy light snow": "局部小雪", "light snow": "小雪", "light snow showers": "小阵雪",
    "patchy moderate snow": "局部中雪", "moderate snow": "中雪",
    "patchy heavy snow": "局部大雪", "heavy snow": "大雪",
    "ice pellets": "冰粒",
    "light rain shower": "小阵雨", "moderate or heavy rain shower": "中到大阵雨",
    "torrential rain shower": "暴雨",
    "light sleet showers": "小雨夹雪阵雨", "moderate or heavy sleet showers": "中到大雨夹雪阵雨",
    "light snow showers": "小阵雪", "moderate or heavy snow showers": "中到大阵雪",
    "patchy light snow showers": "局部小阵雪",
}


def translate_weather(desc_en):
    """将 wttr.in 英文天气描述翻译为中文"""
    key = desc_en.strip().lower()
    return WEATHER_DESC_CN.get(key, desc_en)


def format_weather(data, city_cn="上海"):
    """将 wttr.in 数据格式化为飞书 Markdown"""
    current = data["current_condition"][0]
    today = data["weather"][0]
    tomorrow = data["weather"][1] if len(data["weather"]) > 1 else None

    temp = current["temp_C"]
    feels = current["FeelsLikeC"]
    humidity = current["humidity"]
    raw_desc = current["weatherDesc"][0]["value"]
    desc = translate_weather(raw_desc)
    wind_speed = current["windspeedKmph"]
    wind_dir_en = current["winddir16Point"]
    wind_dir = WIND_DIR_CN.get(wind_dir_en, wind_dir_en)

    lines = [
        f"**{city_cn}今日天气**",
        f"当前：{desc}，{temp}°C（体感 {feels}°C）",
        f"温度范围：{today['mintempC']}°C ~ {today['maxtempC']}°C",
        f"湿度：{humidity}% {wind_dir} {wind_speed}km/h",
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
            if h.get("weatherDesc"):
                tmr_desc = translate_weather(h["weatherDesc"][0]["value"])
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
