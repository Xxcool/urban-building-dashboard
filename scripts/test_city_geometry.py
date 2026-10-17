"""道路水域边界回归：覆盖中点检查遗漏的宽度侵入和细水道穿越。"""
import unittest
from city_geometry import clear_surface

class RoadFootprintTest(unittest.TestCase):
 def test_full_width_hits_bank(self):
  lake=[[(0,0),(10,0),(10,10),(0,10)]]
  self.assertFalse(clear_surface((-5,-1),(15,-1),4,lake))
  self.assertTrue(clear_surface((-5,-4),(15,-4),4,lake))
 def test_long_segment_crosses_narrow_water(self):
  lake=[[(1,-10),(2,-10),(2,10),(1,10)]]
  self.assertFalse(clear_surface((-20,0),(20,0),2,lake))
 def test_road_encloses_tiny_water(self):
  self.assertFalse(clear_surface((-10,0),(10,0),10,[[(-1,-1),(1,-1),(1,1),(-1,1)]]))

if __name__=='__main__':unittest.main()
