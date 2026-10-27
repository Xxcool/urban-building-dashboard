"""核对区域GLB、稳定园区身份、锚点、预算与规划哈希；不替代网页视觉验证。"""
from pathlib import Path
import argparse,hashlib,json,struct,math
from city_layout import derive_city
from city_geometry import clear_surface
p=argparse.ArgumentParser();p.add_argument('--report',default='checks/city-assets-contract.json');a=p.parse_args();r=Path(__file__).resolve().parents[1];raw=(r/'planning/project.json').read_bytes();plan=json.loads(raw);s=derive_city(plan);m=json.loads((r/'assets/city-manifest.json').read_text());info=json.loads((r/'public/assets/city-build-info.json').read_text());data=(r/s['assets']['scene']).read_bytes();g=json.loads(data[20:20+struct.unpack_from('<I',data,12)[0]]);errors=[]
def check(v,msg):
 if not v:errors.append(msg)
check(struct.unpack_from('<4sII',data)==(b'glTF',2,len(data)),'GLB头长度错误');check(hashlib.sha256(raw).hexdigest()==m['planningSha256']==info['planningSha256'],'规划/区域模型版本不一致');check(hashlib.sha256(data).hexdigest()==m['assetSha256']==info['assetSha256'],'模型清单哈希不一致');check(m.get('execution')=='Blender MCP','城市不是MCP制作产物')
for operation,digest in m['operations'].items():check(hashlib.sha256((r/operation).read_bytes()).hexdigest()==digest,'MCP操作记录改变：'+operation)
nodes=g['nodes'];root=next(n for n in nodes if n.get('name')=='city_PARK-DEMO');check(root['extras']['regionObjectId']=='PARK-DEMO','园区身份错误');x,y,z=s['campusPositionM'];check(all(math.isclose(a,b,abs_tol=1e-3) for a,b in zip(root.get('translation',[]),[x,z,-y])),'园区坐标不一致')
for poi in s['poi']:
 matches=[n for n in nodes if n.get('name')=='city_anchor_'+poi['id']];check(len(matches)==1,poi['id']+'锚点重复/缺失')
 if matches:
  x,y,z=poi['position'];check(all(math.isclose(a,b,abs_tol=1e-3) for a,b in zip(matches[0].get('translation',[]),[x,z,-y])),poi['id']+'锚点坐标错误')
check(len(data)<=s['budget']['glbMegabytes']*1_000_000,'区域模型超过体积预算');check(m['triangles']<=s['budget']['triangles'],'区域三角形超过预算');check(not any('uri' in b for b in g['buffers']),'模型依赖外置buffer')
audit=json.loads((r/'checks/city-road-surfaces.json').read_text());dry_roads=[road for road in audit['roads'] if not road['bridge']]
violations=[i for i,road in enumerate(dry_roads) if not clear_surface(road['a'],road['b'],road['width'],audit['lakes'])]
check(not violations,'普通路面与水域交叉：'+str(violations[:10]))
report={'result':'failed' if errors else 'passed','errors':errors,'planningSha256':m['planningSha256'],'model':info,'dryRoadSurfaces':len(dry_roads),'waterIntersections':len(violations),'scope':'结构与预算检查，非真实地理/视觉/硬件认证'};dest=r/a.report;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False));raise SystemExit(bool(errors))
