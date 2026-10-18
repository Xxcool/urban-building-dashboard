// 确定性的日光与云层环境纹理，供背景和玻璃反射使用，不使用设计整图充当场景。
import * as THREE from 'three';
export function createDaylightSky(spec){
 const width=1024,height=512,data=new Uint8Array(width*height*4),top=new THREE.Color(spec.top),horizon=new THREE.Color(spec.horizon);
 // DataTexture的v沿行号递增；上半球对应v>0.5，与Three的equirectUv一致。
 // 输出数据纹理采用sRGB字节，色值只在这里转换一次。
 top.convertLinearToSRGB();horizon.convertLinearToSRGB();
 const hash=(x,y)=>{const n=Math.sin(x*127.1+y*311.7)*43758.5453;return n-Math.floor(n);};
 const noise=(x,y)=>{const ix=Math.floor(x),iy=Math.floor(y),u=x-ix,v=y-iy,a=u*u*(3-2*u),b=v*v*(3-2*v);return THREE.MathUtils.lerp(THREE.MathUtils.lerp(hash(ix,iy),hash(ix+1,iy),a),THREE.MathUtils.lerp(hash(ix,iy+1),hash(ix+1,iy+1),a),b);};
 for(let y=0;y<height;y++)for(let x=0;x<width;x++){
  const altitude=Math.max(0,(y-height/2)/(height/2)),gradient=Math.sqrt(altitude),fbm=noise(x*.0225,y*.045)*.58+noise(x*.05,y*.085)*.28+noise(x*.105,y*.15)*.14;
  const cloud=THREE.MathUtils.smoothstep(fbm,.48,.72)*spec.cloudStrength*THREE.MathUtils.smoothstep(altitude,0,.08),k=(y*width+x)*4;
  for(const [c,name]of ['r','g','b'].entries())data[k+c]=Math.round(THREE.MathUtils.lerp(THREE.MathUtils.lerp(horizon[name],top[name],gradient),.99,cloud)*255);
  data[k+3]=255;
 }
 const texture=new THREE.DataTexture(data,width,height);texture.colorSpace=THREE.SRGBColorSpace;texture.mapping=THREE.EquirectangularReflectionMapping;texture.minFilter=THREE.LinearFilter;texture.magFilter=THREE.LinearFilter;texture.needsUpdate=true;return texture;
}
