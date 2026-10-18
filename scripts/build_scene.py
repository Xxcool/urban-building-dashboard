"""Blender脚本：从唯一规划源生成简化/细化场景、业务根节点、GLB与构建清单。"""
import argparse
import hashlib
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

import bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument('--gray', action='store_true')
parser.add_argument('--landscape-layout', action='store_true', help='仅生成景观构图简模，必须使用独立output-root')
parser.add_argument('--output-root', type=Path)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
SOURCE_ROOT = Path(__file__).resolve().parents[1]
OUT = args.output_root.resolve() if args.output_root else SOURCE_ROOT
if args.landscape_layout and not args.output_root:raise SystemExit('景观简模必须指定独立输出目录')
sys.path.insert(0,str(SOURCE_ROOT/'scripts'))
from campus_landscape import build_landscape,clipped_path,is_facility_clear
raw = (SOURCE_ROOT / 'planning/project.json').read_bytes()
plan = json.loads(raw)
spec = plan['production']
rng = random.Random(spec['site']['seed'])
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in list(bpy.data.materials):
    bpy.data.materials.remove(block)

def color(value):
    value = value.lstrip('#')
    srgb = [int(value[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in srgb)

landscape_spec=spec.get('landscape')
materials = {}
wall_input=spec.get('materialInputs',{}).get('curtainWall')
wall_image=None
if wall_input:
    wall_path=SOURCE_ROOT/wall_input['path']
    assert hashlib.sha256(wall_path.read_bytes()).hexdigest()==wall_input['sha256'], '幕墙固定输入哈希不一致'
    wall_image=bpy.data.images.load(str(wall_path));wall_image.pack()
foliage_input=spec.get('materialInputs',{}).get('foliage')
foliage_image=None
if foliage_input:
    foliage_path=SOURCE_ROOT/foliage_input['path']
    assert hashlib.sha256(foliage_path.read_bytes()).hexdigest()==foliage_input['sha256'], '叶簇固定输入哈希不一致'
    foliage_image=bpy.data.images.load(str(foliage_path));foliage_image.pack()
    alpha=[foliage_image.pixels[i*4+3] for i in range(0,foliage_image.size[0]*foliage_image.size[1],4096)]
    assert min(alpha)<.1 and max(alpha)>.9, '叶簇必须包含真实透明与实体区域'
for name, hex_color, metal, rough in [
    ('stone','#e0e0d5',0.02,0.65),('frame','#d6dcdb',0.35,0.35),
    ('glass','#7495a6',0.48,0.2),('glassLight','#9eb3bd',0.4,0.28),
    ('interior','#b49a76',0.14,0.5),('bronze','#9c7b50',0.62,0.32),
    ('roof','#68797a',0.12,0.7),('paving','#d0cfc2',0,0.9),
    ('path','#e5dfd0',0,0.9),('road','#7e878b',0,0.95),
    ('marking','#e5e3d8',0,0.9),('grass','#99a77b',0,0.95),
    ('leaves','#71865b',0,0.92),('leavesLight','#91a270',0,0.92),
    ('leavesDark','#536e4b',0,0.92),('bark','#796953',0,0.95),
    ('pink','#c9a3a6',0,0.95),('city','#d9dfe0',0.02,0.75),
    ('cityLight','#e3e5df',0.01,0.8),('car','#e6e6df',0.2,0.35),
    ('carDark','#506577',0.5,0.3),('dark','#3b484d',0.1,0.65),
    ('vehicleGlass','#253e49',0.35,0.18),('tailLamp','#c94e46',0.1,0.3),('gray','#b5bfc2',0.05,0.75),('leavesCard','#ffffff',0,0.88)]:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color(plan['design']['palette'].get(name,hex_color)), 1)
    bsdf.inputs['Metallic'].default_value = metal
    bsdf.inputs['Roughness'].default_value = rough
    if name.startswith('glass'):
        bsdf.inputs['Coat Weight'].default_value = 0.35
    if name=='glass' and wall_image:
        tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=wall_image;tex.extension='REPEAT'
        mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
        bsdf.inputs['Metallic'].default_value=.22;bsdf.inputs['Roughness'].default_value=.28
    if name=='leavesCard' and foliage_image:
        tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=foliage_image
        mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
        mat.node_tree.links.new(tex.outputs['Alpha'],bsdf.inputs['Alpha'])
        mat.use_backface_culling=False;mat.surface_render_method='DITHERED'
    materials[name] = mat

if landscape_spec:
    for name,value in {**landscape_spec['palette'],'skin':'#bca38b'}.items():
        mat=bpy.data.materials.new(name);mat.use_nodes=True;bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(*color(value),1);bsdf.inputs['Roughness'].default_value=.24 if name=='water' else .82;bsdf.inputs['Metallic'].default_value=.22 if name in ['metal','water'] else .0;materials[name]=mat

class Batch:
    # 同一业务对象内按材质合批；不合并不同楼栋的可拾取身份。
    def __init__(self, name, parent=None):
        self.name, self.parent = name, parent
        self.data = defaultdict(lambda: [[], []])

    def box(self, center, size, mat):
        verts, faces = self.data[mat]
        x,y,z = center; w,d,h = [n/2 for n in size]; start = len(verts)
        verts.extend([(x-w,y-d,z-h),(x+w,y-d,z-h),(x+w,y+d,z-h),(x-w,y+d,z-h),
                      (x-w,y-d,z+h),(x+w,y-d,z+h),(x+w,y+d,z+h),(x-w,y+d,z+h)])
        faces.extend(tuple(start+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])

    def ellipsoid(self, center, radii, mat, segments=8, rings=5):
        verts, faces = self.data[mat]; start = len(verts)
        for j in range(rings+1):
            phi = math.pi*j/rings
            for i in range(segments):
                a=2*math.pi*i/segments
                jitter=1+.09*math.sin(a*5+j*2.3+center[0]) if mat.startswith('leaves') else 1
                verts.append((center[0]+radii[0]*math.sin(phi)*math.cos(a)*jitter,center[1]+radii[1]*math.sin(phi)*math.sin(a)*jitter,center[2]+radii[2]*math.cos(phi)*jitter))
        for j in range(rings):
            for i in range(segments):
                k=start+j*segments+i; n=start+j*segments+(i+1)%segments
                faces.append((k,n,n+segments,k+segments))

    def segment(self, a, b, width, z, mat):
        # 地面路径使用独立顶点，避免按方向生成另一份场景坐标。
        dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
        if not length:return
        nx,ny=-dy/length*width/2,dx/length*width/2
        verts,faces=self.data[mat]; s=len(verts)
        verts.extend([(a[0]+nx,a[1]+ny,z),(a[0]-nx,a[1]-ny,z),(b[0]-nx,b[1]-ny,z),(b[0]+nx,b[1]+ny,z)])
        faces.append((s,s+1,s+2,s+3))

    def foliage_card(self,center,width,height,angle):
        verts,faces=self.data['leavesCard'];s=len(verts);dx,dy=math.cos(angle)*width/2,math.sin(angle)*width/2
        x,y,z=center
        verts.extend([(x-dx,y-dy,z-height/2),(x+dx,y+dy,z-height/2),(x+dx,y+dy,z+height/2),(x-dx,y-dy,z+height/2)])
        faces.append((s,s+1,s+2,s+3))

    def disc(self,x,y,z,rx,ry,mat,segments=40):
        verts,faces=self.data[mat];s=len(verts);verts.append((x,y,z))
        verts.extend((x+rx*math.cos(i*2*math.pi/segments),y+ry*math.sin(i*2*math.pi/segments),z) for i in range(segments))
        faces.extend((s,s+1+i,s+1+(i+1)%segments) for i in range(segments))

    def finish(self):
        for material,(verts,faces) in self.data.items():
            mesh=bpy.data.meshes.new(self.name+'_'+material)
            mesh.from_pydata(verts,[],faces);mesh.materials.append(materials[material]);mesh.update()
            if material=='glass' and wall_image:
                # 各立面按真实窗格宽度及规划层高重复4×4固定贴图，UV与实际楼层横梁对齐。
                uv=mesh.uv_layers.new(name='CurtainWall')
                for polygon in mesh.polygons:
                    axis=1 if abs(polygon.normal.x)>.5 else 0
                    co=[mesh.vertices[mesh.loops[i].vertex_index].co for i in polygon.loop_indices]
                    low=min(v[axis] for v in co);span=max(v[axis] for v in co)-low
                    columns=max(1,round(span/2.6))
                    for loop_id,v in zip(polygon.loop_indices,co):
                        uv.data[loop_id].uv=((v[axis]-low)/max(span,.01)*columns/wall_input['atlasColumns'],v.z/spec['floorHeightM']/wall_input['atlasRows'])
            if material=='leavesCard':
                uv=mesh.uv_layers.new(name='Foliage')
                for polygon in mesh.polygons:
                    for loop_id,coord in zip(polygon.loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[loop_id].uv=coord
            if material.startswith('leaves'):
                for polygon in mesh.polygons:polygon.use_smooth=True
            obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(obj)
            if self.parent:obj.parent=self.parent

def tree(batch,x,y,z=0,scale=1):
    h=rng.uniform(9,14)*scale
    batch.box((x,y,z+h*.32),(.35*scale,.35*scale,h*.64),'bark')
    if foliage_image:
        for i in range(foliage_input['cardsPerTree']):
            angle=i*2.4;spread=h*.23*math.sqrt((i+1)/foliage_input['cardsPerTree'])
            batch.foliage_card((x+math.cos(angle)*spread,y+math.sin(angle)*spread,z+h*rng.uniform(.65,.92)),h*rng.uniform(*foliage_input['widthHeightRatioRange']),h*rng.uniform(*foliage_input['heightRatioRange']),angle)
        return
    for i in range(13):
        a=i*2.4;radius=h*rng.uniform(.13,.20);spread=h*.25*math.sqrt((i+1)/13)
        batch.ellipsoid((x+math.cos(a)*spread,y+math.sin(a)*spread,z+h*rng.uniform(.57,.94)),
                        (radius*1.05,radius*.95,radius*.95),['leaves','leavesLight','leavesDark'][i%3],segments=8,rings=4)

def facade(batch,cx,cy,z,w,d,h,floor_count,roof_garden=True):
    batch.box((cx,cy,z+h/2),(w,d,h),'gray' if args.gray else 'glass')
    if args.gray:return
    floor_h=h/floor_count
    # 幕墙分格与总层数共享同一楼层定义；每层横梁、竖梃为实际几何。
    for floor in range(floor_count+1):
        zz=z+floor*floor_h
        batch.box((cx,cy,zz),(w+.55,d+.55,.25),'frame')
    for side in (-1,1):
        n=max(4,round(w/2.6))
        for i in range(n+1):
            x=cx-w/2+w*i/n
            batch.box((x,cy+side*(d/2+.12),z+h/2),(.18,.2,h),'frame')
            if i<n:
                for floor in range(floor_count):
                    if not wall_image and rng.random()<.08:
                        batch.box((x+w/n/2,cy+side*(d/2+.025),z+(floor+.5)*floor_h),(w/n-.32,.06,floor_h-.38),'interior' if rng.random()<.2 else 'glassLight')
        n=max(4,round(d/2.6))
        for i in range(n+1):
            y=cy-d/2+d*i/n
            batch.box((cx+side*(w/2+.12),y,z+h/2),(.2,.18,h),'frame')
    batch.box((cx,cy,z+h+.24),(w+.7,d+.7,.48),'stone')
    batch.box((cx,cy,z+h+.5),(w-1.8,d-1.8,.18),'roof')
    if roof_garden:
        # 实体矮墙与内退种植带形成屋顶花园，避免把屋顶做成平色板。
        for side in (-1,1):
            batch.box((cx,cy+side*(d/2-.35),z+h+1.0),(w,.3,1.3),'frame')
            batch.box((cx+side*(w/2-.35),cy,z+h+1.0),(.3,d,1.3),'frame')
        for side in (-1,1):
            batch.box((cx+side*(w/2-2.4),cy,z+h+.7),(2.5,d-4,.35),'grass')
            for y in (cy-d*.30,cy,cy+d*.30):tree(batch,cx+side*(w/2-2.4),y,z+h+.8,.3)
            batch.box((cx,cy+side*(d/2-2.4),z+h+.7),(w-5,2.5,.35),'grass')
        batch.box((cx,cy+d*.24,z+h+1.2),(w*.24,d*.2,1.4),'frame')
        for x in range(5):batch.box((cx-w*.15+x*w*.075,cy-d*.15,z+h+.9),(.25,d*.25,.4),'bronze')

mapping=[]
for identity in plan['demoDesign']['buildingIdentities']:
    key=identity['id'];g=spec['geometryById'][key]
    root=bpy.data.objects.new('building_'+key,None);bpy.context.collection.objects.link(root)
    root.location=g['position'];root['objectId']=key;root['role']=identity['role']
    b=Batch(key,root)
    if key==plan['demoDesign']['focusBuilding']['id']:
        floors=plan['demoDesign']['focusBuilding']['floorsDefinition'];fh=spec['floorHeightM']
        assert len(g['podiumSizes'])==floors['podium']
        for i,(w,d) in enumerate(g['podiumSizes']):
            z=i*fh
            facade(b,0,0,z,w,d,fh,1,roof_garden=False)
            if not args.gray:
                b.box((0,-d/2+2,z+fh+.3),(w-5,2.5,.45),'grass')
                for xx in (-w*.32,0,w*.32):tree(b,xx,-d/2+2,z+fh+.6,.34)
                for side in (-1,1):
                    b.box((side*(w/2-2),0,z+fh+.3),(2.4,d-5,.45),'grass')
                    for yy in (-d*.28,d*.28):tree(b,side*(w/2-2),yy,z+fh+.6,.3)
                for xx in range(-int(w/2)+2,int(w/2),8):b.box((xx,-d/2+.4,z+fh+.65),(3.7,.18,.6),'frame')
        w,d=g['towerSize'];cx,cy=g['towerOffset'];base=floors['podium']*fh;h=floors['towerAbovePodium']*fh
        facade(b,cx,cy,base,w,d,h,floors['towerAbovePodium'])
        if not args.gray:
            for i in range(14):
                y=cy-d/2+d*i/13
                b.box((cx+w/2+.45,y,base+h/2+1),(.65,.18,h+2),'bronze')
        height=floors['total']*fh
    else:
        w,d,height=g['size']
        count=max(1,round(height/spec['floorHeightM']))
        facade(b,0,0,0,w,d,height,count)
        if not args.gray and height<30:
            for xx in (-w/2,w/2):b.box((xx,0,height/2),(1.1,d+1,height+1),'stone')
    b.finish()
    anchor=bpy.data.objects.new('anchor_'+key,None);bpy.context.collection.objects.link(anchor);anchor.parent=root;anchor.location=(0,0,height+3)
    root['heightM']=height
    if key==plan['demoDesign']['focusBuilding']['id']:
        root['totalFloors']=floors['total'];root['podiumFloors']=floors['podium'];root['towerFloors']=floors['towerAbovePodium']
    mapping.append({'objectId':key,'rootNode':root.name,'anchorNode':anchor.name,'heightM':height})

env=Batch('environment')
pw,pd=spec['site']['parkSize'];rw=spec['site']['roadWidth']
env.box((0,0,-.55),(3000,3000,1),'paving')
env.box((0,0,.05),(pw,pd,.3),'path')
for y in (-pd/2-rw/2,pd/2+rw/2):env.box((0,y,.02),(pw+2*rw,rw,.18),'road')
for x in (-pw/2-rw/2,pw/2+rw/2):env.box((x,0,.02),(rw,pd,.18),'road')
for y in (-pd/2-1,pd/2+1):env.box((0,y,.16),(pw+2,1.2,.28),'stone')
for x in (-pw/2-1,pw/2+1):env.box((x,0,.16),(1.2,pd,.28),'stone')
if not args.gray:
    for x in range(-int(pw/2),int(pw/2),12):
        for y in (-pd/2-rw/2,pd/2+rw/2):env.box((x,y,.14),(5,.18,.03),'marking')
    for y in range(-int(pd/2),int(pd/2),12):
        for x in (-pw/2-rw/2,pw/2+rw/2):env.box((x,y,.14),(.18,5,.03),'marking')
    for side in (-1,1):
        for i in range(8):env.box((-pw/2-rw/2+i*1.4,side*(pd/2-8),.17),(.7,5,.03),'marking')
    env.disc(5,-3,.41,82,56,'grass')
    for x in (-pw/2+9,pw/2-9):env.box((x,0,.32),(12,pd-24,.2),'grass')
    env.box((0,pd/2-21,.32),(pw-30,28,.2),'grass')
    env.box((0,-pd/2+9,.32),(pw-30,12,.2),'grass')
    for key,g in spec['geometryById'].items():
        w,d=g['podiumSizes'][0] if 'podiumSizes' in g else g['size'][:2]
        env.box((g['position'][0],g['position'][1],.29),(w+8,d+8,.18),'grass')
    paths=landscape_spec['paths'];fountain=landscape_spec['fountain']
    for y in paths['crossRowsM']:
        a,b=([paths['crossEndpointsM'][0],y-6],[paths['crossEndpointsM'][1],y+5])
        for start,end in clipped_path(a,b,fountain['centerM'],fountain['pathClearanceM']):env.segment(start,end,paths['crossWidthM'],.49,'path')
    for start,end in clipped_path(*paths['spineM'],fountain['centerM'],fountain['pathClearanceM']):env.segment(start,end,paths['spineWidthM'],.51,'path')
    def outside_buildings(x,y,pad=4):
        for k,g in spec['geometryById'].items():
            w,d=g['podiumSizes'][0] if 'podiumSizes' in g else g['size'][:2]
            if abs(x-g['position'][0])<w/2+pad and abs(y-g['position'][1])<d/2+pad:return False
        return True
    n=0
    for _ in range(5000):
        x,y=rng.uniform(-pw/2+4,pw/2-4),rng.uniform(-pd/2+5,pd/2-5)
        if not outside_buildings(x,y) or not is_facility_clear(x,y,landscape_spec) or (x/64)**2+(y/35)**2<1:continue
        env.disc(x,y,.41,3.3,3.1,'grass',segments=12)
        tree(env,x,y,.3,rng.uniform(.8,1.2));n+=1
        if n>=spec['site']['treeCount']:break
    for x in range(-180,190,26):
        for y in (-pd/2-20,pd/2+20):tree(env,x,y,0,.9)
    for x,y in spec['site'].get('centralTreePositionsM',[]):
        if is_facility_clear(x,y,landscape_spec,3):tree(env,x,y,.3,1.0)
    for x in range(-340,341,24):
        for y in (220,260):tree(env,x+rng.uniform(-4,4),y+rng.uniform(-8,8),0,.9)
    # 独立车辆模板供网页实例化，避免静态环境内留下重复车辆或固定车影。
    vehicle_root=bpy.data.objects.new('traffic_vehicle_template',None);bpy.context.collection.objects.link(vehicle_root)
    def car_profile(batch,profile,width,mat):
        # 沿车身纵向轮廓挤出，车窗和机盖具有坡度，不使用上下堆叠的货盘方盒。
        verts,faces=batch.data[mat];start=len(verts);n=len(profile)
        verts.extend((x,y,z) for y in [-width/2,width/2] for x,z in profile)
        faces.extend([tuple(start+i for i in reversed(range(n))),tuple(start+n+i for i in range(n))])
        faces.extend((start+i,start+(i+1)%n,start+n+(i+1)%n,start+n+i) for i in range(n))
    def wheel(batch,x,y,radius):
        verts,faces=batch.data['dark'];start=len(verts);segments=12
        verts.extend((x+radius*math.cos(i*math.tau/segments),yy,radius+.05+radius*math.sin(i*math.tau/segments)) for yy in [y-.12,y+.12] for i in range(segments))
        faces.extend([tuple(start+i for i in range(segments)),tuple(start+segments+i for i in reversed(range(segments)))])
        faces.extend((start+i,start+(i+1)%segments,start+segments+(i+1)%segments,start+segments+i) for i in range(segments))
        batch.box((x,y,.05+radius),(.27,.27,.27),'gray')
    for item in spec['traffic']['fleet']:
        kind=item['type'];length=item['lengthM'];width=item['widthM'];height=item['heightM']
        group=bpy.data.objects.new('traffic_'+kind,None);bpy.context.collection.objects.link(group);group.parent=vehicle_root
        vehicle=Batch('vehicle_'+kind,group);half=length/2
        car_profile(vehicle,[(-half+.12,.42),(half-.15,.42),(half,.65),(half-.18,.92),(-half+.12,1.02),(-half,.72)],width,'car')
        if kind=='truck':
            vehicle.box((-1.05,0,1.83),(3.8,width,2.12),'car')
            car_profile(vehicle,[(.96,.85),(half-.05,.85),(half-.12,1.55),(half-.65,2.3),(.96,2.3)],width*.94,'car')
            car_profile(vehicle,[(1.12,1.4),(half-.25,1.4),(half-.67,2.13),(1.12,2.13)],width*.96,'vehicleGlass')
        else:
            roof=height-.08;rear=-half*.62;front=half*.58
            car_profile(vehicle,[(rear,1.0),(front,1.0),(front-.72,roof),(rear+.42,roof)],width*.86,'vehicleGlass')
            vehicle.box(((front+rear-.3)/2,0,roof+.035),(front-rear-1.1,width*.85,.07),'car')
            # 窗柱、前后保险杠与灯组提供真实汽车尺度线索。
            for y in [-width*.44,width*.44]:vehicle.box((-.24,y,(roof+1)/2),(.09,.06,roof-1),'car')
        for x in [-half*.62,half*.62]:
            for y in [-width*.48,width*.48]:wheel(vehicle,x,y,.37 if kind=='truck' else .34)
        vehicle.box((half-.035,0,.58),(.09,width*.75,.13),'dark')
        for y in [-width*.34,width*.34]:
            vehicle.box((half-.02,y,.84),(.06,.33,.15),'marking');vehicle.box((-half+.02,y,.84),(.06,.3,.14),'tailLamp')
        vehicle.finish()
    # 保留旧景观随机序列，移走静态车辆后不扰动远景建筑位置。
    for _ in range(spec['traffic']['vehicleCount']):rng.uniform(-180,180)
    for _ in range(spec['site']['cityCount']):
        x,y=rng.uniform(-650,650),rng.uniform(240,700)
        if abs(x)<pw/2+45 and abs(y)<pd/2+45:continue
        w,d,h=rng.uniform(22,55),rng.uniform(24,52),rng.uniform(18,85)
        env.box((x,y,h/2),(w,d,h),'city' if rng.random()<.5 else 'cityLight')
env.finish()
if not args.gray:build_landscape(Batch,landscape_spec,tree,args.landscape_layout,spec['geometryById'])

for name,cs in spec['cameras'].items():
    data=bpy.data.cameras.new(name);obj=bpy.data.objects.new('camera_'+name,data);bpy.context.collection.objects.link(obj)
    obj.location=cs['eye'];direction=Vector(cs['target'])-obj.location;obj.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    data.sensor_fit='VERTICAL';data.sensor_height=36;data.lens=36/(2*math.tan(math.radians(cs['fov']/2)))
    if name=='campus':bpy.context.scene.camera=obj
sun_data=bpy.data.lights.new('daylight','SUN');sun_data.energy=2.0;sun_data.angle=.12
sun=bpy.data.objects.new('daylight',sun_data);bpy.context.collection.objects.link(sun);sun.location=spec['render']['sunPosition'];sun.rotation_euler=(-sun.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.world.color=(.6,.68,.72)
bpy.context.scene.render.resolution_x=plan['project']['viewport']['width'];bpy.context.scene.render.resolution_y=plan['project']['viewport']['height']

quality='gray' if args.gray else 'detailed'
blend=OUT/'assets'/('scene-gray.blend' if args.gray else 'scene.blend')
glb=OUT/spec['assets']['grayScene' if args.gray else 'scene']
blend.parent.mkdir(parents=True,exist_ok=True);glb.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
pending_glb=glb.with_name('.'+glb.stem+'-pending.glb')
bpy.ops.export_scene.gltf(filepath=str(pending_glb),export_format='GLB',export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_apply=True)
pending_glb.replace(glb)
manifest={'quality':quality,'planningSha256':hashlib.sha256(raw).hexdigest(),'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'landscapePhase':'layout' if args.landscape_layout else 'detailed','landscapeGeneratorSha256':hashlib.sha256((SOURCE_ROOT/'scripts/campus_landscape.py').read_bytes()).hexdigest(),
          'blender':bpy.app.version_string,'seed':spec['site']['seed'],'objects':mapping,
          'files':{str(path.relative_to(OUT)):{'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size} for path in [blend,glb]},
          'triangles':sum(len(poly.vertices)-2 for obj in bpy.data.objects if obj.type=='MESH' for poly in obj.data.polygons)}
(OUT/'assets'/('manifest-gray.json' if args.gray else 'manifest.json')).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(glb.parent/'build-info.json').write_text(json.dumps({'quality':quality,'triangles':manifest['triangles'],'asset':glb.name,'assetSha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'objects':mapping,'planningSha256':manifest['planningSha256']},ensure_ascii=False,indent=2)+'\n')
print('BUILD_RESULT',json.dumps({'quality':quality,'glb':str(glb),'bytes':glb.stat().st_size,'triangles':manifest['triangles'],'objects':len(mapping)},ensure_ascii=False))
