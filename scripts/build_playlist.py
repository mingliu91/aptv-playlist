import re
from pathlib import Path
from urllib.request import Request, urlopen

INPUT = Path("archive/iptv_collection.m3u")
OUTPUT = Path("playlist.m3u")

# 独立央视源
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
        "international",
        "global",
        "world",
    ]):
        return "国际"

    # 城市
    if any(x in name for x in CITY_KEYWORDS):
        return "城市"

    # 省级卫视
    if any(x in name for x in SATELLITE):
        return "卫视"

    return None


def parse_m3u_text(text):
    lines = text.splitlines()
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


def parse_m3u():
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)

    text = INPUT.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    return parse_m3u_text(text)


def download_cctv():
    print("正在下载独立央视源...")

    request = Request(
        CCTV_SOURCE,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urlopen(request, timeout=60) as response:
        text = response.read().decode(
            "utf-8",
            errors="ignore"
        )

    channels = parse_m3u_text(text)

    print("央视源读取:", len(channels), "条")

    return channels


def is_cctv(name):
    return bool(
        re.search(
            r"\bCCTV[- ]?(1[0-7]|[1-9])\b",
            name,
            re.I
        )
    )


def main():

    channels = parse_m3u()

    result = {group: [] for group in GROUPS}

    seen = set()

    # ==========================
    # 处理 archive
    # ==========================

    for ch in channels:

        name = ch["name"]

        # 黑名单
        if any(
            word.lower() in name.lower()
            for word in BLACKLIST
        ):
            continue

        # 央视改用独立央视源
        if is_cctv(name):
            continue

        group = get_group(name)

        if not group:
            continue

        # 名称去重
        key = re.sub(
            r"[^a-zA-Z0-9\u4e00-\u9fff]",
            "",
            name
        ).lower()

        if key in seen:
            continue

        seen.add(key)

        result[group].append(ch)

    # ==========================
    # 加入独立央视源
    # ==========================

    cctv_channels = download_cctv()

    cctv_result = []
    cctv_seen = set()

    for ch in cctv_channels:

        name = ch["name"]

        if not is_cctv(name):
            continue

        match = re.search(
            r"CCTV[- ]?(1[0-7]|[1-9])",
            name,
            re.I
        )

        if not match:
            continue

        number = match.group(1)
        cctv_name = f"CCTV-{number}"

        if cctv_name in cctv_seen:
            continue

        cctv_seen.add(cctv_name)

        info = ch["info"]

        info = re.sub(
            r'group-title="[^"]*"',
            'group-title="央视"',
            info
        )

        if 'group-title=' not in info:
            info = info.replace(
                "#EXTINF:-1",
                '#EXTINF:-1 group-title="央视"'
            )

        if "," in info:
            info = info.split(",", 1)[0] + "," + cctv_name

        cctv_result.append({
            "info": info,
            "name": cctv_name,
            "url": ch["url"],
        })

    # 央视放在第一组
    result["央视"] = cctv_result

    # ==========================
    # 生成最终 playlist
    # ==========================

    output = [
        "#EXTM3U",
        "#EXT-X-APP APTV",
        "#EXT-X-APTV-TYPE remote",
    ]

    for group in GROUPS:

        for ch in result[group]:

            info = ch["info"]

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

    total = sum(
        len(v)
        for v in result.values()
    )

    print()
    print("原始频道:", len(channels))
    print("最终频道:", total)

    for group in GROUPS:
        print(group, len(result[group]))


if __name__ == "__main__":
    main()
