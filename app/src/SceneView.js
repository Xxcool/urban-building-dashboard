// 实际GLB场景、相机、拾取、标签和生命周期；不从网格颜色反推业务数据。
import {onMounted,onBeforeUnmount,ref,watch,computed} from 'vue';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {createDaylightSky} from './daylight-environment.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {SMAAPass} from 'three/addons/postprocessing/SMAAPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {GTAOPass} from 'three/addons/postprocessing/GTAOPass.js';
import {toThree,number,area,occupancy} from './state.js';
import Icon from './Icon.js';
import {measureFloatingCard} from './floating-card.js';
import {createRoute} from './traffic.js';
import {createCampusLandscape} from './campus-landscape.js';

export default {
  components:{Icon},props:['active','config','level','selected','buildingData','mode','resetTick','tour'],emits:['select','focus','stats','status','ready','interrupt'],
  setup(props,{emit,expose}) {
    const host=ref(null),labelHost=ref(null),status=ref('正在载入三维场景'),failure=ref(false),cardOpen=ref(false),cardPosition=ref(null);
    // 卡片读取父级同一选中楼宇快照，模型高度单独来自制作尺寸；不借用 A1 的经营指标。
    const cardIdentity=computed(()=>props.config.demoDesign.buildingIdentities.find(item=>item.id===props.selected));
    const modelHeight=computed(()=>props.config.production.geometryById[props.selected]?.size?.[2]);
    function closeCardOnEscape(event){if(cardOpen.value&&props.active&&event.key==='Escape'){cardOpen.value=false;event.stopImmediatePropagation();event.preventDefault();}}
    let renderer,scene,camera,controls,composer,aoPass,frame,observer,model,disposed=false,transition=null;
    let environmentTexture,skyTexture,pmrem,room,facadeEnvironment,quality,clickStart,renderCount=0,lastStats=0,lastTime=0;
    const roots=new Map(),anchors=new Map(),labels=new Map(),highlights=new Map(),ray=new THREE.Raycaster(),pointer=new THREE.Vector2(),frameTimes=[];
    let trafficSeconds=0;const trafficMeshes=[],trafficDummy=new THREE.Object3D();
    const pending=[...props.config.demoDesign.buildingIdentities];
    const glassMaterials=new Map(),interiorMeshes=[];
    // 总览使用同一幕墙的反射外观；仅近景启用窗后实体与折射，避免远景重复绘制全场景。
    function applyDetailQuality(){
      const close=props.level==='building';
      for(const [material,authored] of glassMaterials){material.transmission=close&&authored.owner===props.config.demoDesign.focusBuilding.id?authored.transmission:0;material.needsUpdate=true;}
      for(const mesh of interiorMeshes)mesh.visible=close&&mesh.name.startsWith('interior_v27_A1_');
    }
    const loadingController=new AbortController();
    function disposeModel(root){
      const geometries=new Set(),mats=new Set(),textures=new Set();
      root?.traverse(obj=>{if(obj.geometry)geometries.add(obj.geometry);for(const m of obj.material?(Array.isArray(obj.material)?obj.material:[obj.material]):[]){mats.add(m);for(const value of Object.values(m))if(value?.isTexture)textures.add(value);}});
      geometries.forEach(g=>g.dispose());mats.forEach(m=>m.dispose());textures.forEach(t=>t.dispose());
    }
    let entryFrame=null,entryAO=1;const detailReveal={value:1};
    function applyCampusEntry(pose,frame){
      if(!camera)return;transition=null;cardOpen.value=false;entryFrame=frame;entryAO=0;detailReveal.value=frame.material;
      controls.enabled=false;controls.enableDamping=false;controls.autoRotate=false;camera.position.fromArray(pose.eye);controls.target.fromArray(pose.target);camera.fov=pose.fov;camera.lookAt(controls.target);camera.updateProjectionMatrix();camera.updateMatrixWorld(true);
      host.value.dataset.entryProjection=JSON.stringify(new THREE.Vector3(0,0,0).project(camera).toArray());host.value.dataset.cameraSettled='false';host.value.dataset.entryCamera=JSON.stringify(pose);
    }
    function finishCampusEntry(){entryFrame=null;detailReveal.value=1;if(controls){controls.enabled=true;controls.enableDamping=true;}lastTime=0;}
    const interruptEntry=()=>{if(entryFrame)emit('interrupt');};
    expose({applyCampusEntry,finishCampusEntry});
    const setCamera=(instant=false)=>{
      if(!camera)return;instant=instant||matchMedia('(prefers-reduced-motion: reduce)').matches;
      const c=props.config.production.cameras[props.level];
      // 先声明镜头开始过渡，避免快速切层时读到上一帧的停稳标记。
      if(host.value)host.value.dataset.cameraSettled=String(instant);
      camera.near=c.near;camera.far=c.far;
      const eye=new THREE.Vector3(...toThree(c.eye)),target=new THREE.Vector3(...toThree(c.target));
      controls.maxDistance=props.level==='campus'?1000:500;controls.minDistance=props.level==='campus'?100:55;
      if(instant){camera.position.copy(eye);controls.target.copy(target);camera.fov=c.fov;camera.updateProjectionMatrix();controls.update();transition=null;}
      else transition={duration:props.level==='campus'?props.config.production.campusEntry.returnDuration*1000:1100,start:performance.now(),eyeFrom:camera.position.clone(),targetFrom:controls.target.clone(),fovFrom:camera.fov,eye,target,fov:c.fov};
    };
    function choose(key) {cardPosition.value=null;lastCardLayout=0;emit('select',key);cardOpen.value=key!==props.config.demoDesign.focusBuilding.id;if(!cardOpen.value)emit('focus'); }
    let lastCardLayout=0;
    function placeCard(time){
      if(!cardOpen.value||time-lastCardLayout<90)return;lastCardLayout=time;
      const card=host.value.querySelector('.building-info-card'),label=labels.get(props.selected);
      const previous=cardPosition.value?.owner===props.selected?cardPosition.value:null;
      const root=roots.get(props.selected),obstacles=[];
      if(root){const box=new THREE.Box3().setFromObject(root),corners=[];
        for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const p=new THREE.Vector3(x,y,z).project(camera);corners.push({x:(p.x*.5+.5)*host.value.clientWidth,y:(-.5*p.y+.5)*host.value.clientHeight});}
        const left=Math.min(...corners.map(p=>p.x)),top=Math.min(...corners.map(p=>p.y));obstacles.push({left,top,width:Math.max(...corners.map(p=>p.x))-left,height:Math.max(...corners.map(p=>p.y))-top,weight:12});
      }
      const position=measureFloatingCard(host.value,card,label,previous,obstacles);
      if(position)cardPosition.value={...position,owner:props.selected};
    }
    function resize(){
      if(!renderer||!host.value||!host.value.clientWidth)return;
      const w=host.value.clientWidth,h=host.value.clientHeight;
      const screenScale=host.value.getBoundingClientRect().width/w;
      renderer.setPixelRatio(Math.max(.65,Math.min(window.devicePixelRatio,props.config.production.render.maxPixelRatio)*screenScale));
      renderer.setSize(w,h,false);composer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();
    }
    function selectOutline(){for(const [id,group] of highlights)group.visible=id===props.selected;}
    function pointerUp(event){
      if(!clickStart||Math.hypot(event.clientX-clickStart[0],event.clientY-clickStart[1])>5)return;
      const rect=renderer.domElement.getBoundingClientRect();pointer.set((event.clientX-rect.left)/rect.width*2-1,-(event.clientY-rect.top)/rect.height*2+1);
      ray.setFromCamera(pointer,camera);
      const candidates=props.level==='building'?[roots.get(props.config.demoDesign.focusBuilding.id)].filter(Boolean):[...roots.values()];
      const hits=ray.intersectObjects(candidates,true);
      if(hits.length){let obj=hits[0].object;while(obj&&!obj.userData.objectId)obj=obj.parent;if(obj)choose(obj.userData.objectId);}
    }
    function pointerDown(e){interruptEntry();clickStart=[e.clientX,e.clientY];transition=null;}
    const visibilityChanged=()=>{lastTime=0;};
    const progressStatus=(message,error=false)=>{status.value=message;failure.value=error;emit('status',{message,error});};
    onMounted(async()=>{
      try{
        const settings=props.config.production.render;
        renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});renderer.outputColorSpace=THREE.SRGBColorSpace;
        renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=settings.exposure;
        // 窗后折射使用半分辨率缓冲，主画面和文字保持原尺寸。
        renderer.transmissionResolutionScale=settings.transmissionResolutionScale;
        renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFShadowMap;
        // 场景为固定演示快照；相机巡览不改变光源与几何，只在模型载入后计算一次阴影。
        renderer.shadowMap.autoUpdate=false;
        renderer.info.autoReset=false;
        renderer.domElement.setAttribute('aria-label','可旋转和选择楼宇的三维园区');renderer.domElement.tabIndex=0;host.value.prepend(renderer.domElement);
        scene=new THREE.Scene();scene.fog=new THREE.Fog('#e1e8e9',settings.fogNear,settings.fogFar);
        // 天空作为背景纹理，不参与GBuffer，防止环境球遮挡远景AO和形成灰色多边形。
        skyTexture=createDaylightSky(props.config.production.restoration.sky);scene.background=skyTexture;
        scene.add(new THREE.HemisphereLight('#dfeefb','#b6b09a',settings.hemisphereIntensity));
        const sun=new THREE.DirectionalLight('#fff5e5',settings.sunIntensity);sun.position.set(...toThree(settings.sunPosition));sun.castShadow=true;sun.shadow.mapSize.setScalar(settings.shadowMapSize);sun.shadow.camera.left=-300;sun.shadow.camera.right=300;sun.shadow.camera.top=270;sun.shadow.camera.bottom=-270;sun.shadow.camera.near=1;sun.shadow.camera.far=850;sun.shadow.normalBias=.2;sun.shadow.bias=-.00004;sun.shadow.radius=3;sun.shadow.camera.updateProjectionMatrix();sun.shadow.camera.layers.enable(1);scene.add(sun);
        const fillSettings=settings.fillLight,fill=new THREE.DirectionalLight(fillSettings.color,fillSettings.intensity);fill.position.set(...toThree(fillSettings.positionM));scene.add(fill);
        pmrem=new THREE.PMREMGenerator(renderer);environmentTexture=pmrem.fromEquirectangular(skyTexture);scene.environment=environmentTexture.texture;scene.environmentIntensity=settings.environmentIntensity;
        camera=new THREE.PerspectiveCamera(32,1,.2,2400);camera.layers.enable(1);
        controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.07;controls.maxPolarAngle=Math.PI*.46;controls.minPolarAngle=.2;controls.autoRotateSpeed=.45;
        composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));
        const ao=settings.ambientOcclusion;aoPass=new GTAOPass(scene,camera,512,512,undefined,ao);aoPass.blendIntensity=ao.blendIntensity;// 遮蔽通道降低内部采样分辨率，建筑、车辆、标签与浮层仍保持主画面原始分辨率。
        const resizeAO=aoPass.setSize.bind(aoPass);aoPass.setSize=(w,h)=>resizeAO(Math.max(1,Math.round(w*.6)),Math.max(1,Math.round(h*.6)));composer.addPass(aoPass);composer.addPass(new OutputPass());composer.addPass(new SMAAPass());
        // 法线通道不支持透明叶簇的Alpha裁切；只排除装饰叶片，保留主画面及真实裁切阴影。
        const renderAo=aoPass.render.bind(aoPass);aoPass.render=(...args)=>{const mask=camera.layers.mask;camera.layers.disable(1);try{return renderAo(...args);}finally{camera.layers.mask=mask;}};
        const response=await fetch('./assets/build-info.json',{signal:loadingController.signal});if(!response.ok)throw new Error('模型清单读取失败');const info=await response.json();quality=info.quality;
        if(info.planningSha256!==props.config.planningSha256)throw new Error('模型与规划版本不一致，请重新构建');
        const assetResponse=await fetch('./assets/'+info.asset,{signal:loadingController.signal});if(!assetResponse.ok)throw new Error('模型文件读取失败');const bytes=await assetResponse.arrayBuffer();
        if(bytes.byteLength<12||new DataView(bytes).getUint32(0,true)!==0x46546c67)throw new Error('模型文件不是有效GLB');
        const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');if(digest!==info.assetSha256)throw new Error('模型内容与构建清单不一致');
        if(disposed)return;
        const gltf=await new GLTFLoader().parseAsync(bytes,'./assets/');if(disposed){disposeModel(gltf.scene);return;}
        model=gltf.scene;scene.add(model);renderer.shadowMap.needsUpdate=true;
        const baking={...props.config.production.bakedLighting,enabled:props.config.production.bakedLighting.enabled&&info.bakingComplete===true};
        let indirectMap;
        if(baking.enabled){
          indirectMap=await new THREE.TextureLoader().loadAsync('./assets/'+baking.indirectAsset);
          if(disposed){indirectMap.dispose();disposeModel(model);return;}
          indirectMap.flipY=false;indirectMap.colorSpace=THREE.NoColorSpace;indirectMap.channel=baking.uvChannel;
        }
        // 仅在载入后生成一次静态环境探针；玻璃反射真实周边几何，巡览不重复捕获。
        const cubeTarget=new THREE.WebGLCubeRenderTarget(128,{type:THREE.HalfFloatType}),probe=new THREE.CubeCamera(.5,1800,cubeTarget),focusGeometry=props.config.production.geometryById.A1;
        probe.position.set(...toThree([focusGeometry.position[0],focusGeometry.position[1]-focusGeometry.towerSize[1]/2-8,38]));
        const focusRoot=model.getObjectByName('building_A1');focusRoot.visible=false;renderer.shadowMap.enabled=false;probe.update(renderer,scene);renderer.shadowMap.enabled=true;focusRoot.visible=true;
        facadeEnvironment=pmrem.fromCubemap(cubeTarget.texture);cubeTarget.dispose();

        const originalWater=model.getObjectByName('landscape_water')?.material;
        const landscape=createCampusLandscape(model,scene,props.config.production.landscape);originalWater?.dispose();
        const revealMaterials=new Map();
        model.traverse(obj=>{
          if(obj.isMesh){
            let owner=obj;while(owner&&!owner.userData.objectId)owner=owner.parent;
            if(owner){const original=obj.material,key=owner.userData.objectId+':'+original.uuid;if(!revealMaterials.has(key)){const material=original.clone();material.onBeforeCompile=shader=>{shader.uniforms.campusDetailReveal=detailReveal;shader.fragmentShader='uniform float campusDetailReveal;\n'+shader.fragmentShader.replace('#include <color_fragment>','#include <color_fragment>\ndiffuseColor.rgb=mix(vec3(.72,.78,.75),diffuseColor.rgb,campusDetailReveal);');};material.customProgramCacheKey=()=> 'campus-entry-v22';revealMaterials.set(key,material);}obj.material=revealMaterials.get(key);}
            if(obj.userData.bakeReceiver){
              if(!obj.geometry.getAttribute('uv1')||!obj.material.aoMap)throw new Error('静态烘焙接收面缺少UV2或AO：'+obj.name);
              obj.material.aoMapIntensity=baking.aoStrength;obj.material.lightMap=indirectMap;obj.material.lightMapIntensity=baking.indirectStrength;
            }
            if(obj.name.startsWith('interior_v27_'))interiorMeshes.push(obj);
            if(obj.material.name.startsWith('glass')){if(obj.material.transmission)glassMaterials.set(obj.material,{transmission:obj.material.transmission,owner:owner?.userData.objectId});obj.material.envMap=facadeEnvironment.texture;obj.material.envMapIntensity=.9;}
            obj.castShadow=!obj.name.startsWith('environment_city')&&obj.name!=='landscape_water';obj.receiveShadow=true;
            // 小型设施与透明水景保留主画面和真实阴影，避开重复法线/AO通道。
            if(['landscape_wood','landscape_metal','landscape_skin','landscape_clothes','landscape_flower','landscape_water'].includes(obj.name))obj.layers.set(1);
            if(obj.material?.name?.startsWith('leavesCard')){const foliage=props.config.production.materialInputs.foliage;obj.layers.set(1);obj.material.alphaTest=foliage.alphaCutoff;obj.material.transparent=false;obj.material.depthWrite=true;obj.material.side=THREE.DoubleSide;obj.material.needsUpdate=true;}
          }
          if(obj.userData.objectId){if(roots.has(obj.userData.objectId))throw new Error('重复业务根节点');roots.set(obj.userData.objectId,obj);}
          if(obj.name.startsWith('anchor_'))anchors.set(obj.name.slice(7),obj);
        });
        const expected=pending.map(o=>o.id);if(expected.some(id=>!roots.has(id)||!anchors.has(id))||roots.size!==expected.length)throw new Error('模型对象与规划绑定不完整');
        // 三类几何分别实例化，使用同一时钟和路线；车漆颜色由固定车队序号派生。
        const traffic=props.config.production.traffic,routes=[createRoute(props.config.production.site,traffic,1),createRoute(props.config.production.site,traffic,-1)],fleet=[];
        const template=model.getObjectByName('traffic_vehicle_template');if(!template)throw new Error('缺少车辆模板');
        template.visible=false;model.updateMatrixWorld(true);
        let vehicleOffset=0;
        for(const type of traffic.fleet){
          const group=template.getObjectByName('traffic_'+type.type);if(!group)throw new Error('缺少车型 '+type.type);
          const indices=Array.from({length:type.count},(_,i)=>vehicleOffset+i);vehicleOffset+=type.count;
          group.traverse(obj=>{if(!obj.isMesh)return;const geometry=obj.geometry.clone();geometry.applyMatrix4(obj.matrixWorld);const mesh=new THREE.InstancedMesh(geometry,obj.material,type.count);mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);mesh.frustumCulled=false;mesh.castShadow=false;mesh.receiveShadow=true;
            if(obj.material.name==='car')indices.forEach((id,i)=>mesh.setColorAt(i,new THREE.Color(traffic.colors[id%traffic.colors.length])));
            scene.add(mesh);trafficMeshes.push(mesh);fleet.push({mesh,indices});
          });
        }
        if(vehicleOffset!==traffic.vehicleCount)throw new Error('车队数量与规划不一致');
        function updateTraffic(){
          host.value.dataset.landscape=JSON.stringify(landscape.update(trafficSeconds));
          const poses=Array.from({length:traffic.vehicleCount},(_,i)=>{const route=routes[i%2];return route.sample(Math.floor(i/2)*route.length/Math.ceil(traffic.vehicleCount/2)+trafficSeconds*traffic.speedMps);});
          for(const {mesh,indices} of fleet){indices.forEach((id,index)=>{const pose=poses[id];trafficDummy.position.set(...toThree(pose.position));trafficDummy.rotation.set(0,pose.heading,0);trafficDummy.updateMatrix();mesh.setMatrixAt(index,trafficDummy.matrix);});mesh.instanceMatrix.needsUpdate=true;}
          host.value.dataset.traffic=JSON.stringify({seconds:+trafficSeconds.toFixed(3),count:traffic.vehicleCount,types:traffic.fleet.map(t=>({type:t.type,count:t.count})),colors:traffic.colors,first:poses[0]});
        }
        // 轮廓只读同一制作规格，使用少量线框，避免整场景多次离屏渲染。
        for(const [id,root] of roots){
          const g=props.config.production.geometryById[id],group=new THREE.Group();
          const edge=(w,d,h,x,y,z)=>{const box=new THREE.BoxGeometry(w+.22,h+.22,d+.22);const geometry=new THREE.EdgesGeometry(box);box.dispose();const line=new THREE.LineSegments(geometry,new THREE.LineBasicMaterial({color:'#23858b',transparent:true,opacity:.55}));line.position.set(x,z,-y);line.userData.selectionDecoration=true;group.add(line);};
          if(g.podiumSizes){const fh=g.podiumFloorHeightM,th=g.towerFloorHeightM,f=props.config.demoDesign.focusBuilding.floorsDefinition;g.podiumSizes.forEach(([w,d],i)=>edge(w,d,fh,0,0,(i+.5)*fh));edge(...g.towerSize,f.towerAbovePodium*th,...g.towerOffset,f.podium*fh+f.towerAbovePodium*th/2);}
          else edge(...g.size,0,0,g.size[2]/2);
          root.add(group);highlights.set(id,group);
        }
        for(const item of pending){
          const button=document.createElement('button');button.type='button';button.className='building-label';button.textContent=item.id===props.config.demoDesign.focusBuilding.id?item.id+' '+props.config.demoDesign.focusBuilding.name:item.id;button.setAttribute('aria-label','选择楼宇 '+item.id);button.dataset.objectId=item.id;
          button.disabled=!props.active;button.tabIndex=props.active?0:-1;button.addEventListener('click',()=>choose(item.id));labelHost.value.append(button);labels.set(item.id,button);
        }
        renderer.domElement.addEventListener('pointerdown',pointerDown,true);renderer.domElement.addEventListener('pointerup',pointerUp);renderer.domElement.addEventListener('wheel',interruptEntry,{capture:true,passive:true});
        observer=new ResizeObserver(resize);observer.observe(host.value);window.addEventListener('resize',resize);document.addEventListener('visibilitychange',visibilityChanged);resize();setCamera(true);selectOutline();applyDetailQuality();window.addEventListener('keydown',closeCardOnEscape,true);progressStatus('');updateTraffic();renderer.shadowMap.needsUpdate=true;composer.render();
        emit('ready');
        function render(time){
          if(disposed)return;
          if(!props.active||document.visibilityState!=='visible'){lastTime=0;frame=requestAnimationFrame(render);return;}
          const visibleDelta=lastTime?Math.min((time-lastTime)/1000,traffic.maxStepSeconds):0;trafficSeconds+=visibleDelta;
          updateTraffic();
          if(lastTime){if(document.visibilityState==='visible')frameTimes.push(time-lastTime);if(frameTimes.length>600)frameTimes.shift();}lastTime=time;
          if(transition){let t=Math.min((time-transition.start)/transition.duration,1);t=t*t*(3-2*t);camera.position.lerpVectors(transition.eyeFrom,transition.eye,t);controls.target.lerpVectors(transition.targetFrom,transition.target,t);camera.fov=THREE.MathUtils.lerp(transition.fovFrom,transition.fov,t);camera.updateProjectionMatrix();if(t>=1)transition=null;}
          host.value.dataset.cameraSettled=String(!transition&&!entryFrame);
          controls.autoRotate=!!props.tour&&!entryFrame&&!transition&&!matchMedia('(prefers-reduced-motion: reduce)').matches;if(!entryFrame)controls.update();scene.updateMatrixWorld(true);
          for(const [id,node] of anchors){
            const label=labels.get(id),pos=node.getWorldPosition(new THREE.Vector3()).project(camera);
            const visible=(props.level==='campus'||id===props.selected)&&pos.z<1&&pos.x>-.98&&pos.x<.98&&pos.y>-.98&&pos.y<.97;

            const index=pending.findIndex(item=>item.id===id),reveal=entryFrame?entryFrame.labels[id==='A1'?0:index<4?1:2]:1;label.style.opacity=reveal;label.style.pointerEvents=entryFrame?'none':'';label.disabled=!!entryFrame||!props.active||reveal<.7;label.tabIndex=label.disabled?-1:0;label.hidden=!visible||reveal<.01;label.classList.toggle('selected',id===props.selected);label.style.transform=`translate(${(pos.x*.5+.5)*host.value.clientWidth}px,${(-pos.y*.5+.5)*host.value.clientHeight}px) translate(-50%,-100%)`;
          }
          entryAO=entryFrame?0:Math.min(1,entryAO+visibleDelta*5);aoPass.enabled=!baking.enabled&&!entryFrame;aoPass.blendIntensity=ao.blendIntensity*entryAO;placeCard(time);renderer.info.reset();composer.render();renderCount++;
          if(time-lastStats>1200){const sorted=[...frameTimes].sort((a,b)=>a-b);emit('stats',{quality,objects:[...roots.keys()],anchors:[...anchors.keys()],calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,modelTriangles:info.triangles,geometries:renderer.info.memory.geometries,textures:renderer.info.memory.textures,frameP95:sorted.length?+sorted[Math.floor((sorted.length-1)*.95)].toFixed(1):null,frames:renderCount,level:props.level,selection:props.selected,asset:info.asset,assetVersion:digest.slice(0,12)});lastStats=time;}
          frame=requestAnimationFrame(render);
        }
        frame=requestAnimationFrame(render);
      }catch(error){if(!disposed){console.error(error);progressStatus('三维场景加载失败，请检查资源后重试',true);}}
    });
    watch(()=>props.active,()=>{lastTime=0;resize();if(!props.active)cardOpen.value=false;});watch(()=>props.level,()=>{cardOpen.value=false;applyDetailQuality();setCamera();});watch(()=>props.resetTick,()=>setCamera());watch(()=>props.selected,selectOutline);
    onBeforeUnmount(()=>{
      disposed=true;window.removeEventListener('keydown',closeCardOnEscape,true);loadingController.abort();cancelAnimationFrame(frame);observer?.disconnect();window.removeEventListener('resize',resize);document.removeEventListener('visibilitychange',visibilityChanged);controls?.dispose();
      renderer?.domElement.removeEventListener('pointerdown',pointerDown,true);renderer?.domElement.removeEventListener('pointerup',pointerUp);renderer?.domElement.removeEventListener('wheel',interruptEntry,true);
      disposeModel(scene);skyTexture?.dispose();environmentTexture?.dispose();facadeEnvironment?.dispose();room?.dispose();pmrem?.dispose();aoPass?.dispose();composer?.passes.forEach(p=>{if(p!==aoPass)p.dispose();});composer?.dispose();renderer?.dispose();renderer?.forceContextLoss();renderer?.domElement.remove();labels.forEach(label=>label.remove());
    });
    return {number,area,occupancy,host,labelHost,status,failure,cardOpen,cardPosition,cardIdentity,modelHeight,reload:()=>window.location.reload()};
  },
  template:`<div ref="host" class="scene-view"><div ref="labelHost" class="labels"></div><svg v-if="cardOpen&&cardPosition?.owner===selected" class="card-tether" aria-hidden="true"><path :d="cardPosition.path"/></svg><aside v-if="cardOpen&&level==='campus'" class="building-info-card object-popover" role="dialog" aria-label="楼宇信息" :data-building-id="selected" :data-placement="cardPosition?.side" :data-obstruction="cardPosition?.obstruction" :style="{left:(cardPosition?.left??0)+'px',top:(cardPosition?.top??0)+'px',visibility:cardPosition?.owner===selected?'visible':'hidden'}"><header class="popover-head"><div class="popover-symbol"><Icon name="building"/></div><div class="popover-heading"><p class="card-eyebrow">楼宇档案</p><h2><b>{{selected}}</b><span>{{cardIdentity?.role}}</span></h2></div><button class="card-close" @click="cardOpen=false" aria-label="关闭楼宇信息"><Icon name="close"/></button></header><div class="popover-body"><div class="popover-feature"><p>建筑面积</p><strong>{{area(buildingData.grossAreaM2)}}<small v-if="buildingData.grossAreaM2!==null">万㎡</small></strong></div><dl class="popover-metrics"><div><dt>出租率</dt><dd>{{number(occupancy(buildingData))}}<small v-if="buildingData.rentableAreaM2!==null">%</small></dd></div><div><dt>入驻企业</dt><dd>{{number(buildingData.enterprises)}}<small v-if="buildingData.enterprises!==null">家</small></dd></div></dl></div><footer class="popover-footer"><span class="quality-dot">{{mode==='no-data'?'暂无经营数据':'演示数据'}}</span><span>模型高度 {{modelHeight}} m</span></footer></aside><div v-if="status" :class="['scene-status',{error:failure}]" role="status">{{status}}<button v-if="failure" @click="reload">重新载入</button></div></div>`
};
