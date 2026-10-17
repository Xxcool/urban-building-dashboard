// 核对业务确认的动效时序、终态与减少动态效果，防止返回城市误播整段或边界提前完成。
import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {entranceFrame} from '../src/entrance.js';
const spec=JSON.parse(fs.readFileSync(new URL('../../planning/project.json',import.meta.url))).design.motion.cityEntrance;
test('城市先展开，边界随后闭合，园区与标签最后出现',()=>{
 const start=entranceFrame(0,spec),outline=entranceFrame(1.5,spec),park=entranceFrame(2.5,spec),end=entranceFrame(3.2,spec);
 assert.equal(start.boundary,0);assert.equal(start.park,0);assert.equal(start.labels,0);
 assert.equal(outline.city,1);assert.ok(outline.boundary>0&&outline.boundary<1);assert.equal(outline.park,0);
 assert.equal(park.boundary,1);assert.ok(park.park>0&&park.park<1);assert.ok(park.labels>0);
 assert.deepEqual(end,{city:1,material:1,boundary:1,park:1,labels:1,panel:1,camera:1,pulse:0,done:true});
 assert.deepEqual(entranceFrame(0,spec,{reduced:true}),end);
});
test('返回城市只淡入，不重新描边、移动相机或隐藏面板',()=>{
 const f=entranceFrame(.2,spec,{returning:true});assert.equal(f.boundary,1);assert.equal(f.park,1);assert.equal(f.camera,1);assert.equal(f.panel,1);assert.ok(f.city>0&&f.city<1);assert.equal(f.done,false);assert.equal(entranceFrame(.45,spec,{returning:true}).done,true);
});
