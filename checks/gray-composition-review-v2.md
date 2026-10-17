# 简化模型构图复验 v2

2026-10-16。实际网页加载campus-gray.glb，不是图片代替模型。尺寸仍为示意制作估计，原概念图保留作视觉方向与构图依据。

| 层级 | 已确认设计 | 当前简化模型 |
| --- | --- | --- |
| 园区 | ![园区基准](/Users/xiabin/Documents/Codex/2026-10-15/new-chat-2/outputs/gaoxin-digital-building/design/concepts/B-campus-v2.png) | ![园区简化模型v2](/Users/xiabin/Documents/Codex/2026-10-15/new-chat-2/outputs/gaoxin-digital-building/checks/campus-gray-v2-stable.jpg) |
| 楼宇 | ![楼宇基准](/Users/xiabin/Documents/Codex/2026-10-15/new-chat-2/outputs/gaoxin-digital-building/design/concepts/B-building-v2r1.png) | ![楼宇简化模型v2](/Users/xiabin/Documents/Codex/2026-10-15/new-chat-2/outputs/gaoxin-digital-building/checks/building-gray-v2-final.jpg) |

比较条件：应用设计画布1920×1080，实际稳定截图使用浏览器默认1280×720等比例显示；同一演示快照、A1选择、各层规划默认相机，截图在相机完成过渡后保存。浏览器目标viewport的DOM边界另见gray-target-layout.json。浏览器viewport覆盖后的截图出现裁取尺度异常，相关早期1920截图不作为最终完整视口证据；未拉伸或裁图掩盖此限制。

## 修复记录

- G-01：首版园区斜向透视偏重、主体比例偏小。调整唯一规划源中的相机、层高及视觉体量估计；第二版实际可见三塔、两侧、前三栋，八个标签全部位于场景区，无标签互相重叠或进入左侧面板。
- G-02：首版近景底部偏紧。修订同一A1的相机距离与目标点，第二版包含完整三层裙房和塔身。没有按近景另建一栋不同建筑。
- U-01：首版详情栏配套与返回重叠；第二版仍出现返回底端733px超720px。修改组件间距、卡片字号与高度，不改数据或缩放单独元素，最终返回底部705.86px、配套底部668.53px，均在720px视口内。1920画布中分别为1058.80px与1002.80px，均低于1080px边界。
- T-01：开发服务的文件事件没有可靠使旧模块失效，开启限定源目录的轮询并重启服务。实际重新加载后确认旧布局已替换，避免用旧缓存截图判断源修改效果。

## 实际操作

在园区截图观察出的B2网格位置点击，侧栏变为B2、次要塔楼、后排右侧；没有补造指标。随后点击A1塔身实际网格，界面进入building，显示A1对应面积与比例。该检查验证真实网格raycast，非仅按钮跳转。

P-01构图准入在简化阶段通过，允许深化。灰盒不能表示最终材质、细节、性能或视觉还原通过；精确立面和24层分格在细化生成与场景检查中继续核对。P-02完整绑定与P-03材质/性能仍需最终模型验证。
