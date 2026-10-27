"""从唯一规划源生成示意区域、简化构图或细化城市GLB；不读取或伪造真实地理数据。"""
import argparse,hashlib,json,math,random,sys
from pathlib import Path
from collections import defaultdict
import bpy,bmesh
sys.path.insert(0,str(Path(__file__).resolve().parent))
from city_layout import derive_city
from city_geometry import clear_surface,densify
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
p=argparse.ArgumentParser();p.add_argument('--gray',action='store_true');p.add_argument('--output-root',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[1];out=a.output_root.resolve() if a.output_root else root
raw=(root/'planning/project.json').read_bytes();plan=json.loads(raw);s=derive_city(plan);rng=random.Random(s['seed'])
bpy.context.preferences.filepaths.save_version=0;bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def linear(h):
 v=[int(h[i:i+2],16)/255 for i in (1,3,5)];return [x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v]
mats={}
for k,h in s['palette'].items():
 m=bpy.data.materials.new('city_'+k);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*linear(h),1);b.inputs['Roughness'].default_value=.77 if k!='water' else .25;b.inputs['Metallic'].default_value=.12 if k in ['water','glass','bronze'] else 0;mats[k]=m
# 固定透明叶簇直接复用项目已记录的AI输入，不把概念整图烘进模型。
foliage=plan['production']['materialInputs']['foliage'];leaf_path=root/foliage['path'];assert hashlib.sha256(leaf_path.read_bytes()).hexdigest()==foliage['sha256']
image=bpy.data.images.load(str(leaf_path));image.pack();leaf=bpy.data.materials.new('city_leafCard');leaf.use_nodes=True;bsdf=leaf.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.9;tex=leaf.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;leaf.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);leaf.node_tree.links.new(tex.outputs['Alpha'],bsdf.inputs['Alpha']);leaf.surface_render_method='DITHERED';mats['leafCard']=leaf
class Batch:
 def __init__(self,name,parent=None):self.name=name;self.parent=parent;self.parts=defaultdict(lambda:([],[]))
 def add(self,verts,faces,mat):
  v,f=self.parts[mat];n=len(v);v.extend(verts);f.extend(tuple(n+i for i in face) for face in faces)
 def box(self,x,y,z,w,d,h,mat,angle=0):
  c,t=math.cos(angle),math.sin(angle);vs=[]
  for zz in [-h/2,h/2]:
   for xx,yy in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]:vs.append((x+c*xx-t*yy,y+t*xx+c*yy,z+zz))
  self.add(vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
 def poly(self,points,z,mat):
  vs=[Vector((x,y,z)) for x,y in points];tri=tessellate_polygon([vs]);self.add([tuple(v) for v in vs],tri,mat)
 def strip(self,points,width,z,mat):
  for (x,y),(xx,yy) in zip(points,points[1:]):
   length=math.hypot(xx-x,yy-y);nx,ny=-(yy-y)/length*width/2,(xx-x)/length*width/2;self.add([(x-nx,y-ny,z),(xx-nx,yy-ny,z),(xx+nx,yy+ny,z),(x+nx,y+ny,z)],[(0,1,2,3)],mat)
 def tree(self,x,y,h,r):
  # 实体低面数树冠参与光照与阴影，消除远景交叉叶片卡的星形轮廓。
  self.add([(x-r*.06,y,0),(x+r*.06,y,0),(x+r*.06,y,h*.6),(x-r*.06,y,h*.6),(x,y-r*.06,0),(x,y+r*.06,0),(x,y+r*.06,h*.6),(x,y-r*.06,h*.6)],[(0,1,2,3),(4,5,6,7)],'trunk')
  phi=(1+math.sqrt(5))/2;raw=[(-1,phi,0),(1,phi,0),(-1,-phi,0),(1,-phi,0),(0,-1,phi),(0,1,phi),(0,-1,-phi),(0,1,-phi),(phi,0,-1),(phi,0,1),(-phi,0,-1),(-phi,0,1)]
  faces=[(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),(5,11,4),(11,10,2),(10,7,6),(7,1,8),(3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1)]
  angle=rng.random()*math.tau;c,t=math.cos(angle),math.sin(angle);norm=math.sqrt(1+phi*phi)
  verts=[(x+(vx*c-vy*t)/norm*r,y+(vx*t+vy*c)/norm*r,h*.67+vz/norm*h*.32*rng.uniform(.86,1.13)) for vx,vy,vz in raw]
  self.add(verts,faces,'leafLight' if rng.random()<.35 else 'leaf')
 def finish(self):
  for mat,(v,f) in self.parts.items():
   mesh=bpy.data.meshes.new(self.name+'_'+mat);mesh.from_pydata(v,[],f);mesh.materials.append(mats[mat]);mesh.update();
   if mat in ['water','waterDeep']:
    # 湖面补内部顶点并按真实岸线距离着色，避免整片水体只有一种纯色。
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=2,use_grid_fill=True);bm.to_mesh(mesh);bm.free()
    colors=mesh.color_attributes.new(name='LakeDepth',type='FLOAT_COLOR',domain='POINT')
    for vertex in mesh.vertices:
     x,y=vertex.co.x,vertex.co.y;distance=1e9
     for poly in lake_polygons:
      for (ax,ay),(bx,by) in zip(poly,poly[1:]+poly[:1]):
       dx,dy=bx-ax,by-ay;t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/max(dx*dx+dy*dy,.001)));distance=min(distance,math.hypot(x-ax-t*dx,y-ay-t*dy))
     depth=1-math.exp(-distance/55);base=linear(s['palette'][mat]);colors.data[vertex.index].color=(*[base[i]*[1.12-.35*depth,1.13-.22*depth,1.0-.05*depth][i] for i in range(3)],1)
    shader=mats[mat].node_tree;bsdf=shader.nodes.get('Principled BSDF');attribute=shader.nodes.new('ShaderNodeVertexColor');attribute.layer_name='LakeDepth';shader.links.new(attribute.outputs['Color'],bsdf.inputs['Base Color'])
   if mat in ['leaf','leafLight']:

    for polygon in mesh.polygons:polygon.use_smooth=True
   if mat in ['leafCard','water','waterDeep']:
    uv=mesh.uv_layers.new(name='SurfaceUV')
    for polygon in mesh.polygons:
     for lid in polygon.loop_indices:
      v=mesh.vertices[mesh.loops[lid].vertex_index].co
      uv.data[lid].uv=(v.x/90,v.y/90) if mat!='leafCard' else [(0,0),(1,0),(1,1),(0,1)][list(polygon.loop_indices).index(lid)]
   obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(obj)
   if self.parent:obj.parent=self.parent

def rootnode(name):
 obj=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(obj);return obj
region=rootnode('region_'+plan['demoDesign']['region']['id']);region['schematic']=True
# 城市地面延伸到视口之外，去掉v13可见的矩形沙盘边缘。
land=Batch('regional_terrain',region);extent=[s['context']['radiusM']*3]*2;land.box(0,0,-6,*extent,10,'ground');land.poly(s['outline'],.2,'zoneGreen')
for zone in s['zones']:
 if zone['id']!='REGION-TINT':land.poly(zone['polygon'],.5 if zone['material']=='zoneCyan' else .7,zone['material'])
def smooth(points,steps=5,closed=True):
 output=[];n=len(points)
 for k in range(n if closed else n-1):
  p0=points[(k-1)%n] if closed or k>0 else points[0];p1=points[k];p2=points[(k+1)%n];p3=points[(k+2)%n] if closed or k+2<n else points[-1]
  for i in range(steps):
   t=i/steps;t2=t*t;t3=t2*t;output.append(tuple(.5*((2*p1[j])+(-p0[j]+p2[j])*t+(2*p0[j]-5*p1[j]+4*p2[j]-p3[j])*t2+(-p0[j]+3*p1[j]-3*p2[j]+p3[j])*t3) for j in range(2)))
 if not closed:output.append(tuple(points[-1]))
 return output
for poly in s['parks']:land.poly(smooth(poly),.6,'grass')
lake_polygons=[smooth(poly) for poly in s['waterPolygons']];island_polygons=[smooth(poly,3) for poly in s['islands']]
for poly in lake_polygons:
 cx=sum(x for x,y in poly)/len(poly);cy=sum(y for x,y in poly)/len(poly)
 land.poly([(cx+(x-cx)*1.025,cy+(y-cy)*1.025) for x,y in poly],.9,'shore');land.poly(poly,1.4,'water');land.poly([(cx+(x-cx)*.97,cy+(y-cy)*.97) for x,y in poly],1.55,'waterDeep')
for poly in island_polygons:land.poly(poly,2.1,'shore');land.poly(poly,2.3,'grass')
land.finish()
def inside(x,y,poly):
 hit=False
 for (ax,ay),(bx,by) in zip(poly,poly[1:]+poly[:1]):
  if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:hit=not hit
 return hit
def island(x,y):return any(inside(x,y,poly) for poly in island_polygons)
def water(x,y):return any(inside(x,y,poly) for poly in lake_polygons) and not island(x,y)
def segment_distance(x,y,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/max(dx*dx+dy*dy,.001)));return math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)
road_paths=[(densify(smooth(p['points'],12,False)),p['width'],p['bridge']) for p in s['arterials']]+[(densify(smooth(points,8,False)),9,False) for points in s['localRoads']]
# 路面裁切后仍使用原主干线留建筑退界；普通街道不能有任何边缘跨入水域。
road_lines=[(p['points'],p['width']) for p in s['arterials']]+[(p,9) for p in s['localRoads']]
def road_distance(x,y):return min(segment_distance(x,y,a,b)-width/2 for path,width in road_lines for a,b in zip(path,path[1:]))
roads=Batch('regional_roads',region);bridges=Batch('regional_bridges',region);road_audit=[];bridge_count=0
for points,width,bridge in road_paths:
 previous_bridge=False
 for index,(a1,a2) in enumerate(zip(points,points[1:])):
  dry=clear_surface(a1,a2,width+9,lake_polygons)
  if not dry and not bridge:continue
  z=7 if bridge else 3.3
  roads.strip([a1,a2],width+5,z-.3,'marking');roads.strip([a1,a2],width,z,'road')
  if width>15:roads.strip([a1,a2],.7,z+.15,'marking')
  road_audit.append({'a':a1,'b':a2,'width':width+5,'bridge':not dry})
  if not dry:
   # 仅规划的两条跨湖主路允许形成桥梁；栏杆、桥面侧梁和桥墩使跨水关系可辨认。
   length=math.dist(a1,a2);nx,ny=-(a2[1]-a1[1])/length,(a2[0]-a1[0])/length
   for sign in [-1,1]:
    edge=[(x+nx*(width/2+1)*sign,y+ny*(width/2+1)*sign) for x,y in [a1,a2]]
    bridges.strip(edge,1.1,z+1.7,'roof');bridges.strip(edge,1.7,z-1.2,'building')
   if index%6==0:bridges.box(a1[0],a1[1],3,3.5,3.5,8,'building')
   if not previous_bridge:bridge_count+=1
  previous_bridge=not dry
bridges.finish()
walks=Batch('regional_lake_walks',region)
for poly in lake_polygons:
 cx=sum(x for x,y in poly)/len(poly);cy=sum(y for x,y in poly)/len(poly)
 path=[(cx+(x-cx)*1.065,cy+(y-cy)*1.065) for x,y in poly];path.append(path[0])
 for a1,a2 in zip(path,path[1:]):
  if clear_surface(a1,a2,5,lake_polygons):walks.strip([a1,a2],3.5,2.8,'marking')
walks.finish()
roads.finish()
cp=s['campusPositionM'];pw,pd=plan['production']['site']['parkSize'];scale=s['campusScale']
def in_campus(x,y,margin=0):return abs(x-cp[0])<pw*scale/2+margin and abs(y-cp[1])<pd*scale/2+margin
park=rootnode('city_PARK-DEMO');park['regionObjectId']='PARK-DEMO';park.location=cp;park.scale=(scale,scale,scale)
campus=Batch('regional_campus',park);campus.box(0,0,1,pw+24,pd+24,1,'campus');campus.box(0,0,2,pw,pd,1,'grass')
campus.strip([(-pw/2,-pd/2),(pw/2,-pd/2),(pw/2,pd/2),(-pw/2,pd/2),(-pw/2,-pd/2)],7,4,'boundaryRim')
for identity in plan['demoDesign']['buildingIdentities']:
 id=identity['id'];g=plan['production']['geometryById'][id];x,y,_=g['position'];fh=plan['production']['floorHeightM']
 if g.get('podiumSizes'):
  for i,(w,d) in enumerate(g['podiumSizes']):campus.box(x,y,4+(i+.5)*fh,w,d,fh,'building');campus.box(x,y,4+(i+1)*fh,w+1,d+1,.5,'roof')
  w,d=g['towerSize'];dx,dy=g['towerOffset'];h=plan['demoDesign']['focusBuilding']['floorsDefinition']['towerAbovePodium']*fh;z=4+3*fh
  campus.box(x+dx,y+dy,z+h/2,w,d,h,'glass');campus.box(x+dx,y+dy,z+h+1,w+1,d+1,2,'roof')
  if not a.gray:
   for i in range(22):campus.box(x+dx,y+dy,z+i*fh,w+.7,d+.7,.55,'building')
   for yy in range(-18,19,5):campus.box(x+dx+w/2+.8,y+dy+yy,z+h/2,1.3,.65,h,'bronze')
 else:
  w,d,h=g['size'];campus.box(x,y,4+h/2,w,d,h,'glass');campus.box(x,y,5+h,w+1,d+1,2,'roof')
  if not a.gray:
   for z in range(4,int(h)+4,5):campus.box(x,y,z,w+.7,d+.7,.6,'building')
campus.finish()
for item in s['poi']:
 anchor=rootnode('city_anchor_'+item['id']);anchor.location=item['position'];anchor['regionObjectId']=item['id'];anchor['role']='anchor'
if not a.gray:
 city=Batch('regional_buildings',region);b=s['buildings'];n=0;occupied=[]
 for index,(cx,cy) in enumerate(s['buildingSites']):
  # 每组使用连贯的沿街排布和一致朝向，混合住宅条板、办公裙房与少量塔楼。
  angle=(-.16 if index%3 else .12);pitch=b['pitchM'];rows=b['blockRows'];columns=b['blockColumns']
  for row in range(rows):
   for col in range(columns):
    xx,yy=(col-(columns-1)/2)*pitch,(row-(rows-1)/2)*pitch;x=cx+xx*math.cos(angle)-yy*math.sin(angle);y=cy+xx*math.sin(angle)+yy*math.cos(angle)
    w=rng.uniform(*b['widthM']);d=rng.uniform(*b['depthM']);h=rng.uniform(*b['heightM'])
    # 检查整栋包络与岸边缓冲，不把建筑中心在陆地误认为整栋不侵入湖泊。
    clearance=math.hypot(w,d)/2+b['lakeBufferM']
    shore_distance=min(segment_distance(x,y,a,b) for poly in lake_polygons for a,b in zip(poly,poly[1:]+poly[:1]))
    if water(x,y) or island(x,y) or any(inside(x,y,poly) for poly in s['parks']) or shore_distance<clearance or in_campus(x,y,60) or road_distance(x,y)<max(w,d)*.5+8:continue
    mat='buildingWarm' if any(z['material']=='zoneGold' and inside(x,y,z['polygon']) for z in s['zones']) else 'building'
    if index%5==0:h*=1.2;d*=.7
    city.box(x,y,h/2+1,w,d,h,mat,angle);city.box(x,y,h+1,w+1.5,d+1.5,1.8,'roof',angle)
    # 连续街区有退台、屋顶设备和檐口，避免全部表现为同一白盒。
    if index%3==0:city.box(x+2,y,h+4,w*.42,d*.48,5,'building',angle)
    else:city.box(x,y,h+2,w*.23,d*.2,2.2,'roof',angle)
    if index%4==0:
     city.box(x,y,5,w*1.35,d*1.12,8,mat,angle)
    for z in range(12,int(h),14):city.box(x,y,z,w+.5,d+.5,.45,'roof',angle)
    occupied.append((x,y,w/2,d/2));n+=1
 city.finish()
 trees=Batch('regional_landscape',region);count=0
 # 优先沿湖、岛屿和街区绿带成簇布置，避免均匀随机撒点。
 centers=[]
 for poly in island_polygons:centers.extend(poly[::4])
 for poly in lake_polygons:centers.extend(poly[::7])
 for poly in s['parks']:
  centers.extend(poly*5);centers.extend([(sum(x for x,y in poly)/len(poly),sum(y for x,y in poly)/len(poly))]*15)
 centers.extend(s['buildingSites'][::3])
 for i in range(s['trees']['count']*5):
  cx,cy=centers[i%len(centers)];x,y=cx+rng.gauss(0,55),cy+rng.gauss(0,40)
  if water(x,y) or in_campus(x,y,8) or road_distance(x,y)<7:continue
  if any(abs(x-bx)<w+5 and abs(y-by)<d+5 for bx,by,w,d in occupied):continue
  trees.tree(x,y,rng.uniform(*s['trees']['heightM']),rng.uniform(*s['trees']['radiusM']));count+=1
  if count>=s['trees']['count']:break
 trees.finish()
else:n=0;count=0
# 连续低细节城市覆盖缩远可见范围，按多个偏转街区组织，避免复制一个巨大棋盘。
context=Batch('regional_context',region);green=Batch('regional_context_greens',region);context_roads=Batch('regional_context_roads',region)
crng=random.Random(s['context']['seed']);pitch=s['context']['districtPitchM'];radius=s['context']['radiusM'];context_count=0
for iy in range(-math.ceil(radius/pitch),math.ceil(radius/pitch)+1):
 for ix in range(-math.ceil(radius/pitch),math.ceil(radius/pitch)+1):
  cx=ix*pitch+crng.uniform(-160,160);cy=iy*pitch+crng.uniform(-160,160);distance=math.hypot(cx,cy)
  if distance<s['context']['innerRadiusM'] or distance>radius:continue
  if any(inside(cx,cy,poly) for poly in lake_polygons):continue
  angle=.38*math.sin(ix*1.7)+.34*math.cos(iy*.8);c,si=math.cos(angle),math.sin(angle)
  def world(x,y):return (cx+x*c-y*si,cy+x*si+y*c)
  # 每组短街道有不同偏角与支路；分组绿地形成连续中景，不给重点区域添网格。
  path=densify([world(-pitch*.58,-230),world(0,-180),world(pitch*.58,-210)],45)
  for aa,bb in zip(path,path[1:]):
   if clear_surface(aa,bb,34,lake_polygons):
    context_roads.strip([aa,bb],30,2.5,'road');road_audit.append({'a':aa,'b':bb,'width':30,'bridge':False})
  middle=distance<s['context']['middleRadiusM']
  district_count=s['context']['middleBuildingsPerDistrict'] if middle else s['context']['buildingsPerDistrict']
  for j in range(district_count):
   xx=(j%6-2.5)*155+crng.uniform(-65,65);yy=(j//6)*230-80+crng.uniform(-65,65)
   x,y=world(xx,yy);w=crng.uniform(50,100);d=crng.uniform(60,130);h=crng.uniform(45,145)*(1 if middle else .7)
   if any(inside(x,y,poly) for poly in s['parks']) or not clear_surface((x-w/2,y),(x+w/2,y),d+70,lake_polygons):continue
   if distance<4200 and any(abs(x-bx)<bw+100 and abs(y-by)<bd+100 for bx,by,bw,bd in occupied):continue
   context.box(x,y,h/2,w,d,h,'building',angle)
   context.poly([(x+dx*c-dy*si,y+dx*si+dy*c) for dx,dy in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]],h+.1,'roof')
   if j%4==0:context.box(x,y,h+4,w*.48,d*.4,6,'building',angle)
   context_count+=1
  if middle:
   for j in range(s['context']['middleTreesPerDistrict']):
    x,y=world(crng.uniform(-490,490),crng.choice([-285,680])+crng.uniform(-35,35))
    if clear_surface((x-15,y),(x+15,y),30,lake_polygons):green.tree(x,y,crng.uniform(18,28),crng.uniform(12,19))
   side=densify(smooth([world(-510,720),world(-450,460),world(-320,150),world(-250,-190)],8,False),35)
   for aa,bb in zip(side,side[1:]):
    if clear_surface(aa,bb,26,lake_polygons):
     context_roads.strip([aa,bb],22,2.5,'road');road_audit.append({'a':aa,'b':bb,'width':22,'bridge':False})
  gx,gy=world(320,340)
  if clear_surface((gx-120,gy),(gx+120,gy),160,lake_polygons):green.poly([world(180,250),world(460,250),world(460,430),world(180,430)],.4,'grass')
context.finish();green.finish();context_roads.finish()
(out/'checks').mkdir(parents=True,exist_ok=True)
(out/'checks/city-road-surfaces.json').write_text(json.dumps({'roads':road_audit,'lakes':lake_polygons,'bridgeSpans':bridge_count,'contextBuildings':context_count},ensure_ascii=False))
cam=s['camera'];data=bpy.data.cameras.new('city_camera');obj=bpy.data.objects.new('city_camera',data);bpy.context.collection.objects.link(obj);obj.location=cam['eye'];obj.rotation_euler=(Vector(cam['target'])-obj.location).to_track_quat('-Z','Y').to_euler();data.sensor_fit='VERTICAL';data.sensor_height=36;data.lens=36/(2*math.tan(math.radians(cam['fov']/2)));bpy.context.scene.camera=obj
quality='gray' if a.gray else 'detailed';glb=out/s['assets']['grayScene' if a.gray else 'scene'];blend=out/('assets/city-gray.blend' if a.gray else s['assets']['blend']);glb.parent.mkdir(parents=True,exist_ok=True);blend.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(blend));pending=glb.with_name('.'+glb.stem+'-pending.glb');bpy.ops.export_scene.gltf(filepath=str(pending),export_format='GLB',export_yup=True,export_extras=True,export_cameras=False);pending.replace(glb)
info={'quality':quality,'planningSha256':hashlib.sha256(raw).hexdigest(),'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'asset':glb.name,'assetSha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'bytes':glb.stat().st_size,'triangles':sum(len(p.vertices)-2 for obj in bpy.data.objects if obj.type=='MESH' for p in obj.data.polygons),'decorativeBuildings':n,'trees':count,'contextBuildings':context_count,'bridgeSpans':bridge_count,'regionObjectIds':[item['id'] for item in s['poi']],'scope':'概念区域；装饰建筑不等于真实楼宇数据','blender':bpy.app.version_string}
(out/'public/assets/city-build-info.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n');(out/('assets/city-manifest-gray.json' if a.gray else 'assets/city-manifest.json')).write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n');print('CITY_BUILD_RESULT',json.dumps(info,ensure_ascii=False))
