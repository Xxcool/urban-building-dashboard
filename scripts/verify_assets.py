"""核对GLB实体节点、坐标、楼层横梁、固定输入与导出清单；不替代网页视觉验收。"""
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
parser.add_argument('--report', default='checks/assets-contract.json')
args = parser.parse_args()
root = args.root.resolve()
sha = lambda data: hashlib.sha256(data).hexdigest()
source = (root / 'planning/project.json').read_bytes()
p = json.loads(source)
spec = p['production']
manifest = json.loads((root / 'assets/manifest.json').read_text())
runtime = json.loads((root / 'public/assets/runtime.json').read_text())
info = json.loads((root / 'public/assets/build-info.json').read_text())
raw = (root / spec['assets']['scene']).read_bytes()
errors = []

def check(condition, message):
    if not condition:
        errors.append(message)

check(struct.unpack_from('<4sII', raw) == (b'glTF', 2, len(raw)), 'GLB头或长度不一致')
length, kind = struct.unpack_from('<II', raw, 12)
check(kind == 0x4e4f534a, '缺少glTF JSON块')
g = json.loads(raw[20:20 + length])
bin_start = 20 + length + 8
nodes = g['nodes']
expected = {o['id'] for o in p['demoDesign']['buildingIdentities']}
roots = {n.get('extras', {}).get('objectId'): (i, n) for i, n in enumerate(nodes) if n.get('extras', {}).get('objectId')}
check(set(roots) == expected, '业务根节点ID集合不匹配')
check(sum(bool(n.get('extras', {}).get('objectId')) for n in nodes) == len(expected), '存在重复业务根节点')
for object_id in sorted(expected):
    if object_id not in roots:
        continue
    _, node = roots[object_id]
    x, y, z = spec['geometryById'][object_id]['position']
    check(all(math.isclose(a, b, abs_tol=1e-4) for a, b in zip(node.get('translation', [0, 0, 0]), [x, z, -y])), object_id + '坐标转换不一致')
    anchors = [i for i, n in enumerate(nodes) if n.get('name') == 'anchor_' + object_id]
    check(len(anchors) == 1 and anchors[0] in node.get('children', []), object_id + '锚点缺失或归属错误')

focus = p['demoDesign']['focusBuilding']
floors = focus['floorsDefinition']
check(floors['total'] == floors['podium'] + floors['towerAbovePodium'] == focus['floors'], '总层数定义冲突')
focus_node = roots[focus['id']][1]
check(focus_node['extras']['totalFloors'] == floors['total'], '导出楼层元数据不一致')

# 读取真实顶点，验证塔楼22道水平幕墙横梁的位置，不只核对extras中的层数字段。
frame = next(n for n in nodes if n.get('name') == focus['id'] + '_frame')
positions = []
for primitive in g['meshes'][frame['mesh']]['primitives']:
    accessor = g['accessors'][primitive['attributes']['POSITION']]
    view = g['bufferViews'][accessor['bufferView']]
    check(accessor['componentType'] == 5126 and accessor['type'] == 'VEC3', '不支持的位置属性格式')
    offset = bin_start + view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
    stride = view.get('byteStride', 12)
    positions.extend(struct.unpack_from('<fff', raw, offset + i * stride) for i in range(accessor['count']))
fh = spec['floorHeightM']
width = spec['geometryById'][focus['id']]['towerSize'][0]
offset_x = spec['geometryById'][focus['id']]['towerOffset'][0]
verified_beams = 0
for i in range(floors['towerAbovePodium'] + 1):
    focus_geometry=spec['geometryById'][focus['id']]
    height = floors['podium']*focus_geometry['podiumFloorHeightM']+i*focus_geometry['towerFloorHeightM']+.125*focus_geometry['towerFloorHeightM']/fh
    corner_x = offset_x + (width + .55) / 2
    found = any(abs(v[0] - corner_x) < 1e-3 and abs(v[1] - height) < 1e-3 for v in positions)
    check(found, f'缺少第{i}道塔楼横梁的实际顶点')
    verified_beams += int(found)

# 从导出顶点核对步行入口，不让主通道或外展平台侵入南侧车行道。
south_limit=spec['site']['parkSize'][1]/2-spec['landscape']['entranceLanding']['roadClearanceM']
entrance_nodes=[n for n in nodes if n.get('name','').split('.')[0] in ['correction_v26_paving','correction_v26_paverJoint']]
check(len(entrance_nodes)==2,'南侧入口铺装缺失')
for node in entrance_nodes:
    for primitive in g['meshes'][node['mesh']]['primitives']:
        attr=g['accessors'][primitive['attributes']['POSITION']]
        check(attr['max'][2]<=south_limit+1e-3,'南侧步行入口侵入车行道：'+node['name'])

# 读取每种车型实际POSITION包络，核对导出身份与米制车身尺度。
vehicle_bounds={}
for item in spec['traffic']['fleet']:
    matches=[n for n in nodes if n.get('name')=='traffic_'+item['type']]
    check(len(matches)==1,'车型模板缺失或重复：'+item['type'])
    if not matches:continue
    parts=[nodes[i] for i in matches[0].get('children',[]) if 'mesh' in nodes[i]]
    bounds=[]
    for node in parts:
        for primitive in g['meshes'][node['mesh']]['primitives']:
            attr=g['accessors'][primitive['attributes']['POSITION']];bounds.append((attr['min'],attr['max']))
    size=[max(b[1][i] for b in bounds)-min(b[0][i] for b in bounds) for i in range(3)]
    check(abs(size[0]-item['lengthM'])<.2 and abs(size[2]-item['widthM'])<.3,'车型包络与米制规格不符')
    check(abs(size[1]-item['heightM'])<.2,'车型高度不符')
    vehicle_bounds[item['type']]={'sizeXYZ':size,'parts':len(parts),'instances':item['count']}
check(sum(item['count'] for item in spec['traffic']['fleet'])==spec['traffic']['vehicleCount'],'车队总量不一致')

for name, item in manifest['files'].items():
    data = (root / name).read_bytes()
    check(sha(data) == item['sha256'] and len(data) == item['bytes'], name + '与清单不一致')
for name, item in p.get('selectedVisual', {}).get('concepts', {}).items():
    check(sha((root / item['path']).read_bytes()) == item['sha256'], name + '已确认图片被改变')
for level, states in p['design']['baselines'].items():
    for name, item in states.items():
        check(sha((root / item['path']).read_bytes()) == item['sha256'], level + '/' + name + '整屏基准被改变')
for name, item in spec.get('materialInputs', {}).items():
    check(sha((root / item['path']).read_bytes()) == item['sha256'], name + '固定材质输入被改变')
check(manifest.get('execution')=='Blender MCP','模型不是MCP制作产物')
for operation,digest in manifest['operations'].items():
    check(sha((root/operation).read_bytes())==digest,'MCP操作记录已改变：'+operation)
check(all(item['planningSha256'] == sha(source) for item in [manifest, runtime, info]), '模型/网页/规划版本混用')
check(info['assetSha256'] == sha(raw), '网页加载清单的模型哈希不匹配')
check(manifest.get('landscapeGeneratorSha256') == sha((root/'scripts/campus_landscape.py').read_bytes()), '景观生成模块与清单不一致')
check(any(n.get('name')=='landscape_water' for n in nodes), '景观水面节点缺失')
check(not any(n.get('name','').startswith('landscape') and n.get('extras',{}).get('objectId') for n in nodes), '装饰错误占用了业务身份')
check(manifest['triangles'] <= spec['budget']['triangles'], '模型本体三角形超过预算')
landscape_budget=spec['landscape']['budget']
# v26另外增加幕墙和城市背景，景观预算只统计设施、人物与植被网格。
landscape_triangles=sum(g['accessors'][primitive['indices']]['count']//3 for node in nodes if node.get('name','').startswith(('landscape_','vegetation_')) and 'mesh' in node for primitive in g['meshes'][node['mesh']]['primitives'])
check(landscape_triangles<=landscape_budget['additionalTrianglesMax'],'景观网格三角形超过约定')
check(len(raw)-landscape_budget['previousCampusBytes']<=landscape_budget['additionalGlbBytesMax'],'景观新增模型体积超过约定')
check(len(raw) <= spec['budget']['glbMegabytes'] * 1_000_000, 'GLB超过预算')
check(not any('uri' in b for b in g['buffers']), 'GLB依赖外置二进制')
check(not any('uri' in image for image in g.get('images', [])), 'GLB依赖外置贴图')
report = {'result': 'passed' if not errors else 'failed', 'errors': errors, 'planningSha256': sha(source),
          'glbSha256': sha(raw), 'glbBytes': len(raw), 'modelTriangles': manifest['triangles'],
          'objects': sorted(expected),'vehicleTemplates':vehicle_bounds, 'verifiedTowerBeams': verified_beams, 'embeddedImages': len(g.get('images', [])), 'landscapeTriangles':landscape_triangles,
          'scope': '结构和固定输入核对；视觉、拾取和性能另需网页实测'}
out = root / args.report
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
raise SystemExit(bool(errors))
