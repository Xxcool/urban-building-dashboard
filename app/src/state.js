// 统一演示快照与数值格式；缺失使用null，场景和面板消费同一选择与模式。
export function snapshot(config, mode) {
  const blank = source => Object.fromEntries(Object.entries(source).map(([k,v])=>[k,typeof v==='number'?null:v]));
  const source={...config.demoDesign.buildingMetrics,[config.demoDesign.focusBuilding.id]:config.demoDesign.focusBuilding};
  const byBuilding=Object.fromEntries(Object.entries(source).map(([id,item])=>[id,mode==='no-data'?blank(item):item]));
  const campus={buildings:Object.keys(source).length,...Object.fromEntries(['grossAreaM2','rentableAreaM2','rentedAreaM2','enterprises'].map(key=>[key,Object.values(source).reduce((sum,item)=>sum+item[key],0)]))};
  const industryComposition=config.demoDesign.industryComposition.items.map(item=>({...item,enterprises:mode==='no-data'?null:item.enterprises,share:mode==='no-data'?null:Math.round(item.enterprises/campus.enterprises*100)}));
  return {industryComposition,campus:mode==='no-data'?blank(campus):campus,building:byBuilding[config.demoDesign.focusBuilding.id],byBuilding,quality:mode==='no-data'?'missing':'demo'};
}
export function number(value, decimals=0) {
  return value===null || value===undefined || !Number.isFinite(value) ? '—' : value.toLocaleString('zh-CN',{minimumFractionDigits:decimals,maximumFractionDigits:decimals});
}
export function area(value, precision=1, trim=true) { const formatted=value===null||value===undefined?'—':number(value/10000,precision);return trim?formatted.replace(/\.0$/,''):formatted; }
export function occupancy(source) { return source.rentedAreaM2===null || source.rentableAreaM2===null || source.rentableAreaM2<=0?null:source.rentedAreaM2/source.rentableAreaM2*100; }
export function vacant(source) { return source.rentedAreaM2===null||source.rentableAreaM2===null?null:source.rentableAreaM2-source.rentedAreaM2; }
export const toThree = v => [v[0],v[2],-v[1]];
