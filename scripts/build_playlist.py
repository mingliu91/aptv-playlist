import re
from pathlib import Path

INPUT = Path("archive/iptv_collection.m3u")
OUTPUT = Path("playlist.m3u")
CCTV_SOURCE = "https://raw.githubusercontent.com/best-fan/iptv-sources/main/cn_cctv.m3u8"

# 最终频道分组顺序
GROUPS = [
    "央视",
    "卫视",
    "城市",
    "港澳台",
    "日本",
    "韩国",
    "美国",
    "欧洲",
    "国际",
]

# 明显不需要的内容
BLACKLIST = [
    "购物",
    "教育",
    "培训",
    "课堂",
    "少儿",
    "春晚",
    "回放",
    "重播",
    "点播",
    "录像",
    "历史",
    "测试",
    "广告",
    "宣传片",
    "MV",
]

# 城市台
CITY_KEYWORDS = [
    "北京",
    "上海",
    "广州",
    "深圳",
    "成都",
    "重庆",
    "杭州",
    "南京",
    "武汉",
    "西安",
    "天津",
]

def get_group(name):
    n = name.lower()

    # 央视
    if re.search(r"CCTV[- ]?\d+", name, re.I):
        return "央视"

    if any(x in name for x in ["央视", "CGTN"]):
        return "央视"

    # 港澳台
    if any(x in name for x in [
        "香港", "翡翠台", "明珠台", "凤凰",
        "TVB", "澳门", "澳视", "台湾",
        "台视", "中视", "华视", "民视",
    ]):
        return "港澳台"

    # 日本
    if any(x in n for x in [
        "nhk", "tbs", "fuji", "ntv",
        "tv asahi", "abema", "japan",
    ]):
        return "日本"

    # 韩国
    if any(x in n for x in [
        "kbs", "mbc", "sbs", "jtbc",
        "tvn", "korea",
    ]):
        return "韩国"

    # 美国
    if any(x in n for x in [
        "cnn", "fox news", "cnbc",
        "bloomberg", "abc news",
        "nbc", "cbs", "msnbc",
        "usa",
    ]):
        return "美国"

    # 欧洲
    if any(x in n for x in [
        "bbc", "sky news", "dw",
        "france 24", "euronews",
        "itv", "channel 4",
        "uk",
    ]):
        return "欧洲"

    # 国际
    if any(x in n for x in [
        "al jazeera",
        "cgtn",
        "international",
        "global",
        "world",
    ]):
        return "国际"

    # 城市
    if any(x in name for x in CITY_KEYWORDS):
        return "城市"

    # 省级卫视
    SATELLITE = [
        "湖南卫视",
        "浙江卫视",
        "江苏卫视",
        "东方卫视",
        "北京卫视",
        "广东卫视",
        "深圳卫视",
        "四川卫视",
        "安徽卫视",
        "山东卫视",
        "河南卫视",
        "湖北卫视",
        "江西卫视",
        "福建东南卫视",
        "广西卫视",
        "云南卫视",
        "贵州卫视",
        "辽宁卫视",
        "黑龙江卫视",
        "吉林卫视",
        "河北卫视",
        "山西卫视",
        "陕西卫视",
        "甘肃卫视",
        "宁夏卫视",
        "新疆卫视",
        "内蒙古卫视",
        "青海卫视",
        "海南卫视",
    ]

    if any(x in name for x in SATELLITE):
        return "卫视"

    return None


def parse_m3u():
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)

    lines = INPUT.read_text(
        encoding="utf-8",
        errors="ignore"
    ).splitlines()

    channels = []

    i = 0

    while i < len(lines):

        if lines[i].startswith("#EXTINF"):
            info = lines[i]

            if "," in info:
                name = info.split(",", 1)[1].strip()
            else:
                name = "未知频道"

            if i + 1 < len(lines):
                url = lines[i + 1].strip()

                if url.startswith("http"):
                    channels.append({
                        "info": info,
                        "name": name,
                        "url": url,
                    })

            i += 2
        else:
            i += 1

    return channels


def main():

    channels = parse_m3u()

    result = {group: [] for group in GROUPS}

    seen = set()

    for ch in channels:

        name = ch["name"]

        # 黑名单
        if any(word.lower() in name.lower()
               for word in BLACKLIST):
            continue
        
        # 央视改用独立央视源，跳过 archive 中的央视
        if re.search(r"CCTV[- ]?\d+", name, re.I):
            continue
       
        group = get_group(name)

        if not group:
            continue

        # 名称去重
        key = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]", "", name).lower()

        if key in seen:
            continue

        seen.add(key)

        result[group].append(ch)

    output = [
        "#EXTM3U",
        '#EXT-X-APP APTV',
        '#EXT-X-APTV-TYPE remote',
    ]

    for group in GROUPS:

        for ch in result[group]:

            info = ch["info"]

            # 强制设置分类
            info = re.sub(
                r'group-title="[^"]*"',
                f'group-title="{group}"',
                info
            )

            if 'group-title=' not in info:
                info = info.replace(
                    "#EXTINF:-1",
                    f'#EXTINF:-1 group-title="{group}"'
                )

            output.append(info)
            output.append(ch["url"])

    OUTPUT.write_text(
        "\n".join(output) + "\n",
        encoding="utf-8"
    )

    total = sum(len(v) for v in result.values())

    print("原始频道:", len(channels))
    print("最终频道:", total)

    for group in GROUPS:
        print(group, len(result[group]))


if __name__ == "__main__":
    main()
