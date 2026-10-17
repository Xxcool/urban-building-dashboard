"""在全新目录复制固定输入、生成模型与网页、运行检查，记录可重复构建结果。"""
import argparse
import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--dest', type=Path, required=True)
parser.add_argument('--blender', default='/Applications/Blender.app/Contents/MacOS/Blender')
parser.add_argument('--cache', type=Path, required=True)
parser.add_argument('--report', default='checks/rebuild-report.json')
args = parser.parse_args()
dest = args.dest.resolve()
if dest.exists():
    raise SystemExit('目标目录已存在；请选择全新目录，脚本不会删除现有成果。')
dest.mkdir(parents=True)
for name in ['planning', 'scripts', 'design']:
    shutil.copytree(root / name, dest / name)
for name in ['src', 'tests']:
    shutil.copytree(root / 'app' / name, dest / 'app' / name)
for name in ['index.html', 'package.json', 'package-lock.json', 'vite.config.js']:
    shutil.copy2(root / 'app' / name, dest / 'app' / name)
steps = []
start = time.monotonic()
with (dest / 'rebuild.log').open('w') as log:
    def run(label, command, cwd):
        tick = time.monotonic()
        log.write('\n' + label + '\n'); log.flush()
        result = subprocess.run(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
        steps.append({'step': label, 'exitCode': result.returncode, 'seconds': round(time.monotonic() - tick, 2)})
        if result.returncode:
            raise RuntimeError(label + '失败，见' + str(dest / 'rebuild.log'))
    run('Blender从规划源生成', [args.blender, '-b', '--python', 'scripts/build_scene.py'], dest)
    run('Blender生成区域LOD', [args.blender, '-b', '--python', 'scripts/build_city.py'], dest)
    run('生成网页配置', ['python3', 'scripts/prepare_runtime.py'], dest)
    run('安装锁定依赖', ['npm', 'ci', '--legacy-peer-deps', '--no-audit', '--no-fund', '--cache', str(args.cache.resolve())], dest / 'app')
    run('道路水域边界回归', ['python3', 'scripts/test_city_geometry.py'], dest)
    run('业务契约测试', ['npm', 'test'], dest / 'app')
    run('生产构建', ['npm', 'run', 'build'], dest / 'app')
    run('实际资产契约核对', ['python3', 'scripts/verify_assets.py', '--report', 'checks/rebuilt-assets-contract.json'], dest)

    run('区域资产契约核对', ['python3', 'scripts/verify_city.py', '--report', 'checks/rebuilt-city-contract.json'], dest)

sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
comparisons = {}
for name in ['app/public/assets/campus.glb', 'app/public/assets/runtime.json','app/public/assets/city.glb']:
    comparisons[name] = {'original': sha(root / name), 'rebuilt': sha(dest / name)}
    comparisons[name]['identical'] = comparisons[name]['original'] == comparisons[name]['rebuilt']
report = {'result': 'passed' if all(c['identical'] for c in comparisons.values()) else 'different',
          'output': str(dest), 'seconds': round(time.monotonic() - start, 2), 'steps': steps,
          'comparisons': comparisons, 'log': str(dest / 'rebuild.log'),
          'notes': ['未复制旧GLB、blend、runtime、node_modules或dist；只复制规划、脚本、固定图像输入和前端源码。',
                    'blend包含保存路径等本机元数据，不要求二进制相同；实际GLB和网页配置做哈希比对。',
                    '网页交互和视觉需继续从本次dist实际打开核对。']}
(root / args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(report['result'] != 'passed')
