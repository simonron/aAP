#!/usr/bin/env python3
import json, os, tempfile
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

HOST=os.environ.get('AAP_HOST','0.0.0.0'); PORT=int(os.environ.get('AAP_PORT','8789'))
DATA=os.path.expanduser(os.environ.get('AAP_DATA','~/Library/Application Support/aAP/records.json'))
os.makedirs(os.path.dirname(DATA),exist_ok=True)

def read_data():
    try:
        with open(DATA,'r',encoding='utf-8') as f: return json.load(f)
    except (FileNotFoundError,json.JSONDecodeError): return []

def write_data(v):
    fd,tmp=tempfile.mkstemp(dir=os.path.dirname(DATA),prefix='aap-',suffix='.tmp')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(v,f,ensure_ascii=False,indent=2); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,DATA)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

class H(BaseHTTPRequestHandler):
    def send_json_headers(self,code=200):
        self.send_response(code); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Methods','GET,PUT,OPTIONS'); self.send_header('Access-Control-Allow-Headers','Content-Type'); self.send_header('Cache-Control','no-store'); self.end_headers()
    def do_OPTIONS(self): self.send_json_headers(204)
    def do_GET(self):
        if urlparse(self.path).path!='/api/records': self.send_json_headers(404); return
        self.send_json_headers(); self.wfile.write(json.dumps(read_data(),ensure_ascii=False).encode())
    def do_PUT(self):
        if urlparse(self.path).path!='/api/records': self.send_json_headers(404); return
        try:
            n=int(self.headers.get('Content-Length','0')); v=json.loads(self.rfile.read(n) or b'[]')
            if not isinstance(v,list): raise ValueError()
            write_data(v); self.send_json_headers(); self.wfile.write(b'{"ok":true}')
        except Exception:
            self.send_json_headers(400); self.wfile.write(b'{"ok":false}')
    def log_message(self,fmt,*args): print('%s - %s'%(self.address_string(),fmt%args))

print(f'aAP shared data server: http://{HOST}:{PORT}/api/records')
print(f'Data file: {DATA}')
ThreadingHTTPServer((HOST,PORT),H).serve_forever()
