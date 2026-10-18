"""读取景观制作规格生成静态设施；装饰不参与楼宇身份、指标或拾取。"""
import math
import random


def clipped_path(a, b, center, radius):
    """直线步道在水景广场环带处收口，池内不保留穿越铺装。"""
    dx,dy=b[0]-a[0],b[1]-a[1];ax,ay=a[0]-center[0],a[1]-center[1]
    aa=dx*dx+dy*dy;bb=2*(ax*dx+ay*dy);cc=ax*ax+ay*ay-radius*radius
    discriminant=bb*bb-4*aa*cc
    if discriminant<=0:return [(a,b)]
    t0,t1=sorted(((-bb-math.sqrt(discriminant))/(2*aa),(-bb+math.sqrt(discriminant))/(2*aa)))
    if t1<=0 or t0>=1:return [(a,b)]
    result=[]
    if t0>0:result.append((a,[a[0]+dx*t0,a[1]+dy*t0]))
    if t1<1:result.append(([a[0]+dx*t1,a[1]+dy*t1],b))
    return result


def is_facility_clear(x,y,spec,pad=3):
    f=spec['fountain'];cx,cy=f['centerM']
    if math.hypot(x-cx,y-cy)<spec['clearance']['fountainNoTreeRadiusM']+pad:return False
    for item in spec['pergolas']:
        px,py=item['centerM'];w,d,_=item['sizeM']
        if abs(x-px)<w/2+pad and abs(y-py)<d/2+pad:return False
    entry=spec['entry'];ex,ey,_=entry['canopyCenterM']
    if abs(x-ex)<14+pad and 20-pad<y<ey+pad:return False
    for item in spec['benches']:
        if math.dist([x,y],item['centerM'])<3.5+pad:return False
    return True


def build_landscape(Batch,spec,tree_fn,layout=False,buildings=None):
    """简模和深化共用米制坐标，只有细节密度不同。"""
    batch=Batch('landscape');rng=random.Random(spec['seed']);f=spec['fountain'];cx,cy=f['centerM']
    def box(c,size,mat):batch.box(c,size,mat)
    def ring(x,y,z,outer,inner,mat,segments=48):
        verts,faces=batch.data[mat];s=len(verts)
        for radius in [outer,inner]:verts.extend((x+radius*math.cos(i*math.tau/segments),y+radius*math.sin(i*math.tau/segments),z) for i in range(segments))
        faces.extend((s+i,s+(i+1)%segments,s+segments+(i+1)%segments,s+segments+i) for i in range(segments))
    def beam(a,b,width,depth,mat):
        # 立面/自行车杆使用有截面的三维杆件，避免俯视时消失。
        dx,dy,dz=[b[i]-a[i] for i in range(3)];length=math.sqrt(dx*dx+dy*dy+dz*dz)
        if not length:return
        ux,uy,uz=dx/length,dy/length,dz/length
        nx,ny,nz=(-uy,ux,0) if abs(uz)<.98 else (1,0,0)
        n=math.sqrt(nx*nx+ny*ny+nz*nz);nx,ny,nz=nx/n,ny/n,nz/n
        vx,vy,vz=uy*nz-uz*ny,uz*nx-ux*nz,ux*ny-uy*nx
        verts,faces=batch.data[mat];s=len(verts)
        for p in [a,b]:
            for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]:verts.append(tuple(p[i]+u*width/2*[nx,ny,nz][i]+v*depth/2*[vx,vy,vz][i] for i in range(3)))
        faces.extend(tuple(s+i for i in face) for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    def bench(x,y,angle=0,length=3.6):
        def local(px,py,z):return (x+px*math.cos(angle)-py*math.sin(angle),y+px*math.sin(angle)+py*math.cos(angle),z)
        beam(local(-length/2-.5,0,.61),local(length/2+.5,0,.61),2.6,.1,'waterEdge')
        for xx in [-length*.34,length*.34]:
            a=local(xx,0,.76);box(a,(.32,.6,.5),'waterEdge')
        for yy in [-.22,0,.22]:beam(local(-length/2,yy,1.04),local(length/2,yy,1.04),.18,.12,'wood')
        for xx in [-length*.34,length*.34]:beam(local(xx,.3,1.0),local(xx,.3,1.72),.08,.08,'metal')
        for z in [1.38,1.62]:beam(local(-length/2,.32,z),local(length/2,.32,z),.16,.12,'wood')
    batch.disc(cx,cy,.525,f['plazaRadiusM'],f['plazaRadiusM'],'paving',segments=64)
    # 水盆为低矮实体外壁和内侧石边；水面高于底板，避免地面穿透。
    segments=64
    ring(cx,cy,.57,f['outerRadiusM']+.3,f['waterRadiusM'],'waterEdge',segments)
    ring(cx,cy,.84,f['outerRadiusM'],f['waterRadiusM'],'waterEdge',segments)
    verts,faces=batch.data['waterEdge'];s=len(verts)
    for z in [.57,.84]:verts.extend((cx+f['outerRadiusM']*math.cos(i*math.tau/segments),cy+f['outerRadiusM']*math.sin(i*math.tau/segments),z) for i in range(segments))
    faces.extend((s+i,s+(i+1)%segments,s+segments+(i+1)%segments,s+segments+i) for i in range(segments))
    batch.disc(cx,cy,f['waterHeightM'],f['waterRadiusM'],f['waterRadiusM'],'water',segments=64)
    for a in [math.pi*.2,math.pi*.8,math.pi*1.2,math.pi*1.8]:bench(cx+math.cos(a)*11.6,cy+math.sin(a)*11.6,a+math.pi/2,4.0)
    for item in spec['pergolas']:
        x,y=item['centerM'];w,d,h=item['sizeM'];box((x,y,.59),(w+1.8,d+2.5,.14),'waterEdge')
        for xx in [-w/2+.4,0,w/2-.4]:
            for yy in [-d/2+.3,d/2-.3]:box((x+xx,y+yy,.62+h/2),(.24,.24,h),'metal')
        for yy in [-d/2,d/2]:box((x,y+yy,h+.62),(w+.8,.24,.27),'metal')
        if layout:box((x,y,h+.78),(w,d,.16),'wood')
        else:
            count=round(w/.52)
            for i in range(count+1):box((x-w/2+w*i/count,y,h+.83),(.17,d+.7,.23),'wood')
        for xx in [-w*.29,w*.29]:bench(x+xx,y+1.8,0,4.4)
    for item in spec['benches']:bench(*item['centerM'],item['angleRad'])
    for bed in spec['beds']:
        x,y=bed['centerM'];rx,ry=bed['radiiM'];batch.disc(x,y,.56,rx,ry,'shrub',segments=32)
        ring(x,y,.58,1,0.97,'waterEdge',24) if layout else None
        if layout:continue
        for i in range(spec['plantClustersPerBed']):
            a=rng.random()*math.tau;r=math.sqrt(rng.random())*.89;px=x+math.cos(a)*rx*r;py=y+math.sin(a)*ry*r
            height=rng.uniform(*spec['shrubHeightRangeM']);radius=rng.uniform(*spec['shrubRadiusRangeM'])
            if not is_facility_clear(px,py,spec,radius+1):continue
            batch.ellipsoid((px,py,.57+height*.45),(radius,radius*.8,height*.6),'shrub' if i%4 else 'leavesLight',segments=7,rings=3)
            if i%5==0:
                for j in range(3):batch.ellipsoid((px+j*.42,py,.85),(.62,.45,.26),'flower',segments=6,rings=3)
        # 每片庭院一簇较低树冠，保留休憩设施附近的净空。
        for index in range(spec['treesPerBed']):
            tx=x+rx*(index-1)*.43;ty=y+ry*(.24 if index%2 else -.2)
            if is_facility_clear(tx,ty,spec,4):tree_fn(batch,tx,ty,.4,.58+index*.07)
    # 沿低层楼宇前场形成连续种植边带，中央保留入口通道；尺度由同一建筑布局派生。
    court=spec['forecourt']
    for key in court['buildingIds']:
        g=buildings[key];x,y,_=g['position'];w,d=g['size'][:2];front=y-d/2-court['offsetM']
        for a,b in [(x-w/2-1,x-court['entranceHalfWidthM']),(x+court['entranceHalfWidthM'],x+w/2+1)]:
            batch.segment((a,front),(b,front),court['widthM'],.59,'shrub')
            beam((a,front-court['widthM']/2,.72),(b,front-court['widthM']/2,.72),.22,.3,'waterEdge')
            if layout:continue
            count=max(1,round((b-a)/court['plantSpacingM']))
            for i in range(count+1):
                px=a+(b-a)*i/count
                if not is_facility_clear(px,front,spec,1.5):continue
                batch.ellipsoid((px,front,1.1),(1.8,1.45,.7),'shrub',segments=6,rings=3)
                if i%3==0:batch.ellipsoid((px,front-1,1.0),(1.0,.6,.4),'flower',segments=6,rings=3)
    e=spec['entry'];x,y,z=e['canopyCenterM'];w,d,h=e['canopySizeM']
    box((x,y,z),(w,d,h),'glassLight')
    for xx in [-w/2,w/2]:
        box((x+xx,y,z-.15),(.17,d+.4,.26),'metal');box((x+xx,y-d/2+.4,(z+.5)/2),(.22,.22,z-.5),'metal')
    box((x,y-d/2,z-.1),(w+.2,.22,.22),'metal')
    sx,sy=e['stairsCenterM']
    for i in range(3):box((sx,sy+i*.46,.58+(i+1)*.09),(w-2,3-i*.75,(i+1)*.18),'waterEdge')
    rx,ry=e['rampCenterM'];rw,rd,rh=e['rampSizeM'];verts,faces=batch.data['waterEdge'];s=len(verts)
    verts.extend([(rx-rw/2,ry-rd/2,.56),(rx+rw/2,ry-rd/2,.56),(rx+rw/2,ry+rd/2,.56),(rx-rw/2,ry+rd/2,.56),(rx-rw/2,ry+rd/2,.56+rh),(rx+rw/2,ry+rd/2,.56+rh)])
    faces.extend(tuple(s+i for i in f) for f in [(0,1,5,4),(0,4,3),(1,2,5),(3,4,5,2)])
    for px,py in spec['signPositionsM']:
        box((px,py,1.5),(.18,.18,2),'metal');box((px,py,2.5),(1.5,.18,1.2),'metal')
        for zz in [2.25,2.5,2.75]:box((px,py-.11,zz),(1,.04,.055),'stone')
    if not layout:
        for index,item in enumerate(spec['people']):
            x,y=item['positionM'];z=.56
            batch.ellipsoid((x,y,z+1.58),(.13,.13,.15),'skin',segments=6,rings=4)
            batch.ellipsoid((x,y,z+1.11),(.23,.14,.36),'clothes' if index%3 else 'stone',segments=6,rings=3)
            for side in [-1,1]:
                beam((x+side*.12,y,z+.84),(x+side*.14,y+side*.09,z+.08),.13,.13,'clothes')
                beam((x+side*.21,y,z+1.31),(x+side*.31,y+.1,z+.8),.1,.1,'skin')
        rack=spec['bikeRack'];bx,by=rack['centerM']
        for i in range(rack['count']):
            x,y=bx+i*rack['spacingM'],by
            for yy in [-.65,.65]:
                for k in range(16):
                    a=k*math.tau/16;b=(k+1)*math.tau/16;beam((x,y+yy+math.cos(a)*.34,.94+math.sin(a)*.34),(x,y+yy+math.cos(b)*.34,.94+math.sin(b)*.34),.045,.045,'metal')
            for a,b in [((x,y-.65,.94),(x,y,1.5)),((x,y,1.5),(x,y+.65,.94)),((x,y-.65,.94),(x,y+.2,.94)),((x,y+.2,.94),(x,y,1.5))]:beam(a,b,.06,.06,'metal')
            box((x,y,1.58),(.32,.28,.08),'wood');box((x,y+.52,1.65),(.5,.08,.08),'metal')
    batch.finish()
