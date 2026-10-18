"""核对三张唯一终稿、固定哈希和材质依赖，防止旧设计重新成为制作依据。"""
import argparse,hashlib,json
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--report',default='checks/design-contract-current.json');args=parser.parse_args()
r=Path(__file__).resolve().parents[1];p=json.loads((r/'planning/project.json').read_text());m=json.loads((r/'design/final/manifest.json').read_text());errors=[]
def check(value,message):
 if not value:errors.append(message)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
levels={'city','campus','building'}
check(m['status']=='user_confirmed','终稿未确认')
check(set(m['assets'])==levels,'终稿层级集合不一致')
check({f.name for f in (r/'design').rglob('*.png')}=={x+'.png' for x in levels},'design里存在非终稿图片')
for level in levels:
 item=m['assets'][level];f=r/item['path']
 check(item['path']=='design/final/'+level+'.png','终稿路径不是唯一入口')
 check(f.exists() and sha(f)==item['sha256'],level+'终稿不存在或被修改')
 check(p['selectedVisual']['concepts'][level]==item,level+'已选视觉引用与终稿不符')
 check(p['design']['baselines'][level]=={'selected-A1':item},level+'仍有并列旧基准')
for old in ['design/concepts','design/screens','references']:
 check(not (r/old).exists(),old+'旧目录仍存在')
for name,item in p['production']['materialInputs'].items():
 check(item['path'].startswith('assets/materials/'),'材质与设计目录未分离')
 check((r/item['path']).exists() and sha(r/item['path'])==item['sha256'],name+'材质丢失或改变')
 check((r/item['provenance']).exists(),name+'来源记录缺失')
check(p['production']['city']['alignment']['designTarget']==m['assets']['city'],'城市校准目标不是终稿')
check(p['production']['city']['alignment']['calibrationStatus']=='final-v26-control-points','当前校准状态未如实声明')
report={'result':'failed' if errors else 'passed','errors':errors,'scope':'终稿文件、引用与重建输入闭合；不代表实际页面已还原','finalAssets':m['assets'],'materialInputs':{k:v['path'] for k,v in p['production']['materialInputs'].items()}}
out=r/args.report;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False));raise SystemExit(bool(errors))
