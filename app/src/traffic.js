// 示范交通沿外围双向车道匀速循环；由道路规格派生路线，不参与经营统计。
export function createRoute(site,traffic,direction){
  const offset=direction===1?traffic.laneOffsetM:-traffic.laneOffsetM;
  const a=site.parkSize[0]/2+site.roadWidth/2+offset,b=site.parkSize[1]/2+site.roadWidth/2+offset,r=traffic.cornerRadiusM+offset;
  const segments=[],line=(x,y,dx,dy,length)=>segments.push({length,sample:d=>[x+dx*d,y+dy*d,Math.atan2(dy,dx)]});
  const arc=(x,y,start)=>segments.push({length:Math.PI*r/2,sample:d=>{const t=start+d/r;return [x+r*Math.cos(t),y+r*Math.sin(t),t+Math.PI/2];}});
  line(-a+r,-b,1,0,2*(a-r));arc(a-r,-b+r,-Math.PI/2);
  line(a,-b+r,0,1,2*(b-r));arc(a-r,b-r,0);
  line(a-r,b,-1,0,2*(a-r));arc(-a+r,b-r,Math.PI/2);
  line(-a,b-r,0,-1,2*(b-r));arc(-a+r,-b+r,Math.PI);
  const length=segments.reduce((sum,s)=>sum+s.length,0);
  return {length,sample(distance){let d=((distance*direction)%length+length)%length;for(const s of segments){if(d<=s.length){const [x,y,heading]=s.sample(d);return {position:[x,y,0],heading:heading+(direction===-1?Math.PI:0)};}d-=s.length;}}};
}
