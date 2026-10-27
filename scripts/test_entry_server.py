"""仅供本地园区入场验证：实际HTTP延迟/首次失败，不改动模型或生产配置。"""
import argparse,time
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from threading import Lock
p=argparse.ArgumentParser();p.add_argument('--port',type=int,required=True);p.add_argument('--mode',choices=['delay','fail-first'],required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]/'dist';lock=Lock();seen=False
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)
 def do_GET(self):
  global seen
  if self.path.split('?')[0]=='/assets/campus.glb':
   with lock:first=not seen;seen=True
   if first:
    if a.mode=='fail-first':self.send_error(503,'Local verification: first campus request fails');return
    time.sleep(3)
  super().do_GET()
ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
