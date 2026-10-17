"""为每个实际网页版本生成并排对照；只引用原图，不裁切、拉伸或修改设计基准。"""
import argparse
import hashlib
import html
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--version', required=True)
parser.add_argument('--review', required=True)
args = parser.parse_args()
p = json.loads((root / 'planning/project.json').read_text())
review = json.loads((root / args.review).read_text())
panels = []
records = []
for level in [item['id'] for item in p['levels']]:
    baseline = root / p['design']['baselines'][level]['selected-A1']['path']
    actual = root / f'checks/{level}-detailed-{args.version}.jpg'
    if not actual.exists():
        continue
    records.append({'level': level, 'baseline': str(baseline.relative_to(root)),
                    'baselineSha256': hashlib.sha256(baseline.read_bytes()).hexdigest(),
                    'actual': str(actual.relative_to(root)), 'actualSha256': hashlib.sha256(actual.read_bytes()).hexdigest()})
    panels.append(f'<h2>{ {"city":"区域总览","campus":"园区总览","building":"重点楼宇"}[level] }</h2><div class="pair"><figure><img src="../{baseline.relative_to(root)}"><figcaption>已确认整屏基准 · {baseline.name}</figcaption></figure><figure><img src="{actual.name}"><figcaption>实际网页 · {args.version} · {review["viewport"]}</figcaption></figure></div>')
rows = ''.join('<tr>' + ''.join('<td>' + html.escape(str(item.get(key, ''))) + '</td>' for key in ['id', 'expected', 'actual', 'cause', 'sourceChange', 'evidence', 'result', 'next']) + '</tr>' for item in review['differences'])
content = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>B方案逐版对照 {args.version}</title><style>
body{{margin:0;padding:28px;background:#f4f3ee;color:#123b40;font:15px/1.7 system-ui,sans-serif}}h1{{font-size:28px}}h2{{margin-top:32px}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}figure{{margin:0;background:white;border:1px solid #d7e1df;border-radius:8px;overflow:hidden}}img{{display:block;width:100%;height:auto}}figcaption{{padding:10px 14px}}table{{border-collapse:collapse;width:100%;background:#fffefa}}th,td{{padding:12px;border:1px solid #cfdbd7;vertical-align:top;min-width:100px}}.table{{overflow:auto}}pre{{white-space:pre-wrap;word-break:break-all;font-size:12px}}@media(max-width:800px){{.pair{{grid-template-columns:1fr}}}}
</style><h1>B方案 · {args.version} 实际网页与确认基准</h1><p>{html.escape(review['conditions'])}</p><p>两图保留原始比例，AI图不具备测绘精度；对照不把AI不可数细节当作工程数据。浏览器截图是实际WebGL画面。</p>{''.join(panels)}<h2>差异与复验</h2><div class="table"><table><tr><th>ID</th><th>预期</th><th>实际</th><th>原因假设</th><th>源修改</th><th>重建/复验证据</th><th>结果</th><th>后续</th></tr>{rows}</table></div><h2>输入哈希</h2><pre>{html.escape(json.dumps(records,ensure_ascii=False,indent=2))}</pre></html>'''
out = root / f'checks/comparison-{args.version}.html'
out.write_text(content)
(root / f'checks/comparison-{args.version}-inputs.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
print(out)
