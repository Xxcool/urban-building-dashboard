"""只从当前规划和已确认终稿派生城市制作规格，旧坐标明确标为待重校。"""
from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parents[1];raw=(r/'planning/project.json').read_bytes();p=json.loads(raw);s=p['production']['city']
text='# 当前城市制作规格\n\n唯一规划SHA-256：'+hashlib.sha256(raw).hexdigest()+'\n\n唯一视觉终稿：../design/final/city.png，用户确认见../design/final/approval.md。\n\nv26已按唯一终稿重新标注边界、南部完整水系、道路与园区控制点，经Blender MCP制作并烘焙地面AO；重标控制点不等于写实程度已通过视觉验收。湖泊、路网与坐标均为虚构概念，不是测绘资料。\n\n城市独立使用city.glb；园区和楼宇共用campus.glb，业务楼宇身份与指标仍从唯一规划读取。后续先验证新终稿下的投影、区域包含关系与界面占位，再深化材质与建筑。\n\n```json\n'+json.dumps(s,ensure_ascii=False,indent=2)+'\n```\n'
(r/'docs/city-production-current.md').write_text(text)
