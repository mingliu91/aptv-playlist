
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
