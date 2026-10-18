"""通过真实 stdio MCP 协议调用本机 Blender MCP，保留结构化调用证据。"""
import argparse,asyncio,hashlib,json,os,shutil
from datetime import datetime,timezone,timedelta
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--tool',default='get_scene_info')
 parser.add_argument('--arguments',type=Path)
 parser.add_argument('--report',type=Path,required=True)
 args=parser.parse_args()
 env={**os.environ,'BLENDER_HOST':'127.0.0.1','BLENDER_PORT':'9876','DISABLE_TELEMETRY':'1'}
 params=StdioServerParameters(command=shutil.which('uvx')or str(Path.home()/'.local/bin/uvx'),args=['--offline','blender-mcp'],env=env)
 async with stdio_client(params) as (read,write):
  async with ClientSession(read,write) as session:
   init=await session.initialize()
   available=await session.list_tools()
   if args.tool=='list_tools':result={'tools':[t.model_dump(mode='json') for t in available.tools]}
   else:
    inputs=json.loads(args.arguments.read_text()) if args.arguments else {}
    if 'code' in inputs:inputs['code']=inputs['code'].replace('__PROJECT_ROOT__',str(Path(__file__).resolve().parents[1]))
    result=(await session.call_tool(args.tool,inputs,read_timeout_seconds=timedelta(seconds=600))).model_dump(mode='json')
   report={'transport':'MCP stdio → Blender MCP → Blender addon','server':init.serverInfo.model_dump(mode='json'),'tool':args.tool,'executedCodeSha256':hashlib.sha256(inputs['code'].encode()).hexdigest() if args.tool!='list_tools' and 'code' in inputs else None,'argumentsSha256':hashlib.sha256(args.arguments.read_bytes()).hexdigest() if args.arguments else None,'at':datetime.now(timezone.utc).isoformat(),'result':result}
   args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
   print(json.dumps(report,ensure_ascii=False)[:2500])
   if result.get('isError') or any(c.get('type')=='text' and c.get('text','').startswith(('Error executing code:','Rejected by safe mode')) for c in result.get('content',[])):
    raise RuntimeError('MCP工具返回失败，详见结构化报告；不得据进程退出码误报成功')
if __name__=='__main__':asyncio.run(main())
