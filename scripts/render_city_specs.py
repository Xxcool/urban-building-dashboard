"""从唯一规划源派生区域制作规格，避免重复维护尺寸和相机。"""
from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parents[1];raw=(r/'planning/project.json').read_bytes();p=json.loads(raw);s=p['production']['city']
text='# 区域制作规格 '+p['production']['version']+'\n\n唯一规划SHA-256：'+hashlib.sha256(raw).hexdigest()+'\n\n尺寸、相机与湖泊道路均为概念视觉估计，无真实地理对应。区域布局沿用已确认B-city-v1，原8栋规格从同一production.geometryById复用。城市LOD不计入区域楼宇运营总数。\n\n```json\n'+json.dumps(s,ensure_ascii=False,indent=2)+'\n```\n\n画布1920×1080，左28%面板、右72%场景。简化构图门槛checks/city-gray-gate-v3.md在细化前完成；锚点与区域轮廓实际投影见city-gray-target-v3.json。后续仅增加装饰楼群、树冠与材质，未改变通过的相机和主要锚点。无数据态园区入口保持可用，指标只读取demoDesign.campus；缺失值不归零。\n\n资产：独立city.glb，园区/楼宇共用campus.glb；所有脚本和版本由构建清单核对。初版9.59MB及第二版8.26MB超预算，已优化道路平面及树冠共享顶点；当前实际体积和三角形见city-assets-contract-v13.json。\n'
(r/'docs/city-production-spec-v13-final.md').write_text(text)
