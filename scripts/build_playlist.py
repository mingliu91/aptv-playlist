import re
from pathlib import Path
from urllib.request import Request, urlopen

INPUT = Path("archive/iptv_collection.m3u")
OUTPUT = Path("playlist.m3u")

CCTV_SOURCE = "https://raw.githubusercontent.com/best-fan/iptv-sources/main/cn_cctv.m3u8"
SATELLITE_SOURCE = "https://raw.githubusercontent.com/best-fan/iptv-sources/main/cn_province_status.m3u8"

GROUPS = ["央视", "卫视", "城市", "港澳台", "日本", "韩国", "美国", "欧洲", "国际"]

BLACKLIST = ["购物", "教育", "培训", "课堂", "少儿", "春晚", "回放", "重播", "点播", "录像", "历史", "测试", "广告", "宣传片", "MV"]

CITY_KEYWORDS = ["北京", "上海", "广州", "深圳", "成都", "重庆", "杭州", "南京", "武汉", "西安", "天津"]

SATELLITE = [
    "湖南卫视", "浙江卫视", "江苏卫视", "东方卫视", "北京卫视",
    "广东卫视", "深圳卫视", "四川卫视", "安徽卫视", "山东卫视",
    "河南卫视", "湖北卫视", "江西卫视", "福建东南卫视", "广西卫视",
    "云南卫视", "贵州卫视", "辽宁卫视", "黑龙江卫视", "吉林卫视",
    "河北卫视", "山西卫视", "陕西卫视", "甘肃卫视", "宁夏卫视",
    "新疆卫视", "内蒙古卫视", "青海卫视", "海南卫视",
]

def download_text(url):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="ignore")

def parse_m3u_text(text):
    lines = text.splitlines()
    channels = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            info = lines[i]
            name = info.split(",", 1)[1].strip() if "," in info else "未知频道"
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url.startswith("http"):
                    channels.append({"info": info, "name": name, "url": url})
            i += 2
        else:
            i += 1
    return channels

def parse_archive():
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)
    return parse_m3u_text(INPUT.read_text(encoding="utf-8", errors="ignore"))

def normalize_name(name):
    return re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]", "", name).lower()

def get_response_time(info):
    match = re.search(r'response-time="(\d+)ms"', info, re.I)
    return int(match.group(1)) if match else 999999

def is_cctv(name):
    return bool(re.search(r"\bCCTV[- ]?(1[0-7]|[1-9])\b", name, re.I))

def normalize_cctv(name):
    match = re.search(r"CCTV[- ]?(1[0-7]|[1-9])", name, re.I)
    return f"CCTV-{match.group(1)}" if match else None

def get_group(name):
    n = name.lower()
    if is_cctv(name) or any(x in name for x in ["央视", "CGTN"]):
        return "央视"
    if any(x in name for x in ["香港", "翡翠台", "明珠台", "凤凰", "TVB", "澳门", "澳视", "台湾", "台视", "中视", "华视", "民视"]):
        return "港澳台"
    if any(x in n for x in ["nhk", "tbs", "fuji", "ntv", "tv asahi", "abema", "japan"]):
        return "日本"
    if any(x in n for x in ["kbs", "mbc", "sbs", "jtbc", "tvn", "korea"]):
        return "韩国"
    if any(x in n for x in ["cnn", "fox news", "cnbc", "bloomberg", "abc news", "nbc", "cbs", "msnbc", "usa"]):
        return "美国"
    if any(x in n for x in ["bbc", "sky news", "dw", "france 24", "euronews", "itv", "channel 4", "uk"]):
        return "欧洲"
    if any(x in n for x in ["al jazeera", "international", "global", "world"]):
        return "国际"
    if any(x in name for x in CITY_KEYWORDS):
        return "城市"
    if any(x in name for x in SATELLITE):
        return "卫视"
    return None

def clean_info(info, group, name=None):
    info = re.sub(r'group-title="[^"]*"', f'group-title="{group}"', info)
    if 'group-title=' not in info:
        info = info.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{group}"')
    if name and "," in info:
        info = info.split(",", 1)[0] + "," + name
    return info

def choose_best(candidates):
    return sorted(candidates, key=lambda x: (get_response_time(x["info"]), len(x["url"])))[0]

def build_cctv():
    print("读取央视专用源...")
    channels = parse_m3u_text(download_text(CCTV_SOURCE))
    result, seen = [], set()
    for ch in channels:
        name = normalize_cctv(ch["name"])
        if not name or name in seen:
            continue
        seen.add(name)
        ch["info"] = clean_info(ch["info"], "央视", name)
        ch["name"] = name
        result.append(ch)
    result.sort(key=lambda x: int(re.search(r"\d+", x["name"]).group()))
    return result

def build_satellite():
    print("读取卫视专用源...")
    channels = parse_m3u_text(download_text(SATELLITE_SOURCE))
    candidates = {}
    for ch in channels:
        name = ch["name"]
        if not any(x in name for x in SATELLITE):
            continue
        candidates.setdefault(normalize_name(name), []).append(ch)
    result = []
    for items in candidates.values():
        best = choose_best(items)
        best["info"] = clean_info(best["info"], "卫视")
        result.append(best)
        print(f"卫视 {best['name']}: {len(items)} 个候选 -> {get_response_time(best['info'])}ms")
    result.sort(key=lambda x: x["name"])
    return result

def build_archive_channels():
    print("读取综合源...")
    channels = parse_archive()
    candidates = {group: {} for group in GROUPS}
    for ch in channels:
        name = ch["name"]
        if any(word.lower() in name.lower() for word in BLACKLIST):
            continue
        if is_cctv(name):
            continue
        group = get_group(name)
        if not group or group == "卫视":
            continue
        key = normalize_name(name)
        if key:
            candidates[group].setdefault(key, []).append(ch)
    result = {group: [] for group in GROUPS}
    for group in GROUPS:
        if group == "央视":
            continue
        for items in candidates[group].values():
            best = choose_best(items)
            best["info"] = clean_info(best["info"], group)
            result[group].append(best)
    return result

def main():
    print("=" * 50)
    print("APTV 最终版 IPTV Playlist Builder")
    print("=" * 50)

    result = {group: [] for group in GROUPS}
    result["央视"] = build_cctv()
    result["卫视"] = build_satellite()
    archive_result = build_archive_channels()

    for group in GROUPS:
        if group not in ["央视", "卫视"]:
            result[group] = archive_result[group]

    for group in GROUPS:
        seen, cleaned = set(), []
        for ch in result[group]:
            key = normalize_name(ch["name"])
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(ch)
        result[group] = cleaned

    output = ["#EXTM3U", "#EXT-X-APP APTV", "#EXT-X-APTV-TYPE remote"]
    for group in GROUPS:
        for ch in result[group]:
            output.append(clean_info(ch["info"], group))
            output.append(ch["url"])

    OUTPUT.write_text("\n".join(output) + "\n", encoding="utf-8")

    print("\n" + "=" * 50)
    print("最终结果")
    print("=" * 50)
    total = 0
    for group in GROUPS:
        count = len(result[group])
        total += count
        print(f"{group}: {count}")
    print("-" * 50)
    print(f"最终频道: {total}")
    print(f"Playlist: {OUTPUT}")
    print("=" * 50)

if __name__ == "__main__":
    main()
