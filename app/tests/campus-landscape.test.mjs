// 水景轨迹必须保持在水池内，且遵循模型到Three的轴向转换。
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {jetPosition} from '../src/campus-landscape.js';
const spec=JSON.parse(fs.readFileSync(new URL('../../planning/project.json',import.meta.url))).production.landscape;
test('喷泉起止回到水面，低喷头轨迹始终落在池内',()=>{
 for(let jet=0;jet<spec.fountain.jetCount;jet++)for(let step=0;step<=100;step++){
  const p=step/100,[x,y,z]=jetPosition(spec,jet,p),f=spec.fountain;
  assert.ok(Math.hypot(x-f.centerM[0],z+f.centerM[1])<f.waterRadiusM);
  assert.ok(y>=f.waterHeightM-1e-9&&y<=f.waterHeightM+f.jetHeightM+1e-9);
  if(step===0||step===100)assert.ok(Math.abs(y-f.waterHeightM)<1e-9);
 }
});
