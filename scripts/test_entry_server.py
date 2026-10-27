"""仅供本地加载与入场验证：真实HTTP延迟、分片限速和首次失败，不改动模型或生产配置。"""
import argparse,time
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from threading import Lock
p=argparse.ArgumentParser();p.add_argument('--port',type=int,required=True);p.add_argument('--mode',choices=['delay','stream','fail-first'],required=True);p.add_argument('--asset',choices=['campus','city'],default='campus');a=p.parse_args();root=Path(__file__).resolve().parents[1]/'dist';lock=Lock();seen=False
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)
 def do_GET(self):
  global seen
  if self.path.split('?')[0]=='/assets/'+a.asset+'.glb':
   with lock:first=not seen;seen=True
   if first:
    if a.mode=='fail-first':self.send_error(503,'Local verification: first model request fails');return
    if a.mode=='stream':
     # 通过真实响应分片制造可观察的下载过程，供进度与README截图验证。
     data=(root/'assets'/(a.asset+'.glb')).read_bytes();self.send_response(200);self.send_header('Content-Type','model/gltf-binary');self.send_header('Content-Length',str(len(data)));self.end_headers()
     for offset in range(0,len(data),512*1024):
      try:self.wfile.write(data[offset:offset+512*1024]);self.wfile.flush()
      except (BrokenPipeError,ConnectionResetError):return
      time.sleep(.3)
     return
    time.sleep(3)
  super().do_GET()
ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
