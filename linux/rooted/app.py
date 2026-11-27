"""Zero-dependency HTTP application. Run: python3 -m rooted.app."""
import argparse
import json
import mimetypes
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, unquote
import webbrowser
from .curriculum import BY_ID, public_curriculum
from .simulator import Terminal, canonical, initial_state
from .storage import Store
from .workbook import build_pack
from .concepts import calculate

ROOT=Path(__file__).resolve().parent

def lesson_action(store,lesson_id,body):
    if lesson_id not in BY_ID: raise ValueError('Unknown lesson')
    lesson=BY_ID[lesson_id]; action=body.get('action'); result={}
    with store.edit(lesson_id) as state:
        if action=='terminal':
            command=body.get('command')
            if not isinstance(command,str) or len(command)>4096: raise ValueError('Enter a command under 4096 characters')
            term=Terminal(state['lab']); result=term.run(command)
            # These are guided command checkpoints, not arbitrary-shell assessments.
            for i,task in enumerate(lesson['tasks']):
                if canonical(command)==canonical(task['command']) and result['status'] in (0,1) and i not in state['lab']['done']:
                    state['lab']['done'].append(i)
        elif action=='read': state['read']=True
        elif action=='bookmark': state['bookmark']=not state['bookmark']
        elif action=='note':
            note=body.get('notes','')
            if not isinstance(note,str) or len(note)>20000: raise ValueError('Notes must be text under 20,000 characters')
            state['notes']=note
        elif action=='reset_lab':
            state['lab']=initial_state()
            # Completed learning remains earned; a reset is a fresh practice attempt.
        elif action=='quiz':
            answers=body.get('answers')
            if not isinstance(answers,list) or len(answers)!=len(lesson['questions']) or any(type(x)!=int or not 0<=x<3 for x in answers): raise ValueError('Answer every question')
            review=[dict(correct=a==q['answer'],answer=q['answer'],explanation=q['explanation']) for a,q in zip(answers,lesson['questions'])]
            score=sum(r['correct'] for r in review)
            state['attempts']+=1; state['best_score']=max(state['best_score'],score)
            state['quiz_pass']=state['quiz_pass'] or score==len(review)
            state['last_answers']=answers
            result=dict(score=score,total=len(review),review=review,passed=score==len(review))
        elif action=='complete':
            if not state['read'] or not state['quiz_pass'] or len(state['lab']['done'])<len(lesson['tasks']): raise ValueError('Read the lesson, finish every guided task and pass the knowledge check first')
            state['completed']=True
        else: raise ValueError('Unknown action')
    return {'result':result,'state':state}

class Handler(BaseHTTPRequestHandler):
    server_version='Rooted/1.0'
    def log_message(self,format,*args):
        if self.server.verbose: super().log_message(format,*args)
    def send(self,value,status=200,kind='application/json; charset=utf-8'):
        data=json.dumps(value,ensure_ascii=False).encode() if kind.startswith('application/json') else value
        self.send_response(status)
        self.send_header('Content-Type',kind); self.send_header('Content-Length',str(len(data)))
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store')
        self.send_header('Referrer-Policy','same-origin')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        path=unquote(urlparse(self.path).path)
        if path=='/api/course': return self.send(public_curriculum())
        if path=='/api/progress': return self.send(self.server.store.all())
        if path=='/api/practice-pack': return self.send(build_pack(),kind='application/zip')
        if path=='/api/reference': return self.send(json.loads((ROOT/'reference.json').read_text()))
        if path=='/api/export': return self.send(dict(format='rooted-progress-v1',progress=self.server.store.all(full=True)))
        if path.startswith('/api/lesson/'):
            lid=path.removeprefix('/api/lesson/')
            return self.send(self.server.store.get(lid)) if lid in BY_ID else self.send({'error':'Unknown lesson'},404)
        if path.startswith('/api/'): return self.send({'error':'Not found'},404)
        name='index.html' if path=='/' else path.lstrip('/')
        file=(ROOT/'static'/name).resolve()
        if not file.is_relative_to(ROOT/'static') or not file.is_file(): return self.send({'error':'Not found'},404)
        return self.send(file.read_bytes(),kind=mimetypes.guess_type(file)[0] or 'application/octet-stream')
    def do_POST(self):
        # Custom header + JSON + no CORS defeats cross-origin form/fetch writes.
        if self.headers.get('X-Rooted-Client')!='1' or self.headers.get_content_type()!='application/json': return self.send({'error':'Use the local application interface'},403)
        origin=self.headers.get('Origin')
        if origin and urlparse(origin).netloc!=self.headers.get('Host'): return self.send({'error':'Cross-origin writes are not allowed'},403)
        path=unquote(urlparse(self.path).path)
        if not path.startswith('/api/lesson/') and path!='/api/tools': return self.send({'error':'Not found'},404)
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=30000: raise ValueError('Request too large or empty')
            body=json.loads(self.rfile.read(length))
            if not isinstance(body,dict): raise ValueError('Expected a JSON object')
            response=calculate(body) if path=='/api/tools' else lesson_action(self.server.store,path.removeprefix('/api/lesson/'),body)
            return self.send(response)
        except (ValueError,TypeError) as error: return self.send({'error':str(error)},400)

def create_server(host='127.0.0.1',port=8765,data_dir=None,verbose=False):
    data_dir=Path(data_dir) if data_dir else Path(os.environ.get('XDG_DATA_HOME',str(Path.home()/'.local/share')))/'rooted'
    server=ThreadingHTTPServer((host,port),Handler)
    server.store=Store(data_dir/'progress.sqlite3'); server.verbose=verbose
    return server

def main():
    parser=argparse.ArgumentParser(description='Rooted Linux learning app — Python 3.10+, no dependencies')
    parser.add_argument('--host',default='127.0.0.1',help='Default: local computer only. No authentication; do not expose publicly.')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--data-dir',type=Path)
    parser.add_argument('--open',action='store_true',help='Open the interface in your browser')
    parser.add_argument('--verbose',action='store_true')
    args=parser.parse_args()
    try: server=create_server(args.host,args.port,args.data_dir,args.verbose)
    except OSError as error: parser.exit(1,f'Cannot start Rooted: {error}. Try a different --port.\n')
    url=f'http://127.0.0.1:{server.server_port}'
    print(f'Rooted is running at {url}\nProgress: {server.store.path}\nPress Ctrl-C to stop.',flush=True)
    if args.open: webbrowser.open(url)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=='__main__': main()
