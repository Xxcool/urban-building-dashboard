"""生成网页只读配置，省去用户确认记录与本机路径；业务事实只取规划源。"""
import argparse
import hashlib
import json
from city_layout import derive_city
from pathlib import Path

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output-root',type=Path,default=root)
args=parser.parse_args()
raw=(root/'planning/project.json').read_bytes();p=json.loads(raw)
out=args.output_root/'app/public/assets';out.mkdir(parents=True,exist_ok=True)
# 原确认总量作为校验约束；前端实际汇总只从逐栋演示指标派生。
rows=[p['demoDesign']['focusBuilding'],*p['demoDesign']['buildingMetrics'].values()]
assert len(rows)==p['demoDesign']['campus']['buildings']
for key in ['grossAreaM2','rentableAreaM2','rentedAreaM2','enterprises']:
 assert sum(row[key] for row in rows)==p['demoDesign']['campus'][key],key+'逐栋总量不一致'
config={k:p[k] for k in ['project','demoDesign','production']}
config['production']['city']=derive_city(p)
config['design']={k:v for k,v in p['design'].items() if k not in ['baselines','baselineReuse']}
config['planningSha256']=hashlib.sha256(raw).hexdigest()
(out/'runtime.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
print(out/'runtime.json')
