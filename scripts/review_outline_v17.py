"""生成边界实线与光晕修复的完整画面对照，不修改任何输入图片。"""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
images=[('设计基准','design/screens/city-no-data-design-v1.png'),('修正前：白色过亮','checks/city-no-data-v14c.jpg'),('修正后：青蓝实线与柔和外晕','checks/city-outline-v17.png')]
figures=''.join(f'<figure><img src="../{path}"><figcaption>{title}</figcaption></figure>' for title,path in images)
(root/'checks/outline-review-v17.html').write_text('<!doctype html><meta charset="utf-8"><title>区域边界 v17 对照</title><style>body{font:16px/1.7 system-ui;background:#f4f3ee;color:#123b40;margin:24px}main{display:grid;grid-template-columns:1fr 1fr;gap:20px}figure{margin:0}img{width:100%;height:auto}figcaption{padding:12px}</style><h1>区域边界 v17 专项修复</h1><p>1920×1080，区域总览，无数据状态，默认相机。图片保持各自原比例，无裁剪；设计稿为1672×941。白色高亮核心改为青蓝实线；浅色衬边与渐弱外晕保留，Bloom单独绘制并降低合成量。边界作为区域标识保持在地形、水体与楼宇前，避免遮断。</p><p>局部修复已实际构建与浏览器复核。颜色与柔光仍待用户评审；城市真实性R-05-REALISM继续开放。入场动效、其他楼宇信息卡提案尚未实施。</p><main>'+figures+'</main>')
(root/'checks/outline-review-v17-inputs.json').write_text(json.dumps([{'path':path,'sha256':hashlib.sha256((root/path).read_bytes()).hexdigest()} for _,path in images],ensure_ascii=False,indent=2))
print('outline review generated')
