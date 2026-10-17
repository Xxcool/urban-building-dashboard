"""将实际网页连续截图制作成预览GIF，并生成保留原比例的整屏与阶段对照。"""
from pathlib import Path
from PIL import Image
import json,html,hashlib
r=Path(__file__).resolve().parents[1];folder=r/'checks/entry-frames-v22-final';timing=json.loads((folder/'timing.json').read_text());files=sorted(folder.glob('*.png'));frames=[Image.open(p).convert('RGB').quantize(colors=192) for p in files]
durations=[max(40,min(300,timing[i+1]['time']-v['time'])) for i,v in enumerate(timing[:-1])]+[800]
frames[0].save(r/'checks/campus-entry-v22.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=2,optimize=False)
p=json.loads((r/'planning/project.json').read_text());inputs=[]
def pic(path,title):
 f=r/path;inputs.append({'path':path,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()});return f'<figure><img src="../{path}"><figcaption>{html.escape(title)}</figcaption></figure>'
def pair(title,a,b):return '<h2>'+title+'</h2><div class="pair">'+pic(*a)+pic(*b)+'</div>'
body='''<!doctype html><meta charset="utf-8"><title>v22园区进入动效复核</title><style>body{margin:0;padding:28px;background:#f4f3ee;color:#123b40;font:15px/1.7 system-ui}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0 0 24px;background:white}img{width:100%;height:auto;display:block}figcaption{padding:12px}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><h1>v22 · 园区进入动效实拍复核</h1><p>首次约2.8秒，再次约1.1秒，A1返回约0.6秒。GIF来自实际页面连续截图，1280×720，无裁切/拉伸；起始帧约0.27秒，末帧额外停留便于查看。实际交互在页面运行，不以GIF替代状态与资源复验。</p>'''+pic('checks/campus-entry-v22.gif','实际网页动画片段')
for phase in ['approach','handoff','settle','reveal','complete']:
 candidates=[i for i,v in enumerate(timing) if v.get('data',{}).get('phase')==phase]
 if candidates:
  i=candidates[len(candidates)//2];body+=pic(f'checks/entry-frames-v22-final/{i:02d}.png',f"{phase} · 约{timing[i]['data']['seconds']}秒")
for level,name in [('city','城市'),('campus','园区'),('building','A1楼宇')]:body+=pair(name+'终态与原基准',(p['design']['baselines'][level]['selected-A1']['path'],'原确认设计基准，未改'),(f'checks/{level}-final-v22.png','当前实际网页 · 1920×1080'))
body+=pair('加载边界',('checks/entry-delayed-v22.png','实际HTTP延迟：留在城市等待'),('checks/entry-failure-v22.png','首次HTTP 503：留在城市并可重试'))
body+='<p>交叠期间两层实际地面投影XY一致，Z因近远裁切面不同而不同。首次朝向未同步的失败样本保留在entry-frames-v22a。运行记录entry-runtime-v22.json；原城市写实差异R-05仍开放，不能把动效通过称为整屏视觉批准。</p>'
body=body.replace('起始帧约0.27秒',f"起始帧约{timing[0]['data']['seconds']:.2f}秒")
(r/'checks/review-v22.html').write_text(body);(r/'checks/review-v22-inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n')
print('GIF bytes', (r/'checks/campus-entry-v22.gif').stat().st_size)
