"""将确认稿中的地面控制点反投影为概念几何；只适用于平面，不推断真实地理或建筑高度。"""
import copy,hashlib,math
from pathlib import Path

def derive_city(plan):
 s=copy.deepcopy(plan['production']['city']);a=s.get('alignment')
 if not a:return s
 root=Path(__file__).resolve().parents[1]
 assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==a['generatorSha256'],'区域布局生成器版本不一致'
 def sub(x,y):return [i-j for i,j in zip(x,y)]
 def dot(x,y):return sum(i*j for i,j in zip(x,y))
 def norm(v):
  d=math.sqrt(dot(v,v));return [x/d for x in v]
 def cross(x,y):return [x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]]
 cam=s['camera'];eye=cam['eye'];forward=norm(sub(cam['target'],eye));right=norm(cross(forward,[0,0,1]));up=cross(right,forward)
 w,h=a['imageSize'];left=plan['design']['layout']['railFraction']*w;aspect=(w-left)/h;tan=math.tan(math.radians(cam['fov'])/2)
 def project(point,z=0):
  x,y=point;u=((x-left)/(w-left)*2-1)*aspect*tan;v=(1-y/h*2)*tan;d=[forward[i]+u*right[i]+v*up[i] for i in range(3)];t=(z-eye[2])/d[2];return [round(eye[i]+t*d[i],4) for i in range(2)]
 s['outline']=[project(p) for p in a['outlinePixels']]
 s['waterPolygons']=[[project(p) for p in poly] for poly in a['waterPixels']]
 s['zones']=[{'id':z['id'],'material':z['material'],'polygon':[project(p) for p in z['pixels']]} for z in a['zones']]
 s['parks']=[[project(p) for p in poly] for poly in a['greenPixels']]
 s['islands']=[]
 for idx,item in enumerate(a['islands']):
  x,y,rx,ry=item;pts=[]
  for i in range(24):
   theta=i*math.tau/24;k=1+.13*math.sin(theta*3+idx)+.08*math.sin(theta*7+idx*.5);pts.append(project([x+rx*k*math.cos(theta),y+ry*k*math.sin(theta)]))
  s['islands'].append(pts)
 s['arterials']=[{'points':[project(p) for p in path['pixels']],'width':path['width'],'bridge':path.get('bridge',False)} for path in a['roads']]
 s['campusPositionM']=[*project(a['campusPixel']),0]
 for poi in s['poi']:
  point=a['poiPixels'][poi['id']];height=poi['heightM'];poi['position']=[*project(point,height),height]
 s['coveragePolygon']=[project(p) for p in [[left-350,-350],[w+350,-350],[w+350,h+350],[left-350,h+350]]]
 s['extentM']=[24000,24000]
 s['buildingSites']=[project([x,y]) for y in range(-120,h+180,a['buildingGridPx'][1]) for x in range(int(left)-100,w+220,a['buildingGridPx'][0])]
 s['localRoads']=[[project(point) for point in path] for path in a['localRoadPixels']]
 s['projectionBasis']='确认稿平面控制点+当前制作相机的反投影估计；不是地理或高度测量'
 return s
