# OpenSkin API 本地验证报告

测试日期：2026-10-28 20:39 PDT（America/Los_Angeles），对应
2026-10-29 03:39 UTC。此次为单次短时验证，不代表长期可用性。

## 范围与证据

使用 Python 3.11.15 与 Windows curl 访问公开 v1 Pricing API，无需 API Key。
未调用 AWS、交易、库存或个人账号接口；未请求个体 Float/Pattern 接口。
源响应包含的嵌套 variant 字段原样保存在本地，不做个体 Pattern 分析。

脚本：`src/validate_openskin.py`；
[机器可读汇总](openskin_validation_summary.json) 包含请求 URL、状态、耗时、
响应体字节数、SHA-256，以及全量字段出现次数、类型和 null 数。
原始响应、响应头和本次 report.json 保存在
`data/raw/openskin/20261029T033914Z/`，由 .gitignore 排除。

参考：[官方 v1 文档](https://openskin.dev/)、
[OpenAPI](https://openskin.dev/openapi.json)。以下统计来自本地实际响应。

## 接口可用性

共执行 16 次 API 请求，未做压力测试或自动重试：

| 请求 | HTTP | 结果 |
|---|---:|---|
| api.openskin.dev /health | 200 | 五个来源 up；items=38,043 |
| api-v2.openskin.dev /health | 503 | degraded；来源更新停留于 8–9 月，items=37,705 |
| /v1/items 首尾页及两个布尔筛选 | 200 × 4 | limit=500；第 77 页返回 43 条 |
| /v1/prices 单品 | 200 | AK-47 Redline Field-Tested |
| /v1/prices/{market} | 200 × 5 | 五个市场单品接口均成功 |
| POST /v1/prices/batch | 200 | 四个不同名称全部返回 |
| 单品缺少 item | 400 | JSON error |
| 不存在商品名称 | 404 | JSON error |
| /v1/prices/all | 200 | 完整快照成功解析 |

官网示例使用 api.openskin.dev，OpenAPI server 却列出 api-v2.openskin.dev。
本次采用实测正常的前者；后者的 503 不代表主 API 故障。
Python urllib 默认请求文档收到 403，而 curl 成功；未确定是客户端、请求头
还是网络路径差异。尚未验证生产采集所需的原生 Python HTTP 客户端。

## 实际返回结构与字段

| 接口 | 结构 |
|---|---|
| items | data 数组；page、limit、total |
| 单品综合价格 | item、icon_url、**prices.{market}**、links、lowest_ask、metrics、updated_at |
| batch | data 名称映射、results 数组、count、updated_at |
| bulk | data 名称映射、count、updated_at；市场直接位于 data[name].{market} |
| 单市场价格 | item、marketplace 与平铺的报价/统计字段 |

目录首 500 条观察到 name、type、weapon、skin、exterior、rarity、
is_stattrak、is_souvenir、icon_url，部分记录有 pattern。
skin、exterior 等字段可能直接缺失。目录 pattern 的含义未验证，不参与建模。

全量快照的实际字段：

| 市场 | 字段 |
|---|---|
| Steam | ask、bid、median、volume_24h、buy_order_count、sell_order_count、liquidity_score、currency、updated_at |
| Skinport | ask、ask_volume、mean、median、max_ask、suggested_price、liquidity_score、patterns、currency、updated_at |
| BUFF163 / YouPin | ask、ask_volume、bid、bid_volume、native_currency、patterns、currency、updated_at |
| CSFloat | ask、sell_order_count、highest_bid、bid_volume、base_price、paint_seed、patterns、currency、updated_at |

市场对象可能缺失；对象存在也可能没有有效报价。数值存在 int/float/null，
不能根据一个样本固定类型。Skinport 未提供 bid，不能填为 0。
bulk 的所有市场 currency 均为 USD；部分 BUFF/YouPin 对象额外保留 CNY 原始报价。
单品的 metrics 与 bulk 中直接位于市场对象下的 liquidity_score 路径不同。
单市场 Steam/Skinport 样本没有 currency，不能假定所有接口字段完全相同。
详尽字段出现次数与类型见 JSON 汇总的 bulk.field_profile。

## 商品与变体数量

目录 total、health items、bulk count、bulk 唯一名称数均为 **38,043**。
这代表本次 OpenSkin 跟踪目录，不代表 CS2 的全部理论可能变体。
统计保留完整名称，没有合并磨损、StatTrak、Souvenir 等变体。

| 分类方法 | StatTrak | Souvenir |
|---|---:|---:|
| 目录布尔筛选返回 total | 5,087 | 3,137 |
| bulk 名称匹配 | 5,088 | 3,532 |

名称匹配剩余 regular 为 29,423，但它不是经过元数据核实的普通皮肤数。
bulk 中有 `StatTrak™ Swap Tool`，说明名称关键词不等于皮肤变体标记；
该例不能证明已逐条解释 StatTrak 差额。Souvenir 差额 395 的原因尚未验证。
补充联网查询未获批准，未执行，保留为后续元数据同步验收项。

| 名称末尾磨损类别 | 数量 |
|---|---:|
| Factory New | 3,657 |
| Minimal Wear | 3,631 |
| Field-Tested | 3,337 |
| Well-Worn | 2,996 |
| Battle-Scarred | 2,919 |
| 无上述后缀 | 21,503 |

磨损与 StatTrak/Souvenir 是交叉分类，不能相加。无磨损后缀不等于无效商品。
目录仅下载首尾页共 543 条元数据，未下载中间页，因此未验证全目录分页
无重复或逐条标签。batch 测试普通、StatTrak、Souvenir、Doppler 四个名称，
全部出现在 bulk；未测试同名不同 Pattern 请求，也未分析其价格。

## 市场覆盖情况

分母统一为 38,043 个唯一名称；有效 ask/bid 要求为有限正数。
CSFloat bid 使用 highest_bid。没有按时间过滤，覆盖率包含陈旧报价。

| 市场 | 对象存在 | 有效 ask | ask 覆盖率 | 有效 bid | ask/bid 均有效 |
|---|---:|---:|---:|---:|---:|
| Steam | 37,354 | 32,750 | 86.09% | 35,302 | 30,698 |
| Skinport | 24,925 | 24,925 | 65.52% | 0（未提供） | 0 |
| BUFF163 | 25,573 | 24,869 | 65.37% | 17,507 | 17,384 |
| YouPin | 25,485 | 24,660 | 64.82% | 17,386 | 17,287 |
| CSFloat | 28,482 | 28,302 | 74.39% | 25,664 | 25,499 |

覆盖集合不同，不能相加；缺失市场不等于零价格。来源健康检查为 up，
但部分报价的 updated_at 最早为 2026 年 6–7 月。商品外层 updated_at
不能代替各市场时间，后续需按来源设置新鲜度阈值。

## 响应大小与耗时

字节数为响应体，不含 HTTP 头、TLS 与协议开销。请求发送 Accept-Encoding: gzip，
保存压缩响应体，再由 Python 解压计数。

| 请求 | 下载字节 | 解压 JSON 字节 | 总耗时 |
|---|---:|---:|---:|
| health | 183 | 391 | 0.643 s |
| 目录首 500 条 | 26,049 | 223,790 | 0.307 s |
| 单品综合价格 | 1,140 | 2,436 | 7.219 s |
| batch 四项 | 2,562 | 21,302 | 0.204 s |
| bulk | **6,916,678** | **62,982,495** | **1.743 s** |

bulk 约 **6.60 MiB gzip / 60.06 MiB JSON**，大小比约 9.11 倍，
Cache-Control 为 public, max-age=300。单次耗时不代表平均值或 P95。
按同样大小保存每小时快照，每 24 次约 158.31 MiB gzip；仅为体积估算，
不是 AWS 费用或内存需求估算。JSON 对象解析后的内存占用尚未测量。

## 验证结果与下一步

- 已执行 `python -m unittest discover -s test -v`：6 项通过。
  覆盖有效价格、缺失/null、独立名称、数量不一致、gzip 字节数、404 与 429 停止行为。
- 已离线重新解析完整原始 bulk，重算统计，与报告核对；
  校验 16 个 HTTP 结果、四个 batch 名称、目录/快照数量，全部通过。
- 已执行 CLI `--help`。最终脚本增加结果验收与请求开始时间记录修正后，
  未重复整轮联网测试。本次 JSON 的 requested_at_utc 是请求返回后的记录时间；
  用 started_at_utc / finished_at_utc 定位整轮窗口。
- 下一步实现本地 Bronze collector：单次 gzip 下载、UTC 采集元数据、
  幂等落盘、失败处理、数量/schema 检查；另行完成元数据全分页与标签差异核对。
- 历史 API、本地转 Parquet、AWS 资源、Lambda 内存和运行时配置均未验证或实施。
