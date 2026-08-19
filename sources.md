
# APTV IPTV 源资料库

这是个人 APTV IPTV 源整理项目。

## 第一优先级：完整大源

名称：cs3306 IPTV-Sources

原始地址：

https://raw.githubusercontent.com/cs3306/IPTV-Sources/main/data/output/iptv_collection.m3u

特点：

- 大量央视频道
- 全国省级卫视
- 大量地方台
- 港澳台及其他地区频道
- 部分频道提供备用播放地址
- 适合作为原始资料库
- 暂时不做精简

## 第二优先级：Kimentanm APTV

https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u

特点：

- APTV 格式
- CCTV
- 省级卫视
- 港澳台
- 部分国际频道
- 适合作为国内核心频道备用源

## 第三优先级：suxuang myIPTV IPv4

https://raw.githubusercontent.com/suxuang/myIPTV/main/ipv4.m3u

特点：

- IPv4
- 频道数量较大
- 可作为备用来源
- 部分频道与其他源重复

## 第四优先级：ChinaIPTV

https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/cnTV_AutoUpdate.m3u8

特点：

- 自动更新
- 国内频道
- 可作为国内频道备用源

## 第五优先级：Guovin iptv-api

https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u

特点：

- 自动采集
- 自动检测
- 自动测速
- 自动去重
- 多源聚合

## 国际频道备用

iptv-org：

https://iptv-org.github.io/iptv/index.m3u

## 项目目标

最终 APTV 使用一个统一订阅地址：

央视
→ 卫视
→ 主要城市
→ 港澳台
→ 日本
→ 韩国
→ 美国
→ 欧洲
→ 国际

最终版本重点：

1. CCTV 完整
2. 主流省级卫视完整
3. 主要城市电视台
4. 港澳台主流频道
5. 日本、韩国主流频道
6. 美国及西方主流新闻频道
7. 同频道保留多个可用线路
8. 自动更新
9. 自动去重
10. 尽量优先低延迟线路

原始大源不删除，作为长期备用资料库。
## 第六优先级：live.hacks.tools 央视源

央视专用备用源：

https://live.hacks.tools/tv/ipv4/categories/央视频道.m3u

特点：

- 央视专用
- IPv4
- 可作为 CCTV 备用线路
- 与其他国内大源互补
- 暂不作为唯一核心源

## APTV 代理/转换地址

以下地址本质上是已有源的代理或包装，不作为独立源统计。

### Kimentanm APTV 代理

https://add.aptv.app/https://gh.aptv.app/https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u

实际来源：

https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u

说明：

- 属于 Kimentanm 源的代理/转换地址
- 与第二优先级源重复
- 如果原始 GitHub 地址正常，优先使用原始地址

### suxuang APTV 代理

https://gh.aptv.app/https://raw.githubusercontent.com/suxuang/myIPTV/main/ipv4.m3u

实际来源：

https://raw.githubusercontent.com/suxuang/myIPTV/main/ipv4.m3u

说明：

- 属于 suxuang/myIPTV 的代理地址
- 与第三优先级源重复
- 原始 GitHub 地址正常时优先使用原始地址

## 源管理原则

1. 原始源和代理源分开记录。
2. 代理地址不作为独立频道来源计算。
3. 同一个频道尽量保留多个不同服务器线路。
4. CCTV 等核心频道优先保留备用线路。
5. 不因为某一个源失效而删除整个频道。
6. 最终 APTV 播放列表以实际可用性为准。
7. 深圳实际播放延迟优先于其他地区服务器的测速结果。
8. IPv4 与 IPv6 根据实际网络环境分别测试。
9. 原始大源长期保存，不轻易删除。
10. 最终精简版只保留真正有价值的频道。

## 最终筛选原则

### 必须保留

- CCTV 全系列
- CCTV 高清/4K 等高质量版本
- 主流省级卫视
- 主要城市电视台
- 港澳台主流频道
- 日本主流频道
- 韩国主流频道
- 美国主流新闻/媒体频道
- 英国及欧洲主流新闻频道
- 国际主流新闻频道

### 原则上删除

- 重复频道
- 县级及大量冷门地方台
- 购物频道
- 教育培训频道
- 明显 VOD/点播节目
- 春晚/晚会等历史录像
- 无法长期播放的明显失效线路

## 当前项目结构

原始资料库：
cs3306 完整大源

国内备用：
Kimentanm
suxuang
ChinaIPTV
Guovin

央视备用：
live.hacks.tools

国际备用：
iptv-org

最终目标：

一个 APTV 订阅地址
→ 自动更新
→ 自动去重
→ 多线路
→ 核心频道优先
→ 深圳实际播放体验优先
→ 原始源长期保存
