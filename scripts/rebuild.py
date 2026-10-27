"""在全新目录通过 Blender MCP 重导已保存工程，再从源码构建网页；不走后台 Blender 建模。"""
import argparse,hashlib,json,shutil,struct,subprocess,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--dest',type=Path,required=True);parser.add_argument('--uvx',default=shutil.which('uvx')or'uvx');parser.add_argument('--cache',type=Path);parser.add_argument('--report',default='checks/rebuild-v27.json');args=parser.parse_args();dest=args.dest.resolve()
if dest.exists():raise SystemExit('目标目录已存在，请使用新的独立目录。')
dest.mkdir(parents=True);(dest/'checks').mkdir();(dest/'assets').mkdir()
for name in ['planning','scripts','design']:shutil.copytree(root/name,dest/name)
for name in ['src','tests','public']:shutil.copytree(root/name,dest/name,ignore=shutil.ignore_patterns('*.glb'))
for name in ['package.json','package-lock.json','index.html','vite.config.js','jsconfig.json','.prettierrc.json']:shutil.copy2(root/name,dest/name)
for name in ['scene.blend','city.blend','manifest.json','city-manifest.json']:shutil.copy2(root/'assets'/name,dest/'assets'/name)
shutil.copytree(root/'assets/materials',dest/'assets/materials');shutil.copytree(root/'assets/mcp-operations',dest/'assets/mcp-operations');shutil.copy2(root/'checks/city-road-surfaces.json',dest/'checks/city-road-surfaces.json')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest();steps=[];started=time.monotonic()
def run(label,command,cwd):
 tick=time.monotonic()
 with (dest/'rebuild.log').open('a')as log:result=subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT)
 steps.append({'step':label,'exitCode':result.returncode,'seconds':round(time.monotonic()-tick,2)})
 if result.returncode:raise RuntimeError(label+'失败，见 '+str(dest/'rebuild.log'))
def canonical_glb(path):
 data=path.read_bytes();size=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+size])
 # 插件连接状态属于会话元数据，既不是模型内容，也不参与网页业务。
 for scene in doc.get('scenes',[]):
  extras=scene.get('extras',{});extras.pop('blendermcp_server_running',None)
  if not extras:scene.pop('extras',None)
 return json.dumps(doc,sort_keys=True),data[20+size:]
comparisons={}
for level,blend in [('campus','scene.blend'),('city','city.blend')]:
 for stage in ['load','export']:
  source=dest/'assets'/blend;target=dest/'public/assets'/(level+'.glb')
  code='import bpy\n'+('bpy.ops.wm.open_mainfile(filepath='+repr(str(source))+')'if stage=='load'else'bpy.ops.export_scene.gltf(filepath='+repr(str(target))+",export_format='GLB',export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_apply=True)")
  operation=dest/'checks'/(level+'-'+stage+'.json');operation.write_text(json.dumps({'code':code},ensure_ascii=False))
  run(level+' MCP '+stage,[args.uvx,'--offline','--from','blender-mcp','python','scripts/blender_mcp_client.py','--tool','execute_blender_code','--arguments',str(operation),'--report','checks/'+level+'-'+stage+'-result.json'],dest)
 original=root/'public/assets'/(level+'.glb');rebuilt=dest/'public/assets'/(level+'.glb');same=canonical_glb(original)==canonical_glb(rebuilt);comparisons[level]={'originalSha256':sha(original),'rebuiltSha256':sha(rebuilt),'identical':sha(original)==sha(rebuilt),'sameModelContent':same}
 if not same:raise RuntimeError(level+' 重导内容不同，保留输出供排查。')
run('派生网页配置',['python3','scripts/prepare_runtime.py'],dest)
npm=['npm','ci','--no-audit','--no-fund']
if args.cache:npm+=['--cache',str(args.cache.resolve())]
run('安装锁定依赖',npm,dest);run('前端契约测试',['npm','test'],dest);run('生产构建',['npm','run','build'],dest)
comparisons['runtime']={'identical':sha(root/'public/assets/runtime.json')==sha(dest/'public/assets/runtime.json')}
report={'result':'passed','output':str(dest),'seconds':round(time.monotonic()-started,2),'steps':steps,'comparisons':comparisons,'scope':'独立目录加载打包Blend，通过真实MCP重导；模型JSON与二进制相同，仅忽略插件运行态布尔字段。前端由规划源和锁定依赖重新构建，不重新执行历史建模操作。'}
(root/args.report).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
