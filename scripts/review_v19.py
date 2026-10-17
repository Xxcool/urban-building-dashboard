"""生成本轮整屏与设计、前版的并排对照，保留原图比例与失败迭代证据。"""
from pathlib import Path
import json,hashlib,html
r=Path(__file__).resolve().parents[1];p=json.loads((r/'planning/project.json').read_text())
blocks=[];inputs=[]
def picture(path,title):
 f=r/path;inputs.append({'path':path,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()});return f'<figure><img src="../{path}"><figcaption>{html.escape(title)}</figcaption></figure>'
for level,name in [('city','城市'),('campus','园区'),('building','A1楼宇')]:
 base=p['design']['baselines'][level]['selected-A1']['path'];actual=f'checks/{level}-final-v19.png'
 blocks.append(f'<h2>{name}整屏</h2><div class="pair">'+picture(base,'已确认设计基准')+picture(actual,'实际网页 · 1920×1080 · 演示数据 · 默认相机')+'</div>')
blocks.append('<h2>城市修改前后</h2><div class="pair">'+picture('checks/city-fullpage-v18.png','前版：底部狭长连湖，边界较粗')+picture('checks/city-final-v19.png','本轮：双湖、细实线与外晕、岸线林带')+'</div>')
blocks.append('<h2>当前选中楼宇与缺失状态</h2><div class="pair">'+picture('checks/campus-C1-v19.png','C1演示指标，左侧与卡片同步')+picture('checks/campus-C1-empty-v19.png','C1无数据：保持身份，指标显示—')+'</div>')
blocks.append('<h2>实际入场阶段截图</h2><div class="pair">'+''.join(picture(f'checks/entrance-{phase}-v19.png',title) for phase,title in [('city','城市展开'),('boundary','边界开始描绘'),('park','园区定位阶段'),('complete','完整终态')])+'</div>')
body='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>v19整屏复核</title><style>body{font:15px/1.7 system-ui;background:#f4f3ee;color:#123b40;padding:24px;margin:0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0 0 18px;background:#fff}img{width:100%;height:auto;display:block}figcaption{padding:10px}h2{margin-top:34px}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><h1>v19 · 整屏与逐项复核</h1><p>所有图片保留原始比例，不裁切、不拉伸；确认基准未改。正常数据，默认相机；车辆按实际截图时刻运动。阶段图为网页实拍，不以四帧替代动态交互检查。</p><p>DATA-19：各栋经营演示指标补齐，左右同源；汇总守恒与缺失态测试通过。LAKE-19：两片湖泊及平滑岸线包含关系通过。MOTION-19：统一时间线、重播及返回逻辑通过；减弱动效有单元测试，未修改系统设置实测。LINE-19：蓝色细线与模糊光晕分离，已逐版截图复核。前版v19a湖面顶点色导出异常，v19c光晕过强，原证据保留，最终修正后重新导出。</p><p>R-05-REALISM仍开放：道路与街区密度/层级、建筑个体差异、水体及湖岸景观精细度仍比原设计简化。工程检查通过不等于整体视觉通过。资源及性能见runtime-v19.json，硬件与长时限制见iteration-v19.md。</p>'''
(r/'checks/review-v19.html').write_text(body+''.join(blocks)+'</html>')
(r/'checks/review-v19-inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n')
print('review-v19.html generated')
