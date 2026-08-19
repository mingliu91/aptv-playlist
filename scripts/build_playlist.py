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


if name == "__main__":
    main()
