"""验证景观步道避水、设施净空及建筑身份的空间约束。"""
import json,math,unittest
from pathlib import Path
from campus_landscape import clipped_path,is_facility_clear
P=json.loads((Path(__file__).resolve().parents[1]/'planning/project.json').read_text())['production'];S=P['landscape']
def distance_to_segment(point,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((point[0]-a[0])*dx+(point[1]-a[1])*dy)/(dx*dx+dy*dy)))
 return math.dist(point,[a[0]+dx*t,a[1]+dy*t])
class LandscapeGeometry(unittest.TestCase):
 def test_paths_do_not_cross_water(self):
  f=S['fountain'];p=S['paths'];lines=[([p['crossEndpointsM'][0],y-6],[p['crossEndpointsM'][1],y+5],p['crossWidthM']) for y in p['crossRowsM']]+[(*p['spineM'],p['spineWidthM'])]
  for a,b,width in lines:
   for start,end in clipped_path(a,b,f['centerM'],f['pathClearanceM']):self.assertGreater(distance_to_segment(f['centerM'],start,end)-width/2,f['waterRadiusM'])
 def test_roof_and_pool_keep_tree_clearance(self):
  self.assertFalse(is_facility_clear(*S['fountain']['centerM'],S))
  for pergola in S['pergolas']:self.assertFalse(is_facility_clear(*pergola['centerM'],S))
 def test_facilities_outside_building_footprints(self):
  for item in S['pergolas']:
   x,y=item['centerM'];w,d,h=item['sizeM'];self.assertGreaterEqual(h,S['clearance']['pergolaHeadroomM'])
   for building in P['geometryById'].values():
    bx,by,_=building['position'];bw,bd=building.get('podiumSizes',[building.get('size')])[0][:2]
    self.assertTrue(abs(x-bx)>(w+bw)/2 or abs(y-by)>(d+bd)/2)
if __name__=='__main__':unittest.main()
