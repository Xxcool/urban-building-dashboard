"""生成设计稿、旧版与修正版的原比例对照，明确未关闭的真实感差异。"""
from pathlib import Path
import json,hashlib,html,re
r=Path(__file__).resolve().parents[1];p=json.loads((r/'planning/project.json').read_text());runtime=json.loads((r/'checks/city-restoration-runtime-v14.json').read_text());cycles=json.loads((r/'checks/three-level-cycles-v14.json').read_text())
assert len(cycles)==18 and all(x['viewport']==[1920,1080] and x['canvases']==2 for x in cycles)
resources={}
for level in ['city','campus','building']:
 rows=[x for x in cycles if x['level']==level];mem={tuple(map(int,re.search(r'几何：(\d+) · 纹理：(\d+)',x['diagnostics']).groups())) for x in rows};assert len(mem)==1;values=[float(m.group(1)) for x in rows if(m:=re.search(r'P95：([\d.]+)',x['diagnostics']))];resources[level]={'cycles':len(rows),'resources':list(mem)[0],'observedP95Ms':[min(values),max(values)]}
assert runtime['logsAfterBuild']==[] and runtime['meshPick']['level']=='campus'
items=[{'id':'R-01','issue':'城市没有铺满，出现矩形地图底板','change':'背景地面延伸至视口外，城市覆盖越过画面四边；地面控制点校准后区域占场景宽94.5%、高74.3%','result':'主要构图已修正','evidence':'city-gray-v14b.jpg；city-detailed-v14c.jpg'}, {'id':'R-02','issue':'区域边界缺少发光效果','change':'同一轮廓的白色核心、青色边线和独立选择性Bloom；地面不参与泛光，避免浅色地面泛白','result':'已补效果；光晕强度仍需用户视觉复核','evidence':'v14a全场泛白→v14b选择性泛光→v14c阴影层次'}, {'id':'R-03','issue':'示范片区没有对应颜色','change':'青绿/浅青色区域及浅金色示范片区铺到地面，示范园区和图钉保持金色强调','result':'色区已补，未虚构区域运营数据','evidence':'city-no-data-v14c.jpg'}, {'id':'R-04','issue':'周边湖泊位置和形态不符','change':'参考图地面湖岸控制点反投影、自然样条岸线、浅岸/深水、岛屿、岸边叶簇，增加微波法线与光照反射','result':'位置关系和湖岸结构改善；水面材质仍不及设计稿细腻','evidence':'city-gray-v14b.jpg；city-no-data-v14c.jpg'}, {'id':'R-05','issue':'周边楼群不真实','change':'连续成组街区、混合低层/条板/裙房/塔楼、曲线主干道、透明叶簇、接触阴影；周边高度降低以突出园区','result':'已改善但未关闭：楼群排布仍有规则重复，建筑细部/景观密度与设计稿仍有差距','evidence':'city-detailed-v14a/b/c.jpg'}]
report={'planningSha256':hashlib.sha256((r/'planning/project.json').read_bytes()).hexdigest(),'engineeringResult':'passed','visualResult':'needs_review','userFeedback':'用户明确否定v13还原质量，不能用工程通过替代视觉验收','items':items,'resources':resources,'notCovered':['展厅目标硬件','长时运行','真实地理精度','用户最终视觉验收']}
inputs={}
for name in ['design/screens/city-no-data-design-v1.png','checks/city-detailed-v13-final.jpg','checks/city-no-data-v14c.jpg']:
 inputs[name]=hashlib.sha256((r/name).read_bytes()).hexdigest()
report['imageInputs']=inputs;(r/'checks/city-restoration-review-v14.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
rows=''.join('<tr>'+''.join('<td>'+html.escape(item[k])+'</td>' for k in ['id','issue','change','result','evidence'])+'</tr>' for item in items)
content='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>城市还原 v14 · 设计与修正版</title><style>body{margin:0;padding:28px;background:#f4f3ee;color:#123b40;font:16px/1.7 system-ui}h1{font-size:28px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0;background:white;border:1px solid #d1ddd5;border-radius:9px;overflow:hidden}img{display:block;width:100%;height:auto}figcaption{padding:12px}table{border-collapse:collapse;background:white}td,th{border:1px solid #cad9d1;padding:12px;vertical-align:top}pre{white-space:pre-wrap;word-break:break-all;font-size:12px}.note{background:#f1e4c8;border-radius:9px;padding:16px;margin:20px 0}@media(max-width:850px){.pair{grid-template-columns:1fr}}</style><h1>按设计稿修正城市层 · v14c</h1><p class="note">视觉仍待复核。用户已指出v13明显偏离设计，本页不会把工程可运行与用户视觉批准混为一谈。地面轮廓来自概念图控制点，不是真实地理资料。</p><h2>同一无数据状态：设计基准 / 实际网页</h2><div class="pair"><figure><img src="../design/screens/city-no-data-design-v1.png"><figcaption>用户附件对应的原AI设计，未修改，1672×941</figcaption></figure><figure><img src="city-no-data-v14c.jpg"><figcaption>v14c 实际WebGL网页1280×720，非AI替换背景</figcaption></figure></div><h2>空间结构：旧版 / 修正版</h2><div class="pair"><figure><img src="city-detailed-v13-final.jpg"><figcaption>v13：有限矩形底板、湖面与楼群过度简化</figcaption></figure><figure><img src="city-detailed-v14c.jpg"><figcaption>v14c：连续城市、控制点校准、分区与边界发光</figcaption></figure></div><h2>按用户指出的五项逐条复验</h2><table><tr><th>ID</th><th>问题</th><th>源修改</th><th>本轮判断</th><th>证据</th></tr>'''+rows+'</table><h2>输入哈希与工程观测</h2><pre>'+html.escape(json.dumps(report,ensure_ascii=False,indent=2))+'</pre></html>'
(r/'checks/city-restoration-v14.html').write_text(content)
(r/'docs/city-review-v14.md').write_text('''# 城市还原 v14 复验

用户对v13的视觉还原提出明确否定，本次按原确认稿修复，基准未改。实际对照见checks/city-restoration-v14.html；五项逐条结果见city-restoration-review-v14.json。城市铺满、区域轮廓、边界发光、示范色区和湖岸结构已实质调整；建筑细部、街区排布与水体材质仍有差距，视觉项保持待复核，不声明最终还原验收通过。

几何由city_layout.py从规划中锁定的概念图地面控制点反投影，生成器内容哈希在规划中校验；这里只适用于平面，不能反推出真实地理、楼高或实际运营总量。模型依然是真实GLB，区域叶簇是固定材质输入，未把整张AI图当背景。

灰盒v14a发现光晕过曝与深度闪烁，b版先校准空间再细化；细化a版18.49MB超过15MB预算，移除远景不可辨的独立树干、调整楼群后当前13,685,224字节、160,688三角形。浅色地面泛白改为独立图层泛光，补接触阴影并排除透明叶簇法线通道伪影，最后补水面色差与反射。

真实1920×1080做6轮三层切换，共18次采样，资源数量稳定；区域69绘制调用、34几何/28纹理，P95采样17.6ms。园区/楼宇96几何/17纹理，17.0~17.5ms。本轮只代表当前执行环境，未覆盖目标硬件或长时。修正后园区实体拾取下钻通过，缺失态保留；当前构建后的控制台错误/警告为空（历史PCFSoftShadowMap弃用警告已改为实际支持的PCFShadowMap，未删除历史日志）。

从全新目录重建见checks/rebuild-v14.json；原园区详细GLB SHA保持不变，root规划与两份清单同步。当前工程检查通过，但视觉项不以此结案。下一轮针对仍有规则重复的街区、建筑细部与更自然水面继续做局部还原，保留现有对照，不改基准掩盖差异。
''')
print(json.dumps({'review':str(r/'checks/city-restoration-v14.html'),'engineering':'passed','visual':'needs_review','resources':resources},ensure_ascii=False))
