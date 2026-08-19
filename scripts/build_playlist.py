import re
import urllib.request
from pathlib import Path

OUTPUT = Path("playlist.m3u")

SOURCES = [
    "https://raw.githubusercontent.com/cs3306/IPTV-Sources/main/data/output/iptv_collection.m3u",
    "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u",
    "https://raw.githubusercontent.com/suxuang/myIPTV/main/ipv4.m3u",
    "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/cnTV_AutoUpdate.m3u8",
    "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u",
]

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
    "广告",
    "宣传片",
    "点播",
    "回放",
    "录像",
    "历史",
    "春晚",
    "测试",
    "MV",
    "电影",
    "电视剧",
    "VOD",
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

def download(url):
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode(
                "utf-8",
                errors="ignore"
            )

    except Exception as e:
        print("源下载失败:", url)
        print(e)
        return ""


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

    if "央视" in name or "cgtn" in n:
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

    all_channels = []

    print("开始下载 IPTV 源...")

    for source in SOURCES:

        print("下载:", source)

        text = download(source)

        if not text:
            continue

        channels = parse_m3u(text)

        print("发现频道:", len(channels))

        all_channels.extend(channels)

    print("全部候选频道:", len(all_channels))

    grouped = {
        group: []
        for group in GROUPS
    }

    # 同频道聚合
    candidates = {}

    for channel in all_channels:

        name = normalize_name(channel["name"])

        if not name:
            continue

        if any(
            word.lower() in name.lower()
            for word in BLACKLIST
        ):
            continue

        group = get_group(name)

        if not group:
            continue

        key = re.sub(
            r"[^a-zA-Z0-9\u4e00-\u9fff]",
            "",
            name
        ).lower()

        if key not in candidates:
            candidates[key] = {
                "name": name,
                "group": group,
                "channels": []
            }

        candidates[key]["channels"].append(channel)

    # 每个频道选择第一个候选地址
    for item in candidates.values():

        grouped[item["group"]].append(
            item["channels"][0]
        )

    output = [
        '#EXTM3U x-tvg-url="https://epg.aptv.app/pp.xml.gz,https://epg.aptv.app/xml"',
        "#EXT-X-APP APTV",
        "#EXT-X-APTV-TYPE remote",
    ]

    for group in GROUPS:

        print(
            group,
            len(grouped[group])
        )

        for channel in grouped[group]:

            info = channel["info"]

            info = re.sub(
                r'group-title="[^"]*"',
                f'group-title="{group}"',
                info
            )

            if "group-title=" not in info:

                info = info.replace(
                    "#EXTINF:-1",
                    f'#EXTINF:-1 group-title="{group}"'
                )

            output.append(info)
            output.append(channel["url"])

    OUTPUT.write_text(
        "\n".join(output) + "\n",
        encoding="utf-8"
    )

    print()
    print("最终频道:", sum(
        len(v) for v in grouped.values()
    ))

    print("生成:", OUTPUT)


if __name__ == "__main__":
    main()
