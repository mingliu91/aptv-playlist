import re
from pathlib import Path

INPUT = Path("archive/iptv_collection.m3u")
OUTPUT = Path("playlist.m3u")

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

SATELLITE = [
    "湖南卫视",
    "浙江卫视",
    "江苏卫视",
    "东方卫视",
    "北京卫视",
    "广东卫视",
    "深圳卫视",
    "四川卫视",
    "重庆卫视",
    "安徽卫视",
    "山东卫视",
    "河南卫视",
    "湖北卫视",
    "江西卫视",
    "东南卫视",
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


def parse_m3u(text):

    lines = text.splitlines()
    result = []

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
                    result.append({
                        "info": info,
                        "name": name,
                        "url": url
                    })

            i += 2

        else:
            i += 1

    return result


def normalize_name(name):

    name = name.strip()

    replacements = {
        "CCTV ": "CCTV-",
        "CCTV": "CCTV",
        "中央电视台": "CCTV",
        "中央": "CCTV",
    }

    for a, b in replacements.items():
        name = name.replace(a, b)

    name = re.sub(r"\s+", "", name)

    return name


def get_group(name):

    n = name.lower()

    # 央视
    if re.search(r"cctv[- ]?\d+", name, re.I):
        return "央视"

    if "央视" in name:
        return "央视"

    # 港澳台
    if any(x in name for x in [
        "香港",
        "翡翠台",
        "明珠台",
        "TVB",
        "凤凰",
        "澳门",
        "澳视",
        "台湾",
        "台视",
        "中视",
        "华视",
        "民视",
        "三立",
        "东森",
        "TVBS",
    ]):
        return "港澳台"

    # 日本
    if any(x in n for x in [
        "nhk",
        "tbs",
        "fuji",
        "ntv",
        "tv asahi",
        "japan",
        "ann",
        "jnn",
    ]):
        return "日本"

    # 韩国
    if any(x in n for x in [
        "kbs",
        "mbc",
        "sbs",
        "jtbc",
        "tvn",
        "korea",
        "ytn",
    ]):
        return "韩国"

    # 美国
    if any(x in n for x in [
        "cnn",
        "fox news",
        "cnbc",
        "bloomberg",
        "abc news",
        "nbc",
        "cbs",
        "msnbc",
        "usa",
    ]):
        return "美国"

    # 欧洲
    if any(x in n for x in [
        "bbc",
        "sky news",
        "dw",
        "france 24",
        "euronews",
        "itv",
        "channel 4",
        "uk",
    ]):
        return "欧洲"

    # 国际
    if any(x in n for x in [
        "al jazeera",
        "international",
        "global",
        "world",
    ]):
        return "国际"

    # 城市
    if any(x in name for x in CITY_KEYWORDS):
        return "城市"

    # 卫视
    if any(x in name for x in SATELLITE):
        return "卫视"

    return None


def main():

    text = INPUT.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    channels = parse_m3u(text)

    print("原始频道:", len(channels))

    grouped = {
        group: []
        for group in GROUPS
    }

    seen = set()

    for channel in channels:

        name = normalize_name(
            channel["name"]
        )

        if not name:
            continue

        # 黑名单过滤
        if any(
            word.lower() in name.lower()
            for word in BLACKLIST
        ):
            continue

        group = get_group(name)

        if not group:
            continue

        # 简单去重
        key = (
            group,
            re.sub(
                r"[^a-zA-Z0-9\u4e00-\u9fff]",
                "",
                name
            ).lower()
        )

        if key in seen:
            continue

        seen.add(key)

        grouped[group].append({
            "info": channel["info"],
            "name": name,
            "url": channel["url"]
        })

    output = [
        '#EXTM3U x-tvg-url="https://epg.aptv.app/pp.xml.gz,https://epg.aptv.app/xml"',
        "#EXT-X-APP APTV",
        "#EXT-X-APTV-TYPE remote",
    ]

    total = 0

    print()
    print("频道统计:")

    for group in GROUPS:

        count = len(grouped[group])

        print(
            f"{group}: {count}"
        )

        for channel in grouped[group]:

            info = channel["info"]

            # 修改已有 group-title
            info = re.sub(
                r'group-title="[^"]*"',
                f'group-title="{group}"',
                info
            )

            # 没有 group-title 就添加
            if "group-title=" not in info:

                info = info.replace(
                    "#EXTINF:-1",
                    f'#EXTINF:-1 group-title="{group}"'
                )

            output.append(info)
            output.append(channel["url"])

            total += 1

    OUTPUT.write_text(
        "\n".join(output) + "\n",
        encoding="utf-8"
    )

    print()
    print("最终频道:", total)
    print("输出文件:", OUTPUT)


if __name__ == "__main__":
    main()
