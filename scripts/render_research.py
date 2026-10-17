"""从唯一规划入口生成调研交接文档；不修改确认记录或派生设计图。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = json.loads((ROOT / 'planning/project.json').read_text())
project = p['project']
level_rows = '\n'.join('| ' + x['name'] + ' | ' + '、'.join(x['content']) + ' |' for x in p['levels'])
visual_rows = '\n'.join('| ' + x['id'] + ' ' + x['name'] + ' | ' + x['layout'] + ' | ' + x['materials'] + ' |' for x in p['visualCandidates'])
decision_rows = '\n'.join('- ' + x['id'] + '：用户回复「' + x['reply'] + '」' + ('，覆盖：' + x['covers'] if 'covers' in x else '') for x in p['decisions'])
campus = p['demoDesign']['campus']
focus = p['demoDesign']['focusBuilding']
text = f'''# {project['title']}：业务与视觉调研、概念设计任务书 v1

2026-10-15。由 scripts/render_research.py 读取 planning/project.json 生成；规划变更请修改该入口后重新生成本文。

## 已确认范围

{project['context']}；{project['siteType']}；用途为{project['purpose']}。目标画布 {project['viewport']['width']}×{project['viewport']['height']}，16:9。目前无用户提供的建筑、测绘、模型或接口资料，使用{project['dataMode']}。

| 层级 | 展示内容 |
| --- | --- |
{level_rows}

建议阅读路径：先看园区空间与关键指标，点击重点楼宇，查看该栋楼的空间、企业和配套，再返回园区。楼宇在场景与面板中沿用同一身份；未来实现交互时，选择状态应同步。

本期边界：{'；'.join(p['exclusions'])}。参考案例中的监控、消防、能耗等能力不会自动成为本期需求。

## 业务调研与依据

1. **武汉东湖高新区：资源要素图**。官方资料将资源地图、产业地图、考察路线区分；楼宇资源详情涉及可租面积、入驻企业和配套。这为“园区看资源分布、楼宇看空间与企业”的内容组织提供本地依据。该文为历史方案说明，不据此声称这些数据当前仍有效或接口可用。
   来源：https://www.wehdz.gov.cn/2022/zmq_75779/xwdt_75782/202210/t20221027_2072873.shtml
2. **光谷光电子信息产业园**。官方介绍涉及光通信、激光、集成电路、移动互联和软件创意等产业。本项目可据此建立光谷产业语境，但不会把整片产业园的统计值代入虚构示范园区。
   来源：https://www.wehdz.gov.cn/2022/ztzl_75799/zsyz_75806/zsdt/202210/t20221023_2065137.shtml
3. **武汉市数据局：光谷数字经济产业园**。资料提出办公、生活、展示融合及生态智慧社区，可作为景观、公共空间与配套呈现的背景依据。本期没有该真实园区的建筑图纸，不能据此复原其建筑或地理布局。
   来源：https://whsj.wuhan.gov.cn/sjjczlwl/cyjjq/202602/t20260209_2726520.shtml

以上为来源核实的信息。具体三维地块、楼栋形态和经营数值属于设计假设；“武汉东湖高新区产业背景 + 虚构示范园区”已获用户确认，不等于用户提供了真实项目数据。

## 实际视觉观察

**图扑《绿色数字园区运维》**：已通过浏览器实际查看全景动态大屏和楼宇透视参考。全景采用中央园区、左右窄栏、顶部标题和底部导航，景观、建筑和环境光共同建立尺度；透视状态将选中建筑提亮，周围模型退后，形成层级。可借鉴空间主次和选中反馈。原图仅约800×400，动态光照有高亮泛白，侧栏较密，不宜直接作为1080p字号依据。

来源：https://www.hightopo.com/blog/2974.html

已归档原始参考：references/hightopo-campus.gif、references/hightopo-building.gif；仅供研究比较，版权归原作者，不作为交付页面素材。

**ThingJS-X 智慧园区方案**：已读取官方方案并在浏览器查看空间可视化应用截图。其深色底、集中突出对象与状态的做法适合选中楼宇；但所示内部空间和运维信息比本期范围更细，不能照搬其设备、告警或内部层级。

来源：https://x.thingjs.com/ibv.html

## 两个待选方向

| 方向 | 构图 | 材质与灯光 |
| --- | --- | --- |
{visual_rows}

A 更适合较暗展厅中的整体态势与指标并读；B 更突出建筑与景观，阅读顺序更接近展陈说明。这是本项目的设计判断，并非来源对本项目的结论。两种方向使用同一组示范对象，比较构图和材质，不只是换色。

每种方向各输出园区总览、重点楼宇一张16:9概念图，共四张。概念图用于确认空间、明暗、材质和信息密度；确定方向后再核对完整整屏文字、图表、状态和视觉基准。

## 概念图输入与检查

园区设计假设：{p['demoDesign']['layout']}。重点对象 {focus['id']} {focus['name']}：{focus['form']}。以上是虚构设计设定，不是工程尺寸。

园区演示数值：{campus['buildings']}栋，总建筑面积{campus['grossAreaM2']/10000:g}万㎡，出租率{campus['rentedAreaM2']/campus['rentableAreaM2']:.0%}，入驻{campus['enterprises']}家。重点楼宇：{focus['floors']}层，建筑面积{focus['grossAreaM2']/10000:g}万㎡，出租率{focus['rentedAreaM2']/focus['rentableAreaM2']:.0%}，入驻{focus['enterprises']}家。出租率按已租面积/可租面积计算，不以总建筑面积作分母。首版概念图若出现不同值或楼栋数量漂移，须在视觉审查中记录，不直接转成实现事实。

AI 可能出现文字、层数、楼栋数量或跨图形态不一致。概念图片不替代规划契约；批准风格也不等于批准这些偏差。下一步整屏设计需收敛对象身份、可读文字、数据范围、选中/返回状态；建模前才确定尺寸、相机与制作参数。

生成方式：内置 image_gen.imagegen；逐图提示词见 design/concepts/prompts-v1.json。产物清单记录实际路径和哈希。确认图将固定保存，不在重建中重新随机生成。

## 用户决定与停点

{decision_rows}

当前未选定视觉方向，也未确认任何概念图片。停点：{p['nextGate']}。

## 能力与未覆盖项

本阶段已验证文件、终端、联网检索、浏览器参考查看能力；生图使用内置工具，结果以实际产物为准。agent-reach Exa 后端未配置，doctor 因配置目录权限失败，已改用可用联网检索，没有修改用户配置。Blender、模型导出、网页联调和目标硬件测试将在对应阶段检查；当前不报告通过。
'''
(ROOT / 'docs').mkdir(exist_ok=True)
(ROOT / 'docs/research-and-brief-v1.md').write_text(text)
print(ROOT / 'docs/research-and-brief-v1.md')
