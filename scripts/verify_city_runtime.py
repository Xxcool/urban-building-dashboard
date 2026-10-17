"""核对区域扩展的实际浏览器证据，区分冷启动、稳态、历史与当前版本。"""
from pathlib import Path
import hashlib,json,re,math
r=Path(__file__).resolve().parents[1];rows=json.loads((r/'checks/three-level-cycles-v13.json').read_text());state=json.loads((r/'checks/city-runtime-v13.json').read_text());reset=json.loads((r/'checks/city-camera-reset-v13-final.json').read_text());errors=[]
def check(v,msg):
 if not v:errors.append(msg)
check(len(rows)==36,'缺少12轮三层切换');results={}
for level,expected in [('city',(19,3)),('campus',(96,17)),('building',(96,17))]:
 samples=[x for x in rows if x['level']==level];check(len(samples)==12,level+'轮数错误');resources=set();p95=[];calls=[]
 for x in samples:
  check(x['viewport']==[1920,1080] and x['canvasCount']==2,'实际视口或复用实例错误');g=re.search(r'几何：(\d+) · 纹理：(\d+)',x['diagnostics']);resources.add(tuple(map(int,g.groups())));f=re.search(r'P95：([\d.]+)',x['diagnostics']);calls.append(int(re.search(r'draw calls：(\d+)',x['diagnostics']).group(1)))
  if f:p95.append(float(f.group(1)))
 check(resources=={expected},level+'资源发生累积/变化');results[level]={'cycles':len(samples),'geometries':expected[0],'textures':expected[1],'observedCallsRange':[min(calls),max(calls)],'observedP95RangeMs':[min(p95),max(p95)] if p95 else None}
check(state['meshPick']['level']=='campus','实体园区拾取未进入园区');check(state['buildingReturn']=='campus','楼宇返回路径错误')
check(state['targetNormal']['safeBottom']>=28 and state['targetMissing']['safeBottom']>=28,'区域卡片底部安全距离不足');check(state['targetNormal']['trafficPausedSample']==state['targetMissing']['trafficPausedSample'],'隐藏园区车辆仍推进')
for key in ['missingPersistsToCampus','missingPersistsToBuilding']:check(state[key]['mode']=='no-data' and '—' in state[key]['kpis'],'无数据模式跨层丢失')
error=max(math.hypot(reset['before'][key]['x']-reset['reset'][key]['x'],reset['before'][key]['y']-reset['reset'][key]['y']) for key in reset['before']);check(error<1e-6,'旋转复位误差过大');check(reset['before']!=reset['rotated'],'未观察到旋转')
check(json.loads((r/'checks/browser-console-v13.json').read_text())==[],'当前预览存在控制台错误/警告')
result={'result':'failed' if errors else 'passed','errors':errors,'planningSha256':hashlib.sha256((r/'planning/project.json').read_bytes()).hexdigest(),'levels':results,'safeBottomPx':{'normal':state['targetNormal']['safeBottom'],'missing':state['targetMissing']['safeBottom']},'cameraResetNormalizedError':error,'scope':'目标画布短时浏览器检查；首个园区样本含一次阴影冷启动234次调用，稳态调用另见原始记录；未覆盖硬件、长时或独立显存卸载分析'}
(r/'checks/city-runtime-verification-v13.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False));raise SystemExit(bool(errors))
