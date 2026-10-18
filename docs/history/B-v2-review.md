# B 方案修订概念图：对照与复验

2026-10-16。当前展示版本为园区 B-campus-v2 与重点楼宇 B-building-v2r1，均待用户确认。它们是概念修订图，不是整屏最终基准或模型/网页成果。

## 旧版与修订版

左为旧概念，右为当前修订概念；保留完整图与原始比例。这轮主动调整了总览取景和内容，不能当作同相机的像素还原验收。

| 层级 | B 旧版 v1 | 当前修订版 |
| --- | --- | --- |
| 园区总览 | ![旧总览](/Users/xiabin/Documents/Codex/2026-10-15/new-chat-2/outputs/gaoxin-digital-building/design/concepts/B-campus-v1.png) | ![新总览v2](/Users/xiabin/Documents/Codex/2026-10-15/new-chat-2/outputs/gaoxin-digital-building/design/concepts/B-campus-v2.png) |
| 重点楼宇 | ![旧楼宇](/Users/xiabin/Documents/Codex/2026-10-15/new-chat-2/outputs/gaoxin-digital-building/design/concepts/B-building-v1.png) | ![新楼宇v2r1](/Users/xiabin/Documents/Codex/2026-10-15/new-chat-2/outputs/gaoxin-digital-building/design/concepts/B-building-v2r1.png) |

## 实际修正结果

| ID | 原差异 | 源修改与生成 | 当前复验结果 |
| --- | --- | --- | --- |
| C-01 | 第八栋身份不清 | 规划源补齐八个ID与相对排布；提示词要求独立实体与标签，拉远总览取景后生成v2 | 总览实际可核对A1/B1/B2三塔、A2/B3两侧、C1/C2/C3前排共八栋。仅关闭B概念的数量/可见性问题；不是对象拾取或绑定通过 |
| C-02 | 产业比例及其他属性由AI补出 | 规划源定义示范产业方向；提示词移除统计图与占比，不从旧图抄数 | 总览改为产业方向及示范产业定位，无未定义产业占比；核心园区与A1演示指标仍与规划对应 |
| C-03 | 字段单位与内容不匹配 | 提示词明确楼层数、已租/可租/空置面积与出租率；生成楼宇v2 | 最终图采用楼层数24层，未出现竣工年份或建筑高度误用；已租3.6万㎡、可租4.0万㎡、可租空置0.4万㎡，对应90%，与源一致 |
| C-04 | 跨图建筑与空间关系未固定 | 楼宇v2使用修订总览作A1身份参考；保留玻璃塔身、右立面古铜翼片、退台和屋顶花园 | 共同建筑特征更接近，但精确24层、立面分格、裙房几何及两相机可解释性未由同一三维模型验证，保持开放；不以AI图直接认证工程尺寸 |
| C-05 | 暖光偏重、高光层次偏强 | 总览与近景提示词改为中性柔和日光，降低金黄雾感与自发光要求 | 新图天空、玻璃和整体环境更中性；古铜翼片与局部窗面仍保留暖反射。此为视觉观察，最终光照仍待用户审美确认及网页复验 |
| C-06 | 入驻企业标题实际展示类别 | 规划源及提示词明确模块为入驻产业，不虚构公司名单 | 近景实际标题为入驻产业，下方为软件研发、光电子信息、企业服务；企业总数42家单独置于KPI |
| C-07 | 新近景v2中的比例条长度不准确 | 保留v2为中间稿，通过内置image_gen局部修订请求v2r1，仅移除空间利用比例条，改为出租率90%文字行 | 已查看v2r1，条形图已移除、比例与三项面积保持正确；主要建筑与画面构图基本延续。没有手绘修补图片 |

数值口径以 planning/project.json 为准。核心KPI图标仅作类别识别，不作为有刻度或图例的定量统计图；整屏设计时优先采用不暗示统计比例的图标。

## 局部再修订对照

| 中间稿：B-building-v2 | 当前：B-building-v2r1 |
| --- | --- |
| ![比例条中间稿](/Users/xiabin/Documents/Codex/2026-10-15/new-chat-2/outputs/gaoxin-digital-building/design/concepts/B-building-v2.png) | ![移除比例条后](/Users/xiabin/Documents/Codex/2026-10-15/new-chat-2/outputs/gaoxin-digital-building/design/concepts/B-building-v2r1.png) |

## 生成与留档

- 方式：内置image_gen.imagegen。总览延续B旧图，近景以修订总览与旧近景为输入，局部修订再以近景v2为编辑目标。没有新检索外部大屏案例。
- 完整提示词及调用参数：[generation-requests-B-v2.json](../design/concepts/generation-requests-B-v2.json)。
- 原始输出路径、归档路径、参考哈希、请求与规划哈希：[manifest-B-v2.json](../design/concepts/manifest-B-v2.json)。总览恢复过程及近景迭代：[B-v2-generation-log.json](B-v2-generation-log.json)。
- 新图实际尺寸均为1672×941，面向规划中的1920×1080应用画布；未拉伸伪装为原生1080p。旧四图及旧清单保持不变。

## 确认与下一步

等待用户确认修订B的园区与重点楼宇两层视觉版本。概念问题的事实核对不等于用户审美批准，selectedVisual仍为空，工作流仍在concept。

用户确认后才继续整屏设计，补齐实际需要的状态、完整文字图表、导航和视觉基准；整屏基准锁定后补制作规格与每层相机、锚点、UI占位，先用网页简化模型验证构图，再深化三维。C-04在该环节验证并关闭；后续逐层每版保存基准/当前截图对照，按差异改源重建。当前没有模型、网页交互或性能通过记录。
