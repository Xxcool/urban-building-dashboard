"""生成原设计、当前整屏及卡片修改前后的等比例对照，不改写确认基准。"""
from pathlib import Path
import json,hashlib,html
r=Path(__file__).resolve().parents[1];p=json.loads((r/'planning/project.json').read_text());inputs=[]
def pic(path,label):
 f=r/path;inputs.append({'path':path,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()});return '<figure><img src="../'+path+'"><figcaption>'+html.escape(label)+'</figcaption></figure>'
def pair(title,a,b):return '<h2>'+title+'</h2><div class="pair">'+pic(*a)+pic(*b)+'</div>'
body='''<!doctype html><meta charset="utf-8"><title>v21整屏与对象卡片复核</title><style>body{margin:0;padding:28px;background:#f4f3ee;color:#123b40;font:15px/1.7 system-ui}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0 0 24px;background:white}img{width:100%;height:auto;display:block}figcaption{padding:12px}h2{margin-top:36px}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><h1>v21 · 城市延伸与对象卡片复核</h1><p>原图完整并排，保持比例；默认整屏1920×1080，演示数据；卡片为实际选择状态。原AI基准未改。实际交互与性能见cards-runtime-v21.json，源重建见rebuild-v21-delivery.json。</p><p>城市还原问题R-05继续开放：建筑、水面、路网和景观仍比原稿简化。卡片为用户后续要求的局部修订，不伪称原稿已包含这套卡片。园区进入动画待用户确认v22分镜，本版未实现。</p>'''
for level,name in [('city','城市'),('campus','园区'),('building','A1楼宇')]:body+=pair(name+'整屏',(p['design']['baselines'][level]['selected-A1']['path'],'已确认原设计基准'),(f'checks/{level}-final-v21.png','当前网页 · 默认相机'))
body+=pair('楼宇卡片修改前后',('checks/campus-C1-v19.png','v19：旧卡片'),('checks/campus-C1-final-v21.png','v21：面积主值、辅助指标、自动避让'))
body+=pair('区域卡片',('checks/city-industry-final-v21.png','产业楼宇：现有类别与园区演示指标'),('checks/city-services-final-v21.png','配套服务：服务方向，无真实设施统计'))
body+=pair('缩远与缺失状态',('checks/city-zoomout-v20.png','城市最大缩远：外围连续街区'),('checks/campus-C1-empty-v21.png','无数据：身份保留，经营数值为—'))
body+=pair('宽屏与小屏',('checks/campus-card-wide-v21.png','2048×951'),('checks/campus-card-small-v21.png','1280×720'))
(r/'checks/review-v21.html').write_text(body);(r/'checks/review-v21-inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n')
