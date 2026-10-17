// 按实际三维描边曲线与湖岸平滑算法核对包含关系，避免控制点都在内但曲线仍穿湖。
import {test} from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import * as THREE from 'three';
const spec=JSON.parse(fs.readFileSync(new URL('../public/assets/runtime.json',import.meta.url))).production.city;
const curve=(poly,type)=>new THREE.CatmullRomCurve3(poly.map(([x,y])=>new THREE.Vector3(x,y,0)),true,type,.5);
const border=curve(spec.outline,'centripetal').getPoints(4096);
function inside(p){let hit=false;for(let i=1;i<border.length;i++){const a=border[i-1],b=border[i];if((a.y>p.y)!==(b.y>p.y)&&p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x)hit=!hit;}return hit;}
test('底部整片湖泊及平滑湖岸位于圈选区域内部',()=>{for(const index of spec.alignment.containedWaterIndices){const lake=curve(spec.waterPolygons[index],'catmullrom').getPoints(1024);for(const point of lake)assert.ok(inside(point),`湖岸穿出边界：${point.x},${point.y}`);}});
