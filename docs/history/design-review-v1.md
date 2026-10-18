# B整屏设计 v1：状态与基准

2026-10-16。正常/选中状态复用用户确认的两张实际概念图，不重新随机生成。状态设计基于相同画面局部修改，使用内置image_gen；没有用HTML拼装替代设计图。

| 层级 | 正常且选中A1的基准 | 无数据基准 |
| --- | --- | --- |
| 园区 | ![园区正常](/Users/xiabin/Documents/Codex/2026-10-15/new-chat-2/outputs/gaoxin-digital-building/design/concepts/B-campus-v2.png) | ![园区无数据](/Users/xiabin/Documents/Codex/2026-10-15/new-chat-2/outputs/gaoxin-digital-building/design/screens/campus-no-data-design-v1.png) |
| 楼宇 | ![楼宇正常](/Users/xiabin/Documents/Codex/2026-10-15/new-chat-2/outputs/gaoxin-digital-building/design/concepts/B-building-v2r1.png) | ![楼宇无数据](/Users/xiabin/Documents/Codex/2026-10-15/new-chat-2/outputs/gaoxin-digital-building/design/screens/building-no-data-design-v1.png) |

已查看两张新图：均未把缺失数据写为0；园区A1卡片包含暂无经营数据，楼宇面积及比例为空，入驻产业区显示暂无产业数据，配套和几何保留。正常与无数据图可能有AI植被细节漂移，几何制作只以正常基准与统一规格为依据，不按状态各造一套建筑。单位与微小间距在代码UI中按规划源统一。

交互与布局唯一参数见 planning/project.json 的design。初始园区选A1；点击A1或重点楼宇导航进入近景；返回恢复园区镜头并保留A1。其他七栋只有已定义身份与角色，不补造指标或企业详情。演示/无数据切换驱动同一状态；缺失不当作故障，不引入告警、回放或内部楼层。

最终实现由独立文字、数据、图标、标签和实际三维场景组成；图片只作对照基准，不能把它作为背景冒充交互三维。原生应用目标1920×1080；参考PNG实际1672×941，比较保留原比例并标注视口。

制作前必须补几何、坐标与每层相机参数并通过网页简化模型检查。目标屏实际观看距离和专用GPU尚未提供；浏览器可测性能，物理屏视距与长时运行不能因此宣称完成。
