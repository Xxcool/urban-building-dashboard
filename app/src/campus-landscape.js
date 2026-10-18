// 园区水景仅消费规划和现有可见时钟；不持有业务状态、不创建独立动画循环。
import * as THREE from 'three';
import {toThree} from './state.js';

export function jetPosition(spec,jet,progress){
  const f=spec.fountain,angle=jet*Math.PI*2/f.jetCount,radial=jet===0?0:f.jetRingRadiusM;
  const origin=[f.centerM[0]+Math.cos(angle)*radial,f.centerM[1]+Math.sin(angle)*radial];
  const travel=.7*progress,height=4*f.jetHeightM*progress*(1-progress);
  return toThree([origin[0]+Math.cos(angle)*travel,origin[1]+Math.sin(angle)*travel,f.waterHeightM+height]);
}

export function createCampusLandscape(model,scene,spec){
  const water=model.getObjectByName('landscape_water');
  if(!water)throw new Error('缺少已规划的园区水面');
  const clock={value:0},f=spec.fountain;
  water.castShadow=false;water.material=water.material.clone();water.material.roughness=.24;water.material.metalness=.18;
  water.material.onBeforeCompile=shader=>{
    shader.uniforms.landscapeTime=clock;
    shader.vertexShader='varying vec3 landscapeWorld;\n'+shader.vertexShader.replace('#include <worldpos_vertex>','#include <worldpos_vertex>\nlandscapeWorld=(modelMatrix*vec4(transformed,1.0)).xyz;');
    shader.fragmentShader='uniform float landscapeTime;\nvarying vec3 landscapeWorld;\n'+shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>\nfloat radius=length(landscapeWorld.xz-vec2(${f.centerM[0].toFixed(3)},${(-f.centerM[1]).toFixed(3)}));\nfloat ripple=sin(radius*5.0-landscapeTime*2.2)*.028+sin(landscapeWorld.x*2.3+landscapeWorld.z*2.1+landscapeTime)*.012;\ndiffuseColor.rgb+=vec3(ripple*.6,ripple*.85,ripple);`);
  };
  water.material.customProgramCacheKey=()=> 'campus-water-v23';
  const lines=[];
  for(let jet=0;jet<f.jetCount;jet++)for(let i=0;i<16;i++)lines.push(...jetPosition(spec,jet,i/16),...jetPosition(spec,jet,(i+1)/16));
  const lineGeometry=new THREE.BufferGeometry();lineGeometry.setAttribute('position',new THREE.Float32BufferAttribute(lines,3));
  const streams=new THREE.LineSegments(lineGeometry,new THREE.LineBasicMaterial({color:'#e5f6f5',transparent:true,opacity:.8}));
  streams.name='fountain_streams';streams.layers.set(1);scene.add(streams);
  const perJet=spec.motion.particleCountPerJet,positions=new Float32Array(f.jetCount*perJet*3),geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.BufferAttribute(positions,3).setUsage(THREE.DynamicDrawUsage));
  const drops=new THREE.Points(geometry,new THREE.PointsMaterial({color:'#f1ffff',size:.17,transparent:true,opacity:.9,depthWrite:false}));
  drops.name='fountain_droplets';drops.layers.set(1);drops.frustumCulled=false;scene.add(drops);
  let lastSample;
  return {
    update(seconds){
      clock.value=seconds*spec.motion.waterRippleSpeed;
      for(let jet=0;jet<f.jetCount;jet++)for(let i=0;i<perJet;i++){
        const progress=(seconds*.8+i/perJet+jet*.13)%1,xyz=jetPosition(spec,jet,progress);positions.set(xyz,(jet*perJet+i)*3);
      }
      geometry.attributes.position.needsUpdate=true;lastSample=Array.from(positions.slice(0,3));
      return {seconds:+seconds.toFixed(3),jets:f.jetCount,particles:positions.length/3,first:lastSample.map(n=>+n.toFixed(3))};
    }
  };
}
