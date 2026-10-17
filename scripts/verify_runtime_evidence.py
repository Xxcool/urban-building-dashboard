"""核对浏览器实际采集的业务、拾取、缺失态、循环资源与目标画布证据。"""
import argparse
import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--tag', required=True)
parser.add_argument('--assets', required=True)
parser.add_argument('--rebuild', required=True)
parser.add_argument('--cycles')
parser.add_argument('--layout')
parser.add_argument('--report')
args = parser.parse_args()
p = json.loads((root / 'planning/project.json').read_text())
read = lambda path: json.loads((root / path).read_text())
picking = read('checks/mesh-picking-' + args.tag + '.json')
missing = read('checks/no-data-' + args.tag + '.json')
cycles = read(args.cycles or 'checks/cycles-performance-' + args.tag + '.json')
layout = read(args.layout or 'checks/layout-1920-' + args.tag + '.json')
assets = read(args.assets)
rebuild = read(args.rebuild)
compact = lambda text: re.sub(r'\s+', '', text)
errors = []

def check(ok, message):
    if not ok:
        errors.append(message)

expected = {item['id'] for item in p['demoDesign']['buildingIdentities']}
focus = p['demoDesign']['focusBuilding']
campus = p['demoDesign']['campus']
check(set(picking['campus']['labels']) == expected, '总览八个标签未全部实际可见')
check({item['id'] for item in picking['picking']} == expected and all(item['result'] == 'passed' and item['id'] == item['selected'] for item in picking['picking']), '实际模型拾取未全部通过')
area = lambda value: f'{value/10000:.1f}'.removesuffix('.0')
campus_text = compact(picking['campus']['metrics'])
for value in [str(campus['buildings'])+'栋', area(campus['grossAreaM2'])+'万㎡', str(round(campus['rentedAreaM2']/campus['rentableAreaM2']*100))+'%', str(campus['enterprises'])+'家']:
    check(value in campus_text, '园区面板口径不一致：' + value)
building_text = compact(picking['building']['metrics'])
for value in [str(focus['floors'])+'层', area(focus['grossAreaM2'])+'万㎡', str(round(focus['rentedAreaM2']/focus['rentableAreaM2']*100))+'%', str(focus['enterprises'])+'家']:
    check(value in building_text, '楼宇面板口径不一致：' + value)
space = compact(picking['building']['space'])
for key, value in [('已租面积',focus['rentedAreaM2']),('可租面积',focus['rentableAreaM2']),('可租空置面积',focus['rentableAreaM2']-focus['rentedAreaM2'])]:
    check(key + f'{value/10000:.1f}万㎡' in space, '空间利用口径不一致：' + key)
for level in ['campus','building']:
    check(missing[level]['mode'] == 'no-data' and missing[level]['kpis'].count('—') == 4, level + '缺失态未显示四个缺失值')
check(missing['campus']['visibleLabels'] == len(expected), '缺失状态删除了几何或标签')
check('暂无产业数据' in missing['building']['industries'], '缺失产业状态不明确')
check('0' not in missing['building']['space'], '缺失面积被伪装为0')
for service in p['demoDesign']['contentDefinitions']['services']['labels']:
    check(service in missing['building']['services'], '缺失数据时错误移除了已知配套')

def stats(text):
    one = lambda pattern: float(re.search(pattern,text).group(1))
    return {'geometries':one(r'几何：(\d+)'),'textures':one(r'纹理：(\d+)'),'calls':one(r'draw calls：(\d+)'),
            'frameP95':one(r'P95：([\d.]+)'),'frames':one(r'已渲染 (\d+)')}
observed = [stats(cycles['before']), *[stats(item['stats']) for item in cycles['cycles']], stats(cycles['after'])]
check(len(cycles['cycles']) >= p['production']['budget']['resourceCycles'], '循环次数不足')
check(all(item['level']=='campus' and item['selected']==focus['id'] for item in cycles['cycles']), '下钻返回没有恢复规定上下文')
check(cycles['measuredViewport']==cycles['endingViewport']==p['project']['viewport'], '循环前后未实测到目标视口')
check(assets['glbSha256'][:12] in cycles['before'] and assets['glbSha256'][:12] in cycles['after'], '浏览器测量的模型版本不匹配')
check(len({(item['geometries'],item['textures']) for item in observed}) == 1, '资源数量随循环增长或变化')
check(max(item['calls'] for item in observed) <= p['production']['budget']['drawCalls'], '绘制调用超过目标')
target_before = stats(cycles['targetBefore'])
target_after = stats(cycles['after'])
check(target_after['frames']-target_before['frames'] >= 600, '目标视口最终P95窗口仍包含之前的帧')
check(target_after['frameP95'] <= p['production']['budget']['frameTimeP95Ms'], '当前浏览器目标视口P95超过目标')
for level in ['campus','building']:
    rail = layout[level]['rail']
    check(rail['scroll'] <= rail['client'], level + '信息栏溢出')
    check(layout[level]['dashboard']['width']==p['project']['viewport']['width'] and layout[level]['dashboard']['height']==p['project']['viewport']['height'], '画布尺寸不匹配')
safe_bottom = p['project']['viewport']['height']-layout['building']['back']['bottom']
check(safe_bottom >= p['design']['layout']['safeBottomPx'], '楼宇返回按钮侵入底部安全区')
check(len(layout['campus']['labels']) == len(expected), '目标视口未显示八栋标签')
check(assets['result']=='passed' and rebuild['result']=='passed', '资产或从源重建未通过')
check(all(item['identical'] for item in rebuild['comparisons'].values()), '新输出目录与当前模型不一致')
report = {'result':'passed' if not errors else 'failed','errors':errors,
          'planningSha256':hashlib.sha256((root/'planning/project.json').read_bytes()).hexdigest(),
          'objects':sorted(expected),'pickingPassed':len(picking['picking']),'cycles':len(cycles['cycles']),
          'resources':observed[0],'targetViewport':layout['viewport'],'targetFinalStats':target_after,'safeBottomPx':safe_bottom,
          'glbBytes':assets['glbBytes'],'modelTriangles':assets['modelTriangles'],
          'scope':'浏览器实际采集证据核对；不代替审美、目标硬件、长时运行或独立显存分析'}
out=root/(args.report or 'checks/runtime-verification-'+args.tag+'.json')
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
