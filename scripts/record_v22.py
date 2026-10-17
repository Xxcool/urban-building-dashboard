"""用工作流CLI登记v22续作证据，保留既有真实概念确认及开放视觉差异。"""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
cli=Path('/Users/xiabin/.codex/skills/build-3d-visual-dashboard/scripts/workflow.py')
s=json.loads((root/'state.json').read_text()); old=s['records']; doc='docs/iteration-v22.md'
def run(*args):
 p=subprocess.run([sys.executable,str(cli),str(root),*args],capture_output=True,text=True)
 if p.returncode: raise RuntimeError(p.stdout+p.stderr)
def advance(summary):run('advance','--evidence',doc,'--summary',summary)
def check(level,artifact,summary,decision=None,evidence=None,result='passed',next_step=None):
 a=['check','--level',level,'--artifact',artifact,'--result',result,'--evidence',*(evidence or [doc,'checks/review-v22.html']),'--summary',summary]
 if decision:a+=['--user-decision',decision]
 if next_step:a+=['--next',next_step]
 run(*a)
run('sync-source','--source','planning/project.json','--reason','用户确认园区进入分镜，v22已实现并复验；复用原概念确认')
advance('复用既有研究和已确认范围，本轮仅实施已确认进入动效')
for level,row in old['concept']['levels'].items():check(level,row['artifact']['path'],'复用原固定概念及真实用户确认',row['userDecision'])
advance('原概念方向不变，确认沿用')
for level,row in old['design']['levels'].items():check(level,row['artifact']['path'],'原基准未修改，v22动效按已确认分镜实施')
advance('既有整屏基准及v22分镜已核对')
run('issue','--level','city','--id','CITY-BUDGET','--change','城市344825三角形/14.293MB，v22独立重建及契约检查通过','--result','passed','--evidence','checks/city-contract-v22.json','checks/rebuild-v22-final.json')
for level,row in old['production']['levels'].items():check(level,row['artifact']['path'],'独立从源重建，资产契约通过；不代表写实视觉批准',evidence=[doc,'checks/rebuild-v22-final.json'])
advance('模型和配置从源生成，哈希一致')
for level in s['levels']:check(level,f'checks/{level}-final-v22.png','实际网页模型加载、绑定及终态构图复核')
advance('三层实际网页终态与原基准并排复核，写实差异保留至review')
for level in s['levels']:check(level,f'checks/{level}-final-v22.png','进入动效、对象联动和往返验证通过',evidence=[doc,'checks/entry-runtime-v22.json'])
advance('动效实际交互及12轮往返完成，保留未覆盖项')
next_step='继续按原稿细化街区、建筑个体与湖岸水面；本轮进入动画等待用户体验反馈'
run('issue','--level','city','--id','R-05-REALISM','--change','v22进入动效实现；原城市建筑和湖岸写实差异仍开放','--result','failed','--evidence',doc,'checks/review-v22.html','--next',next_step)
check('city','checks/city-final-v22.png','动效通过不等于城市写实还原通过',result='failed',next_step=next_step)
print('v22 recorded; review remains open')
