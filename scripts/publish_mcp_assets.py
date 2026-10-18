"""核对MCP实际导出与规划绑定后发布本地资产；不在终端执行Blender或改写模型内容。"""
import argparse,hashlib,json,shutil,struct
from pathlib import Path
from city_layout import derive_city
root=Path(__file__).resolve().parents[1];parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['geometry','baked'],required=True);parser.add_argument('--version');args=parser.parse_args();version=args.version
plan_raw=(root/'planning/project.json').read_bytes();plan=json.loads(plan_raw);digest=hashlib.sha256(plan_raw).hexdigest();version=version or plan['production']['restoration']['version'];work=root/'work'/version;dst=root/'app/public/assets';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read_glb(path):
 data=path.read_bytes();assert data[:4]==b'glTF';length=struct.unpack_from('<I',data,12)[0];return json.loads(data[20:20+length]),data
sources={'campus':(work/'campus-v26.glb',work/'campus-v26.blend'),'city':(work/'city-output/app/public/assets/city.glb',work/'city-output/assets/city.blend')}
if args.stage=='baked':sources={level:(work/(level+'-'+version+'-baked.glb'),work/(level+'-'+version+'-baked.blend'))for level in sources}
loaded={level:read_glb(glb)for level,(glb,blend)in sources.items()}
# 绑定必须在文件复制前验证；不根据材质颜色推断业务身份。
roots={n.get('extras',{}).get('objectId'):n for n in loaded['campus'][0]['nodes'] if n.get('extras',{}).get('objectId')}
assert set(roots)=={x['id']for x in plan['demoDesign']['buildingIdentities']}
for key,node in roots.items():
 x,y,z=plan['production']['geometryById'][key]['position'];assert all(abs(a-b)<.001 for a,b in zip(node.get('translation',[0,0,0]),[x,z,-y]))
city=derive_city(plan);park=next(n for n in loaded['city'][0]['nodes']if n['name']=='city_PARK-DEMO');x,y,z=city['campusPositionM'];assert all(abs(a-b)<.001 for a,b in zip(park['translation'],[x,z,-y]))
for level,(document,data) in loaded.items():
 if args.stage=='baked':
  expected=plan['production']['city']['bakedLighting']['receivers'] if level=='city' else plan['production']['bakedLighting']['receivers']
  receivers=[n for n in document['nodes'] if n.get('extras',{}).get('bakeReceiver')];assert {n['name']for n in receivers}==set(expected)
  for node in receivers:
   for primitive in document['meshes'][node['mesh']]['primitives']:assert 'TEXCOORD_1'in primitive['attributes'] and document['materials'][primitive['material']]['occlusionTexture']['texCoord']==1
backup=work/'before-publish';backup.mkdir(parents=True,exist_ok=True)
for level,(glb,blend) in sources.items():
 destination=dst/('campus.glb' if level=='campus' else 'city.glb');blend_destination=root/('assets/scene.blend' if level=='campus' else 'assets/city.blend')
 for original in [destination,blend_destination]:
  snapshot=backup/original.name
  if original.exists()and not snapshot.exists():shutil.copyfile(original,snapshot)
 shutil.copyfile(glb,destination);shutil.copyfile(blend,blend_destination)
 document,data=loaded[level];triangles=sum(document['accessors'][p['indices']]['count']//3 for mesh in document['meshes']for p in mesh['primitives']if p.get('mode',4)==4)
 operations=['assets/mcp-operations/v26/'+level+'-geometry.json']
 if level=='campus':operations+=['assets/mcp-operations/v26/campus-preview.json','assets/mcp-operations/v26/campus-refine.json','assets/mcp-operations/v26/campus-landscape-correction.json','assets/mcp-operations/v26/campus-landscape-refine.json','assets/mcp-operations/v26/campus-edge-architecture.json','assets/mcp-operations/v26/campus-entrance-curb-fix.json']
 if args.stage=='baked' and level=='campus':operations+=['assets/mcp-operations/v26/campus-indirect.json']
 if args.stage=='baked':operations+=['assets/mcp-operations/v26/'+level+'-prepare.json','assets/mcp-operations/v26/'+level+'-ao.json','assets/mcp-operations/v26/'+level+'-export.json']
 if version=='v27':
  operations=['assets/mcp-operations/v27/'+level+'-'+stage+'.json' for stage in (['polish','ground-bake','glass','ao','interior-atlas','surface-final','indirect','tone','export'] if level=='campus' else ['polish','detail','ao','tone','export'])]
 info={'quality':'detailed','planningSha256':digest,'asset':destination.name,'assetSha256':sha(destination),'bytes':len(data),'triangles':triangles,'bakingComplete':args.stage=='baked','execution':'Blender MCP','operations':{p:sha(root/p) for p in operations},'blender':'5.2.2 LTS'}
 if level=='campus':
  info['objects']=[{'objectId':key,'rootNode':'building_'+key,'anchorNode':'anchor_'+key,'heightM':roots[key]['extras']['heightM']}for key in roots]
  manifest={**info,'files':{str(p.relative_to(root)):{'sha256':sha(p),'bytes':p.stat().st_size}for p in [destination,blend_destination]},'landscapeGeneratorSha256':sha(root/'scripts/campus_landscape.py'),'landscapePhase':'detailed'}
  (root/'assets/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(dst/'build-info.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
 else:
  base=json.loads((root/'app/public/assets/city-build-info.json').read_text());base.update(info);(root/'assets/city-manifest.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n');(dst/'city-build-info.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n')
if version=='v26':shutil.copyfile(work/'a1-preview-v26.png',dst/'a1-preview-v26.png')
if version=='v26':shutil.copyfile(work/'city-output/checks/city-road-surfaces.json',root/'checks/city-road-surfaces.json')
if args.stage=='baked':
 name=plan['production']['bakedLighting']['indirectAsset'];shutil.copyfile(work/name,dst/name)
print(json.dumps({'stage':args.stage,'planningSha256':digest,'models':{level:{'bytes':p[0].stat().st_size,'sha256':sha(p[0])}for level,p in sources.items()}},ensure_ascii=False))
