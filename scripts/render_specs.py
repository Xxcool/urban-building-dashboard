"""由唯一规划入口派生制作规格；文档不另维护相机、坐标或尺寸。"""
import argparse
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--source', default='planning/project.json')
args = parser.parse_args()
raw = (root / args.source).read_bytes()
p = json.loads(raw)
prod = p['production']
rows = '\n'.join('| ' + key + ' | `' + json.dumps(value, ensure_ascii=False) + '` |' for key, value in prod['geometryById'].items())
text = f'''# 制作规格 {prod['version']}

由 scripts/render_specs.py 从 planning/project.json 派生。规划SHA-256：{hashlib.sha256(raw).hexdigest()}。

尺寸依据：{prod['dimensionBasis']}。坐标约定：{json.dumps(prod['coordinateSystem'], ensure_ascii=False)}。

## 对象参数

| 稳定ID | 制作参数 |
| --- | --- |
{rows}

A1层数只读demoDesign.focusBuilding.floorsDefinition；裙房层高{prod['geometryById']['A1']['podiumFloorHeightM']}m，塔楼层高{prod['geometryById']['A1']['towerFloorHeightM']}m。其他建筑高度仅是视觉建模估计，不转写为未定义业务指标。

## 相机与构图

{json.dumps(prod['cameras'], ensure_ascii=False, indent=2)}

UI占位与安全边界：{json.dumps(p['design']['layout'], ensure_ascii=False)}。{prod['compositionGate']}。

初始相机是待校准估计，不能宣称已拟合AI图。以同一空间锚点验证两层，无法同时解释时修订制作估计；改变已确认视觉方向则重新确认。灰盒只作构图检查，不作概念稿或最终模型交付。

## 资产、材质与性能

{json.dumps(prod['assets'], ensure_ascii=False, indent=2)}

渲染配置：{json.dumps(prod['render'], ensure_ascii=False)}。

预算：{json.dumps(prod['budget'], ensure_ascii=False)}。实际浏览器另记录draw calls、三角形、帧时间、重复进入退出和资源释放。未测目标硬件或长时运行不报通过。

## 生成与复验

规划源 + 三张唯一终稿 → Blender MCP修改并保存工程 → MCP制作UV、AO/间接光并导出GLB → 核对后发布资产 → 从规划派生runtime → 实际浏览器同相机对照。MCP操作记录在assets/mcp-operations/v26；不使用终端Blender生成器，不手改GLB。两层共用模型与业务ID映射，标签、拾取和面板读取同一状态。

每层每版保存设计/实际对照，注明版本、视口、相机和状态；先处理构图与几何，再处理材质、UI、数据和交互。未通过项保留ID、原因假设、源修改、重建产物和下一步。
'''
output = root / 'docs/production-current.md'
output.write_text(text)
print(output)
