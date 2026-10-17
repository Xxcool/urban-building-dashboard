// 区域、园区和楼宇三层布局与交互，全部经营数值来自同一快照，不在组件中维护第二份统计值。
import {ref,computed,onMounted,onBeforeUnmount,defineAsyncComponent,nextTick,watch} from 'vue';
import {campusEntryFrame,campusEntryCameras,advanceEntryClock,entryGateSeconds} from './campus-entry.js';
import SceneView from './SceneView.js';
const CityView=defineAsyncComponent(()=>import('./CityView.js'));import Icon from './Icon.js';
import {snapshot,number,area,occupancy,vacant} from './state.js';
export default {
  components:{SceneView,CityView,Icon},props:['config'],
  setup(props){
    const focusBuilding=props.config.demoDesign.focusBuilding;
    const level=ref(props.config.design.interactions.initialLevel),selected=ref(props.config.design.interactions.initialSelection),mode=ref('demo'),resetTick=ref(0),tour=ref(false),menu=ref(false),diagnostics=ref(false),stats=ref(null),sceneStatus=ref({}),isFullscreen=ref(false),presentationNotice=ref('');
    const visitedCampus=ref(false),sceneLevel=ref('campus'),replayTick=ref(0),entrance=ref({done:false}),dashboard=ref(null);
    // 连续进度直接更新两项展示变量，避免每帧让整屏Vue树重新渲染；完成状态仍由统一时间线决定。
    const handleEntrance=frame=>{if(dashboard.value){dashboard.value.style.setProperty('--intro-panel',frame.panel);dashboard.value.style.setProperty('--intro-offset',(1-frame.panel)*12+'px');}if(entrance.value.done!==frame.done)entrance.value={done:frame.done};};
    const cityView=ref(null),campusView=ref(null),journey=ref(null),campusReady=ref(false),campusAttempt=ref(0),entryError=ref('');
    const entrySpec=props.config.production.campusEntry,reduced=matchMedia('(prefers-reduced-motion: reduce)');
    let run=null,entryFrameId=0,entryLast=0,campusFailed=false,hasEntered=false;
    const cityActive=computed(()=>level.value==='city'||journey.value?.phase==='handoff');
    const campusActive=computed(()=>level.value!=='city');
    const entryText=computed(()=>({locate:'正在进入光谷示范园区',approach:'前往示范园区',waiting:'正在准备园区视图',handoff:'进入园区',settle:'园区空间展开',reveal:'园区总览'})[journey.value?.phase]??'');
    function commitLevel(next){level.value=next;tour.value=false;if(next!=='city'){visitedCampus.value=true;sceneLevel.value=next;}if(next==='building')selected.value=focusBuilding.id;}
    function clearEntry(){
      cancelAnimationFrame(entryFrameId);entryLast=0;run=null;cityView.value?.finishCampusEntry({restore:level.value!=='city'});campusView.value?.finishCampusEntry();journey.value=null;
    }
    function interruptEntry(){if(!run)return;if(level.value==='campus')hasEntered=true;clearEntry();}
    function failEntry(){if(!run)return;commitLevel('city');clearEntry();entryError.value='园区资源暂未准备好，请重试进入。';}
    function sceneStatusChanged(s){if(level.value!=='city')sceneStatus.value=s;if(s.error){campusFailed=true;campusReady.value=false;failEntry();}}
    function showLevel(next){
      entryError.value='';if(run){if(next==='campus')return;clearEntry();commitLevel(next);return;}
      if(next==='campus'&&level.value==='city'){beginEntry();return;}commitLevel(next);
    }
    async function beginEntry(){
      if(run)return;entryError.value='';tour.value=false;menu.value=false;selected.value=focusBuilding.id;
      if(campusFailed){campusAttempt.value++;campusReady.value=false;campusFailed=false;}
      if(dashboard.value){const style=dashboard.value.style;const nav=dashboard.value.querySelector('.layer-tabs');style.setProperty('--entry-nav-offset',-(canvasSize.value.height-(nav?.offsetHeight??70)-58)+'px');style.setProperty('--entry-city',1);style.setProperty('--entry-campus',0);style.setProperty('--entry-panel',0);style.setProperty('--entry-city-panel',1);for(let i=1;i<=4;i++)style.setProperty('--entry-kpi-'+i,0);}
      visitedCampus.value=true;sceneLevel.value='campus';journey.value={phase:'locate'};
      run={seconds:0,start:null,options:{repeat:hasEntered,reduced:reduced.matches}};entryLast=0;await nextTick();
      function tick(now){
        if(!run)return;entryFrameId=requestAnimationFrame(tick);
        if(document.visibilityState!=='visible'){entryLast=0;return;}
        const delta=entryLast?(now-entryLast)/1000:0;entryLast=now;
        if(!run.start){run.start=cityView.value?.beginCampusEntry();if(!run.start)return;}
        run.seconds=advanceEntryClock(run.seconds,delta,campusReady.value,entrySpec,run.options);
        const frame=campusEntryFrame(run.seconds,entrySpec,run.options);
        if(!campusReady.value){frame.handoff=false;frame.campusOpacity=0;frame.cityOpacity=1;if(run.seconds>=entryGateSeconds(entrySpec,run.options))frame.phase='waiting';}
        const cameras=campusEntryCameras(run.start,props.config.production,frame,run.options);
        if(frame.handoff&&level.value==='city')commitLevel('campus');
        if(journey.value?.phase!==frame.phase)journey.value={phase:frame.phase};
        cityView.value?.applyCampusEntry(cameras.city,frame);
        if(campusReady.value&&frame.handoff)campusView.value?.applyCampusEntry(cameras.campus,frame);
        if(dashboard.value){const style=dashboard.value.style;style.setProperty('--entry-city',frame.cityOpacity);style.setProperty('--entry-campus',frame.campusOpacity);const nav=dashboard.value.querySelector('.layer-tabs');style.setProperty('--entry-nav-offset',-(canvasSize.value.height-(nav?.offsetHeight??70)-58)*(1-frame.settle)+'px');style.setProperty('--entry-panel',frame.panel);style.setProperty('--entry-city-panel',frame.cityPanel);frame.kpis.forEach((v,i)=>style.setProperty('--entry-kpi-'+(i+1),v));dashboard.value.dataset.campusEntry=JSON.stringify({seconds:+run.seconds.toFixed(3),phase:frame.phase,ready:campusReady.value,repeat:run.options.repeat,reduced:run.options.reduced,campusOpacity:frame.campusOpacity,panel:frame.panel,labels:frame.labels,cityCamera:cameras.city,campusCamera:cameras.campus});}
        if(frame.done&&campusReady.value){hasEntered=true;clearEntry();}
      }
      entryFrameId=requestAnimationFrame(tick);
    }
    function replayCity(){if(run)clearEntry();commitLevel('city');replayTick.value++;tour.value=false;menu.value=false;}
    const entryVisibility=()=>{entryLast=0;};
    const reduceEntry=()=>{if(run&&reduced.matches){run.options.reduced=true;run.seconds=entrySpec.reducedDuration;}};
    watch(tour,value=>{if(value&&run)interruptEntry();});
    const data=computed(()=>snapshot(props.config,mode.value));const values=computed(()=>data.value[level.value==='campus'?'campus':'building']);
    const metrics=computed(()=>[
      {label:level.value==='campus'?'楼宇总数':'楼层数',value:number(level.value==='campus'?values.value.buildings:values.value.floors),unit:level.value==='campus'?'栋':'层',icon:'building'},
      {label:'建筑面积',value:area(values.value.grossAreaM2),unit:'万㎡',icon:'area'},
      {label:'出租率',value:number(occupancy(values.value)),unit:'%',icon:'rate'},
      {label:'入驻企业',value:number(values.value.enterprises),unit:'家',icon:'people'}
    ]);
    const selectedData=computed(()=>data.value.byBuilding[selected.value]);
    const currentIdentity=computed(()=>props.config.demoDesign.buildingIdentities.find(o=>o.id===selected.value));
    const focus=()=>showLevel('building');
    const back=()=>{if(run)return;selected.value=focusBuilding.id;showLevel('campus');};const region=()=>showLevel('city');
    const formatArea=area,formatNumber=number;
    const formatAreaFixed=value=>area(value,props.config.demoDesign.contentDefinitions.spaceUsage.precision,false);
    // 设计尺寸只控制 UI 的等比缩放；逻辑画布扩展到窗口边缘，宽屏余量交给三维场景。
    const baseViewport=props.config.project.viewport;
    const viewport=ref({width:innerWidth,height:innerHeight});
    const scale=computed(()=>Math.min(viewport.value.width/baseViewport.width,viewport.value.height/baseViewport.height));
    const canvasSize=computed(()=>({width:viewport.value.width/scale.value,height:viewport.value.height/scale.value}));
    const railWidth=baseViewport.width*props.config.design.layout.railFraction;
    const sceneStyle=computed(()=>({left:railWidth+'px',width:(canvasSize.value.width-railWidth)+'px'}));
    const screenStyle=computed(()=>({width:canvasSize.value.width+'px',height:canvasSize.value.height+'px',transform:`translate(-50%,-50%) scale(${scale.value})`,...Object.fromEntries(Object.entries(props.config.design.palette).map(([k,v])=>['--'+k,v])),'--title-size':props.config.design.typography.titlePx+'px','--metric-size':props.config.design.typography.metricPx+'px','--body-size':props.config.design.typography.bodyPx+'px','--rail-padding':props.config.design.layout.paddingPx+'px','--rail-width':railWidth+'px'}));
    const resize=()=>viewport.value={width:innerWidth,height:innerHeight};
    const key=e=>{if(e.key==='Escape'){if(menu.value)menu.value=false;else if(level.value==='building')back();else region();}if(e.key==='Home')resetTick.value++;};
    const fullscreenChanged=()=>{isFullscreen.value=!!document.fullscreenElement;resize();};
    async function fullscreen(){
      presentationNotice.value='';
      try{if(!document.fullscreenElement){if(!document.documentElement.requestFullscreen)throw new Error('Fullscreen unavailable');await document.documentElement.requestFullscreen();}else await document.exitFullscreen();fullscreenChanged();menu.value=false;}
      catch{presentationNotice.value='当前窗口不支持全屏，可在独立浏览器打开后使用。';}
    }
    onMounted(()=>{document.addEventListener('visibilitychange',entryVisibility);reduced.addEventListener('change',reduceEntry);resize();window.addEventListener('resize',resize);window.addEventListener('keydown',key);document.addEventListener('fullscreenchange',fullscreenChanged);});
    onBeforeUnmount(()=>{cancelAnimationFrame(entryFrameId);document.removeEventListener('visibilitychange',entryVisibility);reduced.removeEventListener('change',reduceEntry);window.removeEventListener('resize',resize);window.removeEventListener('keydown',key);document.removeEventListener('fullscreenchange',fullscreenChanged);});
    return {cityView,campusView,journey,cityActive,campusActive,campusReady,campusAttempt,entryText,entryError,beginEntry,replayCity,interruptEntry,sceneStatusChanged,dashboard,handleEntrance,selectedData,replayTick,entrance,visitedCampus,sceneLevel,region,showLevel,level,selected,mode,resetTick,tour,menu,diagnostics,stats,sceneStatus,metrics,data,currentIdentity,focusBuilding,focus,back,formatArea,formatAreaFixed,formatNumber,occupancy,vacant,sceneStyle,screenStyle,fullscreen,isFullscreen,presentationNotice};
  },
  template:`<main ref="dashboard" class="dashboard" :class="['level-'+level,{'no-data':mode==='no-data','entering-campus':!!journey}]" :style="screenStyle" :data-level="level" :data-mode="mode" :data-selection="selected" :data-entrance-complete="entrance.done" :data-campus-entry-active="!!journey">
    <CityView ref="cityView" @interrupt="interruptEntry" :data="data" :replay-tick="replayTick" @entrance="handleEntrance" v-show="level==='city'||!!journey" :config="config" :active="cityActive" :reset-tick="resetTick" :tour="tour" :style="sceneStyle" @enter="back" @stats="s=>{if(level==='city')stats=s}" @status="s=>{if(level==='city')sceneStatus=s}"/>
    <SceneView ref="campusView" :key="campusAttempt" @ready="campusReady=true" @interrupt="interruptEntry" v-if="visitedCampus" v-show="level!=='city'||!!journey" :active="campusActive" :config="config" :level="sceneLevel" :selected="selected" :building-data="selectedData" :mode="mode" :reset-tick="resetTick" :tour="tour" :style="[sceneStyle,{pointerEvents:journey&&level==='city'?'none':''}]" @select="selected=$event" @focus="focus" @stats="s=>{if(level!=='city')stats=s}" @status="sceneStatusChanged"/>
    <aside class="rail" :inert="!!journey" :style="{width:'var(--rail-width)'}">
      <header class="brand-header"><h1>{{config.project.title}}</h1><div class="brand-line"><span>武汉 · 光谷</span><span class="badge">{{level==='city'?'区域概念':'示范园区'}} · {{mode==='demo'?'演示数据':'暂无数据'}}</span></div>
      <div v-if="level==='city'" class="city-caption"><h2>区域总览</h2><p>{{config.demoDesign.region.name}}</p></div><div v-else-if="level==='campus'" class="level-caption">产业空间 · 园区总览</div><nav v-else class="breadcrumb"><button @click="back">园区总览</button><span>/</span><strong>重点楼宇</strong></nav></header>
      <div v-if="level==='building'" class="focus-title"><span>{{focusBuilding.id}}</span><h2>{{focusBuilding.name}}</h2></div>
      <section v-if="level!=='city'" class="kpis" aria-label="关键指标"><article v-for="m in metrics" :key="m.label" class="kpi"><Icon :name="m.icon"/><div><div class="metric-value"><strong>{{m.value}}</strong><span v-if="m.value!=='—'">{{m.unit}}</span></div><p>{{m.label}}</p></div></article></section>
      <template v-if="level==='city'">
        <section class="industry-section"><h3>产业方向</h3><div class="category-grid"><div v-for="(text,i) in config.demoDesign.contentDefinitions.industryDirections.labels" :key="text"><Icon :name="['code','chip','briefcase'][i]"/><span>{{text}}</span></div></div></section>
        <section class="city-park-section"><h3>重点园区</h3><div class="resource-card"><button class="resource-heading" @click="back"><span>{{config.demoDesign.region.campusName}}</span><span>›</span></button><div class="city-metrics"><article v-for="(m,i) in [{label:'楼宇数',value:formatNumber(data.campus.buildings),unit:'栋',icon:'building'},{label:'建筑面积',value:formatArea(data.campus.grossAreaM2),unit:'万㎡',icon:'area'},{label:'出租率',value:formatNumber(occupancy(data.campus)),unit:'%',icon:'rate'},{label:'入驻企业',value:formatNumber(data.campus.enterprises),unit:'家',icon:'people'}]" :key="m.label"><Icon :name="m.icon"/><div><strong>{{m.value}}</strong><small v-if="m.value!=='—'">{{m.unit}}</small><p>{{m.label}}</p></div></article></div><p v-if="mode==='no-data'" class="city-empty-note">暂无园区经营数据</p><button class="city-enter" @click="back">进入园区 <span>›</span></button></div></section>
      </template>
      <template v-else-if="level==='campus'">
        <section class="industry-section"><h3>产业方向</h3><p class="section-caption">示范产业定位</p><div class="category-grid"><div v-for="(text,i) in config.demoDesign.contentDefinitions.industryDirections.labels" :key="text"><Icon :name="['code','chip','briefcase'][i]"/><span>{{text}}</span></div></div></section>
        <section class="resource-card" :data-building-id="selected"><button class="resource-heading" :disabled="selected!==focusBuilding.id" @click="selected===focusBuilding.id&&focus()"><span>{{selected}} {{selected===focusBuilding.id?focusBuilding.name:currentIdentity?.role}}</span><span v-if="selected===focusBuilding.id" aria-hidden="true">›</span><small v-else>已选楼宇</small></button>
          <div class="resource-values"><p><b>{{formatNumber(selectedData.floors)}}</b> 层 · <b>{{formatArea(selectedData.grossAreaM2)}}</b> 万㎡</p><p>出租率 <b>{{formatNumber(occupancy(selectedData))}}</b><span v-if="mode==='demo'">%</span> · 入驻企业 <b>{{formatNumber(selectedData.enterprises)}}</b> 家</p></div>
        </section>
      </template>
      <template v-else>
        <section class="space-section"><h3>空间利用</h3><dl><div><dt>出租率</dt><dd>{{formatNumber(occupancy(data.building))}}<span v-if="mode==='demo'">%</span></dd></div><div><dt>已租面积</dt><dd>{{formatAreaFixed(data.building.rentedAreaM2)}} <small>万㎡</small></dd></div><div><dt>可租面积</dt><dd>{{formatAreaFixed(data.building.rentableAreaM2)}} <small>万㎡</small></dd></div><div><dt>可租空置面积</dt><dd>{{formatAreaFixed(vacant(data.building))}} <small>万㎡</small></dd></div></dl></section>
        <section class="building-industry"><h3>入驻产业</h3><div v-if="mode==='demo'" class="category-grid compact"><div v-for="(text,i) in config.demoDesign.contentDefinitions.buildingIndustries.labels" :key="text"><Icon :name="['code','chip','briefcase'][i]"/><span>{{text}}</span></div></div><p v-else class="empty-state">暂无产业数据</p></section>
        <section class="services"><h3>配套服务</h3><div class="category-grid compact"><div v-for="(text,i) in config.demoDesign.contentDefinitions.services.labels" :key="text"><Icon :name="['meeting','parking','bus'][i]"/><span>{{text}}</span></div></div></section>
        <button class="back-button" @click="back"><Icon name="back"/>返回园区</button>
      </template>
    </aside>
    <nav class="layer-tabs" aria-label="展示层级"><button :class="{active:level==='city'}" @click="region">区域总览</button><button :class="{active:level==='campus'}" @click="back">园区总览</button><button :class="{active:level==='building'}" @click="focus">重点楼宇</button></nav>
    <div v-if="journey" class="entry-caption" role="status"><span></span>{{entryText}}</div><div v-if="entryError" class="entry-error" role="status"><p>{{entryError}}</p><button @click="beginEntry">重试进入园区</button><button @click="entryError=''" aria-label="关闭进入提示">×</button></div>
    <div class="scene-actions"><button @click="interruptEntry();resetTick++;tour=false" aria-label="复位视角" title="复位视角"><Icon name="reset"/></button><button @click="menu=!menu" :aria-expanded="menu" aria-label="展示设置" title="展示设置"><Icon name="settings"/></button></div>
    <section v-if="menu" class="settings-panel"><h3>展示设置</h3><p>当前为本地演示快照，未接入实时系统</p><div class="mode-switch"><button @click="mode='demo'" :class="{active:mode==='demo'}">演示数据</button><button @click="mode='no-data'" :class="{active:mode==='no-data'}">无数据状态</button></div><label><input type="checkbox" v-model="tour"> 自动巡览</label><button v-if="level==='city'" @click="replayCity">重播入场</button><button @click="fullscreen"><Icon name="expand"/> {{isFullscreen?'退出全屏':'全屏展示'}}</button><p v-if="presentationNotice" role="status">{{presentationNotice}}</p><button @click="diagnostics=!diagnostics">{{diagnostics?'隐藏':'显示'}}场景信息</button></section>
    <section v-if="diagnostics&&stats" class="diagnostics" aria-label="场景信息"><h3>场景信息</h3><p>资产：{{stats.asset}} · {{stats.quality}}</p><p>版本：{{stats.assetVersion}} · 模型三角形：{{stats.modelTriangles}}</p><p>对象：{{stats.objects.join(', ')}}</p><p>锚点：{{stats.anchors.length}} · draw calls：{{stats.calls}}</p><p>每帧提交三角形：{{stats.triangles}}</p><p>几何：{{stats.geometries}} · 纹理：{{stats.textures}}</p><p>帧间隔 P95：{{stats.frameP95}} ms · 已渲染 {{stats.frames}} 帧</p><p>层级：{{stats.level}} · 选择：{{stats.selection}}</p></section>
    <p v-if="level==='city'" class="city-disclaimer">{{config.demoDesign.region.disclaimer}}</p><div v-if="level==='city'" class="city-legend"><span>区域示意</span><span>示范园区</span></div>
    <p v-if="level!=='city'" class="gesture-hint">拖动旋转 · 滚轮缩放 · 点击楼宇选择</p>
  </main>`
};
