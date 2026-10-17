"""城市道路的平面水域避让；检查完整路面，不把中心点在陆地误认为路面安全。"""
import math

def inside(point,polygon):
 x,y=point;hit=False
 for (ax,ay),(bx,by) in zip(polygon,polygon[1:]+polygon[:1]):
  if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:hit=not hit
 return hit

def intersects(a,b,c,d):
 def cross(p,q,r):return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
 return cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0

def surface(a,b,width):
 length=math.dist(a,b)
 if length<1e-6:return []
 nx,ny=-(b[1]-a[1])/length*width/2,(b[0]-a[0])/length*width/2
 return [(a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny),(b[0]+nx,b[1]+ny),(a[0]+nx,a[1]+ny)]

def clear_surface(a,b,width,lakes):
 quad=surface(a,b,width)
 if not quad:return False
 lo=[min(p[i] for p in quad) for i in range(2)];hi=[max(p[i] for p in quad) for i in range(2)]
 for poly in lakes:
  if any(max(p[i] for p in poly)<lo[i] or min(p[i] for p in poly)>hi[i] for i in range(2)):continue
  if any(inside(p,poly) for p in quad) or any(inside(p,quad) for p in poly):return False
  if any(intersects(a,b,c,d) for a,b in zip(quad,quad[1:]+quad[:1]) for c,d in zip(poly,poly[1:]+poly[:1])):return False
 return True

def densify(points,step=18):
 result=[points[0]]
 for a,b in zip(points,points[1:]):
  n=max(1,math.ceil(math.dist(a,b)/step))
  result.extend(tuple(a[j]+(b[j]-a[j])*i/n for j in range(2)) for i in range(1,n+1))
 return result
